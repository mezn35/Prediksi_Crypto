import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# --- KONFIGURASI ---
st.set_page_config(page_title="AI FORECASTER V4 (Anti-Blokir)", layout="wide")
st.title("🔮 AI FORECASTER: Prediksi 2 Langkah (Anti-Blokir)")
st.markdown("""
**Fitur Perbaikan:**
1.  🛡️ **Dual Engine:** Jika Binance macet, otomatis pakai Data Cadangan.
2.  ⚡ **Real-Time Price:** Mengutamakan harga detik ini.
3.  👣 **2 Target:** Target Pendek (Cepat) & Target Jauh (Swing).
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

# Inisialisasi Exchange
exchange = ccxt.binance({'enableRateLimit': True, 'timeout': 10000})

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Pengaturan Kurs")
    kurs_usd_idr = st.number_input("Kurs USD ke IDR", value=16200, step=50)
    st.info("Sistem sekarang punya 'Ban Serep'. Kalau server utama macet, dia otomatis ganti jalur.")

# --- FUNGSI PENGAMBIL DATA (ROBUST) ---
def get_robust_data(symbol):
    # TARGET 1: COBA BINANCE (REAL-TIME)
    try:
        # Bersihkan simbol untuk CCXT (Binance butuh format BTC/USDT)
        target_ccxt = symbol.replace("/IDR", "/USDT")
        
        # Ambil Harga Terakhir (Ticker)
        ticker = exchange.fetch_ticker(target_ccxt)
        current_price = ticker['last']
        
        # Ambil History Candle (untuk tren)
        bars = exchange.fetch_ohlcv(target_ccxt, timeframe='1h', limit=50)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
        
        return df, current_price, "⚡ Real-Time (Binance)"
        
    except Exception as e:
        # JIKA GAGAL, MASUK TARGET 2: YAHOO FINANCE (BACKUP)
        try:
            # Bersihkan simbol untuk Yahoo (Butuh format BTC-USD)
            target_yf = symbol.replace("/", "-").replace("USDT", "USD").replace("IDR", "USD")
            
            # Download Data
            data_yf = yf.download(target_yf, period='5d', interval='1h', progress=False)
            
            if len(data_yf) > 0:
                # Perbaikan MultiIndex Yahoo
                if isinstance(data_yf.columns, pd.MultiIndex):
                    data_yf.columns = data_yf.columns.droplevel(1)
                
                # Format ulang biar sama kayak Binance
                df = data_yf.reset_index()
                df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
                df.columns = ['time', 'open', 'high', 'low', 'close', 'vol']
                df['time'] = df['time'] + timedelta(hours=7) # Sesuaikan WIB
                
                current_price = df['close'].iloc[-1]
                return df, current_price, "⚠️ Backup (Yahoo)"
            else:
                return None, None, "Error"
        except:
            return None, None, "Error"

# --- ALGORITMA PREDIKSI ---
def analyze_forecast(symbol):
    # 1. AMBIL DATA (Pake fungsi anti-blokir di atas)
    df, current_price, source = get_robust_data(symbol)
    
    if df is None: return None
    
    # 2. HITUNG KEKUATAN GERAK (ATR)
    # Ini ngukur seberapa jauh harga bisa lari dalam beberapa jam ke depan
    df['tr'] = df['high'] - df['low']
    atr = df['tr'].rolling(14).mean().iloc[-1]
    
    # Kalau data ATR error (misal koin baru), pakai 2% dari harga
    if np.isnan(atr) or atr == 0: atr = current_price * 0.02
    
    # 3. PREDIKSI 2 LANGKAH
    # Target 1 (Aman): Harga + (0.8 x Kekuatan Gerak)
    target_1 = current_price + (atr * 0.8)
    
    # Target 2 (Lanjut): Harga + (2.0 x Kekuatan Gerak)
    target_2 = current_price + (atr * 2.0)
    
    # Stop Loss (Pengaman)
    stop_loss = current_price - (atr * 0.6)
    
    # 4. WAKTU
    time_now = datetime.now() + timedelta(hours=7)
    time_s1 = time_now + timedelta(hours=3) # Est 3 jam
    time_s2 = time_now + timedelta(hours=8) # Est 8 jam
    
    # 5. KONVERSI RUPIAH
    res = {
        "symbol": symbol,
        "source": source,
        "now_usd": current_price,
        "now_idr": current_price * kurs_usd_idr,
        "t1_idr": target_1 * kurs_usd_idr,
        "t2_idr": target_2 * kurs_usd_idr,
        "sl_idr": stop_loss * kurs_usd_idr,
        "t1_pct": ((target_1 - current_price)/current_price)*100,
        "t2_pct": ((target_2 - current_price)/current_price)*100,
        "history": df,
        "times": [time_now, time_s1, time_s2]
    }
    return res

# --- UI TAMPILAN ---
col_left, col_right = st.columns([2, 1])

with col_right:
    st.subheader("🔍 Pilih Koin")
    manual_coin = st.selectbox("Daftar Koin:", WATCHLIST, index=0)
    
    if st.button("Ramal Koin Ini 🔥"):
        with st.spinner("Menghubungkan ke market..."):
            data = analyze_forecast(manual_coin)
            
            if data:
                st.session_state['forecast_data'] = data
            else:
                st.error("Data tidak ditemukan di server manapun (Binance/Yahoo). Koin mungkin terlalu baru.")

# --- TAMPILAN HASIL ---
if 'forecast_data' in st.session_state:
    d = st.session_state['forecast_data']
    
    with col_left:
        # Header Status
        status_color = "green" if "Real-Time" in d['source'] else "orange"
        st.caption(f"Sumber Data: :{status_color}[{d['source']}] | Update: {d['times'][0].strftime('%H:%M:%S')} WIB")
        
        # METRIK BESAR
        c1, c2, c3 = st.columns(3)
        c1.metric("HARGA SEKARANG", f"Rp {d['now_idr']:,.0f}", f"${d['now_usd']:.5f}")
        c2.metric("TARGET 1 (Pendek)", f"Rp {d['t1_idr']:,.0f}", f"+{d['t1_pct']:.2f}%")
        c3.metric("TARGET 2 (Jauh)", f"Rp {d['t2_idr']:,.0f}", f"+{d['t2_pct']:.2f}%")
        
        # PESAN STRATEGI
        st.info(f"""
        **Strategi Eksekusi {d['symbol']}:**
        1.  🟢 **BELI SEKARANG** di harga pasar (**Rp {d['now_idr']:,.0f}**).
        2.  🟡 Jual 50% aset saat menyentuh **Rp {d['t1_idr']:,.0f}** (Amankan modal).
        3.  🟢 Jual sisanya saat menyentuh **Rp {d['t2_idr']:,.0f}** (Cuan maksimal).
        4.  🔴 **WAJIB CUT LOSS** jika harga turun ke **Rp {d['sl_idr']:,.0f}**.
        """)
        
        # GRAFIK MASA DEPAN
        fig = go.Figure()
        
        # Plot History
        hist = d['history']
        fig.add_trace(go.Scatter(x=hist['time'], y=hist['close']*kurs_usd_idr, mode='lines', name='Trend', line=dict(color='#00F0FF')))
        
        # Plot Titik Sekarang
        fig.add_trace(go.Scatter(x=[d['times'][0]], y=[d['now_idr']], mode='markers', name='Entry', marker=dict(color='white', size=10)))
        
        # Plot Jalur Prediksi
        fig.add_trace(go.Scatter(
            x=[d['times'][0], d['times'][1], d['times'][2]], 
            y=[d['now_idr'], d['t1_idr'], d['t2_idr']],
            mode='lines+markers+text',
            name='Jalur Prediksi',
            line=dict(color='#00FF00', width=3, dash='dot'),
            text=["", "Target 1", "Target 2"],
            textposition="top left"
        ))
        
        fig.update_layout(title=f"Peta Jalan {d['symbol']}", height=450, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# --- SCANNER CEPAT DI BAWAH ---
st.write("---")
st.subheader("⚡ Scanner Potensi (Acak 5 Koin)")
if st.button("Cari Peluang Lain"):
    batch = random.sample(WATCHLIST, 5)
    cols = st.columns(5)
    
    for i, coin in enumerate(batch):
        with cols[i]:
            res = analyze_forecast(coin)
            if res:
                st.write(f"**{res['symbol']}**")
                st.write(f"T1: +{res['t1_pct']:.2f}%")
                st.write(f"T2: +{res['t2_pct']:.2f}%")
            else:
                st.write(f"{coin}: -")
