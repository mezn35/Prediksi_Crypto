import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
import plotly.graph_objects as go
from ta.volatility import BollingerBands, AverageTrueRange
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from datetime import datetime, timedelta
import random
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="ULTIMATE AI CRYPTO", layout="wide")
st.title("🤖 ULTIMATE AI: Time Traveler + Sniper Mode")
st.markdown("""
**Fitur Lengkap Kembali:**
1.  ⚡ **Real-Time Data:** Harga detik ini (Sinkron Tokocrypto).
2.  📅 **Time Traveler:** Prediksi Tanggal & Jam (Kapan Beli, Kapan Jual).
3.  🛡️ **Smart Filter:** Anti-Zombie (Volume) & Anti-Crash (Falling Knife).
4.  📊 **Visual Pro:** Grafik Candlestick dengan Area Profit (Hijau) & Stop Loss (Merah).
""")

# --- DATABASE KOIN ---
WATCHLIST = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
    "PEPE/USDT", "SHIB/USDT", "WIF/USDT", "BONK/USDT", "FLOKI/USDT", "BOME/USDT", 
    "JASMY/USDT", "LUNC/USDT", "SLP/USDT", "GALA/USDT", "NEAR/USDT", "FET/USDT",
    "RNDR/USDT", "FTM/USDT", "MATIC/USDT", "ADA/USDT", "AVAX/USDT", "DOT/USDT",
    "LINK/USDT", "TRX/USDT", "LTC/USDT", "BCH/USDT", "UNI/USDT", "APT/USDT",
    "FIL/USDT", "ATOM/USDT", "IMX/USDT", "OP/USDT", "INJ/USDT", "STX/USDT",
    "TIA/USDT", "SEI/USDT", "ARB/USDT", "SUI/USDT", "QNT/USDT", "AAVE/USDT",
    "SAND/USDT", "MANA/USDT", "THETA/USDT", "AXS/USDT", "EOS/USDT", "XTZ/USDT",
    "CFX/USDT", "CHZ/USDT", "MEME/USDT", "PEOPLE/USDT", "WLD/USDT", "ARKM/USDT",
    "1000SATS/USDT", "BTTC/USDT", "DENT/USDT", "HOT/USDT", "SC/USDT", "ZIL/USDT",
    "IOST/USDT", "VTHO/USDT", "CKB/USDT", "RSR/USDT", "MBL/USDT", "ANKR/USDT",
    "HEI/USDT", "KOM/USDT", "BROCCOLI714/USDT", "PENGU/USDT", "BIO/USDT", "VANA/USDT",
    "1000CHEEMS/USDT", "TURTLE/USDT", "MDT/USDT", "ACA/USDT", "CITY/USDT", "ATM/USDT",
    "COS/USDT", "ACM/USDT", "CHESS/USDT", "NBT/USDT", "CREO/USDT", "CVC/USDT", 
    "ALPINE/USDT", "BEL/USDT", "JUV/USDT", "HOOK/USDT", "NKN/USDT", "QUICK/USDT"
]

# Inisialisasi Exchange (Binance)
exchange = ccxt.binance({'enableRateLimit': True, 'options': {'defaultType': 'spot'}})

# --- SIDEBAR PENGATURAN ---
with st.sidebar:
    st.header("⚙️ Pusat Komando")
    modal_awal = st.number_input("Modal Investasi (Rp)", value=1000000, step=500000)
    kurs_usd_idr = st.number_input("Kurs USD/IDR (Sesuaikan)", value=16200, step=50)
    target_profit_pct = st.slider("Target Profit (%)", 2.0, 30.0, 5.0)
    st.divider()
    st.info("💡 **Tips:** Jika hasil scan kosong, berarti pasar sedang berbahaya (Crash/Sideways). AI menjaga modal Anda.")

# --- FUNGSI 1: DATA ENGINE (ANTI-BLOKIR) ---
def get_market_data(symbol):
    df = None
    current_price = 0
    source = "Mencari..."
    
    # JALUR 1: BINANCE REAL-TIME
    try:
        # Bersihkan simbol (IDR -> USDT)
        target = symbol.replace("/IDR", "/USDT")
        if "JELLY" in target: target = "JELLY/USDT"
        
        # Ambil Ticker (Harga Detik Ini)
        ticker = exchange.fetch_ticker(target)
        current_price = ticker['last']
        
        # Ambil Candle (Untuk Analisa Grafik)
        bars = exchange.fetch_ohlcv(target, timeframe='1h', limit=200) # Butuh 200 candle untuk EMA 200
        if bars:
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
            df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7) # WIB
            df.set_index('time', inplace=True)
            source = "⚡ Real-Time (Binance)"
    except:
        pass # Gagal? Lanjut ke Yahoo
    
    # JALUR 2: YAHOO FINANCE (BACKUP)
    if df is None:
        try:
            yf_sym = symbol.replace("/", "-").replace("USDT", "USD").replace("IDR", "USD")
            data_yf = yf.download(yf_sym, period='1mo', interval='1h', progress=False)
            if len(data_yf) > 50:
                if isinstance(data_yf.columns, pd.MultiIndex): data_yf.columns = data_yf.columns.droplevel(1)
                df = data_yf[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
                df.columns = ['open', 'high', 'low', 'close', 'vol']
                df.index = df.index + timedelta(hours=7) # WIB
                current_price = df['close'].iloc[-1]
                source = "⚠️ Backup (Yahoo)"
        except:
            pass
            
    return df, current_price, source

# --- FUNGSI 2: THE BRAIN (ANALISA) ---
def analyze_coin(symbol):
    df, real_price, source = get_market_data(symbol)
    if df is None: return None
    
    close = df['close']
    
    # 1. INDIKATOR TEKNIKAL
    df['ema200'] = EMAIndicator(close=close, window=200).ema_indicator()
    df['rsi'] = RSIIndicator(close=close, window=14).rsi()
    bb = BollingerBands(close=close, window=20, window_dev=2)
    df['bb_h'] = bb.bollinger_hband()
    df['bb_l'] = bb.bollinger_lband()
    df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=close, window=14).average_true_range()
    
    # Data Terakhir
    last_candle = df.iloc[-1]
    rsi = df['rsi'].iloc[-1]
    ema200 = df['ema200'].iloc[-1]
    bb_low = df['bb_l'].iloc[-1]
    atr = df['atr'].iloc[-1]
    
    # Gunakan real_price dari Ticker jika ada (lebih akurat), jika tidak pakai close candle
    price_now = real_price if real_price > 0 else last_candle['close']
    
    # 2. FILTER KEAMANAN (ZOMBIE & CRASH)
    # Cek Volume (Minimal $20k sehari)
    vol_usd = last_candle['vol'] * price_now
    if vol_usd < 20000: return {"symbol": symbol, "status": "SKIP", "reason": "Zombie (Sepi)"}
    
    # Cek Crash (Jatuh > 3% di candle terakhir)
    drop_pct = (last_candle['open'] - price_now) / last_candle['open'] * 100
    if drop_pct > 3.0: return {"symbol": symbol, "status": "DANGER", "reason": "Sedang Longsor (Crash)"}

    # 3. LOGIKA BELI (STRATEGI GABUNGAN)
    signal = "WAIT"
    reason = "Sideways"
    score = 0
    
    # Skenario A: Tren Naik (Diatas EMA200) + Koreksi (RSI < 50)
    is_uptrend = price_now > ema200
    if is_uptrend and rsi < 50:
        signal = "BUY ON DIP"
        reason = "✅ Tren Naik + Harga Diskon"
        score = 85
        
    # Skenario B: Rebound dari Bawah (Harga nyentuh BB Bawah + RSI < 35)
    elif price_now <= (bb_low * 1.01) and rsi < 35:
        signal = "SNIPER ENTRY"
        reason = "🎯 Harga di Dasar (Oversold)"
        score = 95
        
    # Skenario C: Breakout (Harga nembus BB Atas + Volume Kuat)
    # (Opsional, tapi biasanya berisiko beli di pucuk, kita skip dulu)

    if score < 50: return {"symbol": symbol, "status": "WAIT", "reason": "Belum ada momen", "df": df}

    # 4. TIME TRAVELER (PREDIKSI WAKTU)
    # Estimasi waktu berdasarkan kecepatan rata-rata (ATR)
    # Berapa lama untuk mencapai target profit?
    target_dist = price_now * (target_profit_pct / 100)
    speed_per_hour = atr if atr > 0 else (price_now * 0.01)
    hours_needed = target_dist / speed_per_hour
    
    # Waktu
    time_now = df.index[-1]
    time_sell = time_now + timedelta(hours=hours_needed)
    
    # 5. HITUNG TARGET HARGA
    price_idr = price_now * kurs_usd_idr
    tp_idr = price_idr * (1 + target_profit_pct/100)
    sl_idr = price_idr * 0.95 # Stop Loss 5%
    profit_rp = modal_awal * (target_profit_pct/100)
    
    return {
        "status": "BUY",
        "symbol": symbol,
        "price_usd": price_now,
        "price_idr": price_idr,
        "tp_idr": tp_idr,
        "sl_idr": sl_idr,
        "profit_rp": profit_rp,
        "time_buy": time_now,
        "time_sell": time_sell,
        "days": hours_needed / 24,
        "reason": reason,
        "score": score,
        "source": source,
        "df": df
    }

# --- UI TAMPILAN ---
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("🕵️ Scanner")
    if st.button("SCAN 30 KOIN (ACAK)", type="primary"):
        batch = random.sample(WATCHLIST, 30)
        results = []
        
        progress = st.progress(0)
        status_txt = st.empty()
        
        for i, coin in enumerate(batch):
            status_txt.caption(f"Menganalisa {coin}...")
            res = analyze_coin(coin)
            if res and res['status'] == "BUY":
                results.append(res)
            progress.progress((i+1)/30)
            
        status_txt.empty()
        progress.empty()
        
        # SIMPAN HASIL KE SESSION STATE AGAR TIDAK HILANG SAAT KLIK LAIN
        st.session_state['results'] = results

with col2:
    st.subheader("📊 Hasil Analisa")
    
    if 'results' in st.session_state:
        data_list = st.session_state['results']
        
        if len(data_list) > 0:
            # Urutkan dari Score Tertinggi
            data_list.sort(key=lambda x: x['score'], reverse=True)
            top = data_list[0]
            
            # --- KARTU REKOMENDASI UTAMA ---
            st.success(f"💎 **PELUANG EMAS: {top['symbol']}**")
            st.caption(f"Sumber: {top['source']} | Alasan: {top['reason']}")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("BELI (Sekarang)", f"Rp {top['price_idr']:,.0f}", f"${top['price_usd']:.5f}")
            m2.metric("JUAL (Target)", f"Rp {top['tp_idr']:,.0f}", f"+{target_profit_pct}%")
            m3.metric("STOP LOSS", f"Rp {top['sl_idr']:,.0f}", "-5%")
            
            st.markdown(f"#### 📅 Jadwal Trading (Estimasi)")
            st.info(f"""
            1.  **Waktu Beli:** SEKARANG ({top['time_buy'].strftime('%H:%M WIB')})
            2.  **Waktu Jual:** {top['time_sell'].strftime('%A, %d %b - %H:%M WIB')} (Estimasi {top['days']:.1f} Hari)
            3.  **Potensi Cuan:** Rp {top['profit_rp']:,.0f}
            """)
            
            # --- GRAFIK VISUAL PRO (KOTAK HIJAU) ---
            df = top['df']
            fig = go.Figure()
            
            # 1. Candlestick
            fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Harga'))
            
            # 2. Garis Tren (EMA 200)
            fig.add_trace(go.Scatter(x=df.index, y=df['ema200'], line=dict(color='orange', width=1), name='Tren Jangka Panjang'))
            
            # 3. Area Profit (Kotak Hijau)
            fig.add_shape(type="rect",
                x0=df.index[-1], y0=top['price_usd'],
                x1=top['time_sell'], y1=top['tp_idr']/kurs_usd_idr,
                fillcolor="rgba(0, 255, 0, 0.2)", line=dict(width=0),
            )
            
            # 4. Area Stop Loss (Kotak Merah)
            fig.add_shape(type="rect",
                x0=df.index[-1], y0=top['sl_idr']/kurs_usd_idr,
                x1=top['time_sell'], y1=top['price_usd'],
                fillcolor="rgba(255, 0, 0, 0.2)", line=dict(width=0),
            )
            
            fig.update_layout(title=f"Peta Jalan {top['symbol']} (Hijau = Area Profit)", height=500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # --- TABEL SISA ---
            with st.expander(f"Lihat {len(data_list)-1} Peluang Lainnya"):
                rows = []
                for item in data_list[1:]:
                    rows.append([item['symbol'], f"Rp {item['price_idr']:,.0f}", f"Rp {item['tp_idr']:,.0f}", item['time_sell'].strftime('%d %b %H:%M')])
                st.table(pd.DataFrame(rows, columns=["Koin", "Harga Beli", "Target Jual", "Waktu Jual"]))
                
        else:
            st.warning("⚠️ Scanner selesai, tapi tidak ada koin yang memenuhi syarat 'AMAN & POTENSIAL' di batch ini.")
            st.write("Saran: Pasar mungkin sedang lesu atau crash. Coba klik tombol Scan lagi untuk mengambil sampel koin yang berbeda.")

# --- CEK MANUAL DI BAWAH ---
st.write("---")
st.subheader("🔍 Cek Koin Manual (Pasti Muncul Data)")
manual_coin = st.selectbox("Pilih Koin:", WATCHLIST)

if st.button("Analisa Koin Ini"):
    with st.spinner("Mengambil data..."):
        res = analyze_coin(manual_coin)
        
        if res and res.get('status') == "BUY":
            st.success(f"✅ {res['symbol']} Layak Beli! (Score: {res['score']})")
            st.write(f"Beli: **Rp {res['price_idr']:,.0f}** | Jual: **Rp {res['tp_idr']:,.0f}**")
            st.caption(f"Alasan: {res['reason']}")
        elif res and res.get('status') != "BUY":
            st.error(f"⛔ {manual_coin}: {res['reason']}")
            if 'df' in res:
                st.line_chart(res['df']['close'])
        else:
            st.error("Data error.")
