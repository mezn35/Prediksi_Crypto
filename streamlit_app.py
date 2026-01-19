import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
from ta.volatility import BollingerBands
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from datetime import datetime, timedelta
import plotly.graph_objects as go
import random

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SNIPER PRO V2", layout="wide")
st.title("🤖 SNIPER PRO V2: Anti-Longsor")
st.markdown("""
**Perbaikan Algoritma (GitHub Style):**
1.  🔪 **Anti-Falling Knife:** Tidak akan beli saat harga sedang terjun bebas (Crash Protection).
2.  🕯️ **Green Candle Confirmation:** Wajib tunggu candle hijau muncul sebelum Entry.
3.  ⏰ **Real-Time Check:** Menampilkan waktu data terakhir agar tidak tertipu data lama.
""")

# --- DATABASE KOIN ---
WATCHLIST = [
    # --- USDT PAIRS ---
    "BAR/USDT", "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
    "ADA/USDT", "AVAX/USDT", "TRX/USDT", "LINK/USDT", "MATIC/USDT", "DOT/USDT", 
    "LTC/USDT", "BCH/USDT", "UNI/USDT", "NEAR/USDT", "APT/USDT", "XLM/USDT", 
    "SHIB/USDT", "ICP/USDT", "HBAR/USDT", "FIL/USDT", "ATOM/USDT", "VET/USDT", 
    "IMX/USDT", "OP/USDT", "INJ/USDT", "GRT/USDT", "RNDR/USDT", "STX/USDT", 
    "LDO/USDT", "FTM/USDT", "TIA/USDT", "SEI/USDT", "ARB/USDT", "ALGO/USDT", 
    "KAS/USDT", "SUI/USDT", "EGLD/USDT", "QNT/USDT", "AAVE/USDT", "MINA/USDT", 
    "FLOW/USDT", "AXS/USDT", "SAND/USDT", "THETA/USDT", "MANA/USDT", "EOS/USDT", 
    "XTZ/USDT", "NEO/USDT", "KCS/USDT", "CAKE/USDT", "CFX/USDT", "CHZ/USDT", 
    "GALA/USDT", "PEPE/USDT", "FLOKI/USDT", "BONK/USDT", "WIF/USDT", "BOME/USDT", 
    "JASMY/USDT", "LUNC/USDT", "SLP/USDT", "NOT/USDT", "TURBO/USDT", "MEME/USDT", 
    "PEOPLE/USDT", "WLD/USDT", "FET/USDT", "AGIX/USDT", "OCEAN/USDT", "ARKM/USDT",
    "HEI/USDT", "KOM/USDT", "BROCCOLI714/USDT", "PENGU/USDT", "BIO/USDT", "VANA/USDT", 
    "A2Z/USDT", "VELODROME/USDT", "1000CHEEMS/USDT", "TURTLE/USDT", "MDT/USDT", "ACA/USDT", 
    "CITY/USDT", "ATM/USDT", "COS/USDT", "ACM/USDT", "CHESS/USDT", "DATA/USDT", "NBT/USDT", 
    "CREO/USDT", "CVC/USDT", "ALPINE/USDT", "BEL/USDT", "JUV/USDT", "HOOK/USDT", "NKN/USDT", 
    "QUICK/USDT", "DEGO/USDT", "D/USDT", "IDEX/USDT", "GHST/USDT", "UTK/USDT", "FIO/USDT", 
    "TRU/USDT", "ENSO/USDT", "RDNT/USDT", "MITO/USDT", "DODO/USDT", "FARM/USDT", 
    "VIC/USDT", "PSG/USDT", "EDEN/USDT", "SYN/USDT", "DF/USDT", "TST/USDT", "LAZIO/USDT", 
    "TKO/USDT", "MLN/USDT", "WAN/USDT", "HAEDAL/USDT", "NFP/USDT", "ADX/USDT", "BMT/USDT", 
    "ASR/USDT", "GTC/USDT", "TUT/USDT", "TREE/USDT", "INIT/USDT", "SHELL/USDT", "PORTAL/USDT", 
    "HEMI/USDT", "PIVX/USDT", "BIFI/USDT", "TLM/USDT", "SCR/USDT", "HMSTR/USDT", "A/USDT", 
    "PORTO/USDT", "SOLV/USDT", "OG/USDT", "LUMIA/USDT", "RAD/USDT", "TOWNS/USDT", "ALICE/USDT", 
    "SYS/USDT", "HIGH/USDT", "ATA/USDT", "PHB/USDT", "NTRN/USDT", "MBOX/USDT", "F/USDT", 
    "OGN/USDT", "KERNEL/USDT", "MUBARAK/USDT", "HFT/USDT", "SAGA/USDT", "EPIC/USDT", "AI/USDT", 
    "FUN/USDT", "ARPA/USDT", "ALCX/USDT", "STO/USDT", "NOM/USDT", "RARE/USDT", "DOGS/USDT", 
    "CATI/USDT", "NEWT/USDT", "ZBT/USDT", "PYR/USDT", "COOKIE/USDT", "MAV/USDT", "VANRY/USDT", 
    "DENT/USDT", "GNS/USDT", "BANK/USDT", "JOE/USDT", "QI/USDT", "GPS/USDT", "OXT/USDT", 
    "C98/USDT", "ACE/USDT", "CETUS/USDT", "ACT/USDT", "C/USDT", "MBL/USDT", "BANANA/USDT", 
    "WIN/USDT", "AGLD/USDT", "YB/USDT", "MOVR/USDT", "RESOLV/USDT", "ZKC/USDT", "DOLO/USDT", 
    "GLMR/USDT", "FORTH/USDT", "AVA/USDT", "WCT/USDT", "AIXBT/USDT", "PIXEL/USDT", "CELR/USDT", 
    "REZ/USDT", "HOLO/USDT", "POND/USDT", "THE/USDT", "DYM/USDT", "QKC/USDT", "CGPT/USDT", 
    "MIRA/USDT", "HYPER/USDT",
    
    # --- IDR PAIRS ---
    "BTC/IDR", "ETH/IDR", "USDT/IDR", "BNB/IDR", "XRP/IDR", "SOL/IDR", "USDC/IDR", 
    "DOGE/IDR", "ADA/IDR", "SUI/IDR", "AVAX/IDR", "HBAR/IDR", "TON/IDR", "TAO/IDR", 
    "ASTER/IDR", "POL/IDR", "WLD/IDR", "ARB/IDR", "ONDO/IDR", "RENDER/IDR", "VIRTUAL/IDR", 
    "SPX/IDR", "TIA/IDR", "FLOKI/IDR", "WIF/IDR", "SOON/IDR", "ALCH/IDR", "ZIL/IDR", 
    "VELO/IDR", "MEW/IDR", "POPCAT/IDR", "GRASS/IDR", "MOODENG/IDR", "JELLYJELLY/IDR", 
    "CARV/IDR", "NEIRO/IDR", "BOME/IDR", "MANTA/IDR", "GOAT/IDR", "DOGS/IDR", "SCR/IDR"
]

exchange = ccxt.binance({'enableRateLimit': True})

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Pusat Komando")
    modal_awal = st.number_input("Modal Trading (Rp)", value=1000000)
    kurs_usd_idr = st.number_input("Kurs USD/IDR", value=16100)
    profit_target_pct = st.slider("Target Profit (%)", 2.0, 20.0, 5.0)

# --- FUNGSI DATA ---
def get_data(symbol):
    df = None
    source = ""
    # 1. COBA BINANCE (Prioritas Utama)
    try:
        target = symbol.replace("/IDR", "/USDT")
        if "JELLY" in target: target = "JELLY/USDT"
        
        # Ambil 100 candle 15 menit
        bars = exchange.fetch_ohlcv(target, timeframe='15m', limit=100)
        if bars:
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
            df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7) # Convert WIB
            df.set_index('time', inplace=True)
            source = "⚡ Real-Time"
    except: pass
    
    # 2. BACKUP YAHOO (Hanya jika Binance gagal)
    if df is None:
        try:
            yf_sym = symbol.replace("/", "-").replace("USDT", "USD").replace("IDR", "USD")
            data_yf = yf.download(yf_sym, period='5d', interval='15m', progress=False)
            if len(data_yf) > 20:
                if isinstance(data_yf.columns, pd.MultiIndex): data_yf.columns = data_yf.columns.droplevel(1)
                df = data_yf[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
                df.columns = ['open', 'high', 'low', 'close', 'vol']
                df.index = df.index + timedelta(hours=7)
                source = "⚠️ Backup (Delay)"
        except: pass
        
    return df, source

# --- LOGIKA TRADING PRO (Anti-Crash) ---
def analyze_pro(symbol):
    df, source = get_data(symbol)
    if df is None: return None
    
    # Data Terakhir
    last_candle = df.iloc[-1]
    prev_candle = df.iloc[-2]
    
    close = df['close']
    
    # 1. HITUNG INDIKATOR
    df['rsi'] = RSIIndicator(close=close, window=14).rsi()
    df['ema200'] = EMAIndicator(close=close, window=200).ema_indicator()
    bb = BollingerBands(close=close, window=20, window_dev=2)
    df['bb_low'] = bb.bollinger_lband()
    df['bb_high'] = bb.bollinger_hband()
    
    rsi = df['rsi'].iloc[-1]
    last_price = last_candle['close']
    last_open = last_candle['open']
    
    # 2. DETEKSI CRASH / DUMP (Falling Knife)
    # Jika harga turun > 3% dalam 15 menit terakhir
    drop_pct = (last_open - last_price) / last_open * 100
    is_crashing = drop_pct > 3.0
    
    # 3. KONFIRMASI CANDLE HIJAU
    # Apakah candle terakhir hijau? (Close > Open)
    is_green_candle = last_price > last_open
    
    # 4. LOGIKA KEPUTUSAN
    status = "WAIT"
    reason = "Sideways / Belum Ada Momen"
    score = 0
    color = "gray"
    
    # SKENARIO 1: HARGA MURAH TAPI LAGI CRASH (JANGAN BELI)
    if rsi < 30 and is_crashing:
        status = "DANGER"
        reason = "⛔ JANGAN TANGKAP PISAU JATUH! (Sedang Crash)"
        score = -100
        color = "red"
        
    # SKENARIO 2: RSI RENDAH + CANDLE HIJAU (BOLEH BELI)
    # Ini yang kita cari: Sudah murah, dan sudah mulai naik (bounce)
    elif rsi < 40 and is_green_candle and (last_price > df['bb_low'].iloc[-1]):
        status = "BUY SIGNAL"
        reason = "✅ Diskon Valid (RSI Rendah + Mulai Rebound)"
        score = 90
        color = "green"
        
    # SKENARIO 3: UPTREND KUAT (EMA 200) + PULLBACK
    elif (last_price > df['ema200'].iloc[-1]) and (rsi < 50) and is_green_candle:
        status = "BUY ON DIP"
        reason = "🚀 Tren Naik + Koreksi Selesai"
        score = 80
        color = "green"
        
    # SKENARIO 4: JUAL
    elif rsi > 70:
        status = "SELL SIGNAL"
        reason = "Harga Pucuk (Overbought)"
        score = -50
        color = "red"

    # Hitung Target
    price_idr = last_price * kurs_usd_idr
    tp_idr = price_idr * (1 + profit_target_pct/100)
    sl_idr = price_idr * 0.95 # Stop loss 5%
    profit_idr = modal_awal * (profit_target_pct/100)
    
    return {
        "ticker": symbol,
        "price_idr": price_idr,
        "status": status,
        "reason": reason,
        "score": score,
        "color": color,
        "tp_idr": tp_idr,
        "sl_idr": sl_idr,
        "profit_idr": profit_idr,
        "timestamp": last_candle.name, # Waktu data terakhir
        "source": source,
        "df": df
    }

# --- UI DASHBOARD ---
st.info("💡 **FITUR BARU:** Sistem menampilkan waktu data terakhir. Pastikan tanggalnya **HARI INI** agar akurat.")

if st.button("🔍 SCANNER ANTRI-CRASH (ACAK 40)", type="primary"):
    batch = random.sample(WATCHLIST, 40)
    results = []
    
    prog = st.progress(0)
    log_col = st.empty()
    
    for i, c in enumerate(batch):
        res = analyze_pro(c)
        if res:
            if "BUY" in res['status']:
                results.append(res)
                log_col.text(f"🟢 DITEMUKAN: {c}")
            elif "DANGER" in res['status']:
                log_col.text(f"🔴 BAHAYA: {c} (Sedang Longsor)")
        prog.progress((i+1)/40)
    
    prog.empty()
    log_col.empty()
    
    # TAMPILKAN HASIL
    if results:
        results.sort(key=lambda x: x['score'], reverse=True)
        top = results[0]
        
        st.success(f"💎 **PELUANG TERBAIK: {top['ticker']}**")
        
        # CEK WAKTU DATA
        time_str = top['timestamp'].strftime('%d %b %Y, %H:%M WIB')
        st.write(f"📅 **Data Market:** {time_str} | Sumber: {top['source']}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("BELI SEKARANG", f"Rp {top['price_idr']:,.0f}")
        c2.metric("TARGET JUAL", f"Rp {top['tp_idr']:,.0f}", f"+{profit_target_pct}%")
        c3.metric("STOP LOSS", f"Rp {top['sl_idr']:,.0f}", "-5%")
        
        st.info(f"📝 **Alasan AI:** {top['reason']}")
        
        # GRAFIK
        df = top['df']
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Harga'))
        
        # Tambahkan Marker Sinyal
        fig.add_annotation(x=top['timestamp'], y=top['price_idr']/kurs_usd_idr, text="ENTRY", showarrow=True, arrowhead=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("---")
        st.write("### Opsi Lainnya:")
        rows = []
        for r in results[1:]:
            rows.append([r['ticker'], r['status'], f"Rp {r['price_idr']:,.0f}", r['timestamp'].strftime('%H:%M')])
        st.table(pd.DataFrame(rows, columns=["Koin", "Sinyal", "Harga", "Jam Data"]))
        
    else:
        st.warning("Tidak ada sinyal BELI yang aman saat ini. Pasar mungkin sedang crash atau flat. Coba scan lagi nanti.")

# --- CEK MANUAL ---
st.sidebar.markdown("---")
manual_coin = st.sidebar.selectbox("Cek Koin Manual", WATCHLIST)
if st.sidebar.button("Analisa"):
    res = analyze_pro(manual_coin)
    if res:
        st.sidebar.markdown(f"### :{res['color']}[{res['status']}]")
        st.sidebar.caption(f"Data: {res['timestamp'].strftime('%H:%M WIB')} ({res['source']})")
        st.sidebar.write(res['reason'])
        st.sidebar.metric("Harga", f"Rp {res['price_idr']:,.0f}")
    else:
        st.sidebar.error("Data tidak ditemukan.")
