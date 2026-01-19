import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
import plotly.graph_objects as go
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from datetime import datetime, timedelta
import time
import random
import base64

# --- KONFIGURASI ---
st.set_page_config(page_title="AI SENTINEL (AUTO-ALARM)", layout="wide")

# --- JUDUL & STATUS ---
st.title("🚨 AI SENTINEL: Pos Ronda 24 Jam")
st.markdown("""
**Cara Kerja Mode Otomatis:**
1.  Centang **"AKTIFKAN POS RONDA"** di menu kiri.
2.  Biarkan layar menyala (Jangan di-close). Keraskan volume speaker.
3.  AI akan mencari koin "Perfect Buy" setiap 60 detik.
4.  Jika ketemu, **ALARM AKAN BERBUNYI** memanggil Anda.
""")

# --- DATABASE KOIN MICIN (< 10k) ---
WATCHLIST = [
    "HEI/USDT", "BROCCOLI714/USDT", "PENGU/USDT", "BIO/USDT", "A2Z/USDT", 
    "VELODROME/USDT", "1000CHEEMS/USDT", "TURTLE/USDT", "MDT/USDT", "ACA/USDT", 
    "COS/USDT", "ACM/USDT", "CHESS/USDT", "DATA/USDT", "NBT/USDT", "CVC/USDT", 
    "ALPINE/USDT", "BEL/USDT", "HOOK/USDT", "NKN/USDT", "QUICK/USDT", "DEGO/USDT", 
    "D/USDT", "IDEX/USDT", "GHST/USDT", "UTK/USDT", "FIO/USDT", "TRU/USDT", 
    "ENSO/USDT", "RDNT/USDT", "MITO/USDT", "DODO/USDT", "BAR/USDT", "VIC/USDT", 
    "EDEN/USDT", "SYN/USDT", "DF/USDT", "TST/USDT", "TKO/USDT", "WAN/USDT", 
    "HAEDAL/USDT", "NFP/USDT", "ADX/USDT", "BMT/USDT", "GTC/USDT", "TUT/USDT", 
    "TREE/USDT", "INIT/USDT", "SHELL/USDT", "PORTAL/USDT", "HEMI/USDT", "PIVX/USDT", 
    "TLM/USDT", "SCR/USDT", "HMSTR/USDT", "A/USDT", "SOLV/USDT", "LUMIA/USDT", 
    "RAD/USDT", "TOWNS/USDT", "ALICE/USDT", "SYS/USDT", "HIGH/USDT", "ATA/USDT", 
    "PHB/USDT", "NTRN/USDT", "MBOX/USDT", "F/USDT", "OGN/USDT", "KERNEL/USDT", 
    "MUBARAK/USDT", "HFT/USDT", "SAGA/USDT", "EPIC/USDT", "AI/USDT", "FUN/USDT", 
    "ARPA/USDT", "STO/USDT", "NOM/USDT", "RARE/USDT", "DOGS/USDT", "CATI/USDT", 
    "NEWT/USDT", "ZBT/USDT", "PYR/USDT", "COOKIE/USDT", "MAV/USDT", "VANRY/USDT", 
    "DENT/USDT", "BANK/USDT", "JOE/USDT", "QI/USDT", "GPS/USDT", "OXT/USDT", 
    "C98/USDT", "ACE/USDT", "CETUS/USDT", "ACT/USDT", "C/USDT", "MBL/USDT", 
    "WIN/USDT", "AGLD/USDT", "YB/USDT", "RESOLV/USDT", "ZKC/USDT", "DOLO/USDT", 
    "GLMR/USDT", "AVA/USDT", "WCT/USDT", "AIXBT/USDT", "PIXEL/USDT", "CELR/USDT", 
    "REZ/USDT", "HOLO/USDT", "POND/USDT", "THE/USDT", "DYM/USDT", "QKC/USDT", 
    "CGPT/USDT", "MIRA/USDT", "HYPER/USDT", "TRX/USDT", "1000CAT/USDT", "DOGE/USDT", 
    "ADA/USDT", "XLM/USDT", "HBAR/USDT", "SHIB/USDT", "WLFI/USDT", "PEPE/USDT", 
    "ENA/USDT", "POL/USDT", "WLD/USDT", "SKY/USDT", "ARB/USDT", "ONDO/USDT", 
    "ALGO/USDT", "VET/USDT", "PUMP/USDT", "BONK/USDT", "SEI/USDT", "JUP/USDT", 
    "OP/USDT", "STX/USDT", "XTZ/USDT", "FET/USDT", "CRV/USDT", "CHZ/USDT", 
    "IMX/USDT", "LDO/USDT", "TIA/USDT", "FLOKI/USDT", "GRT/USDT", "2Z/USDT", 
    "STRK/USDT", "SYRUP/USDT", "CFX/USDT", "JASMY/USDT", "SUN/USDT", "BTTC/USDT", 
    "SAND/USDT", "IOTA/USDT", "PYTH/USDT", "WIF/USDT", "ZK/USDT", "KAIA/USDT", 
    "GALA/USDT", "JST/USDT", "THETA/USDT", "MANA/USDT", "BAT/USDT", "WAL/USDT", 
    "XPL/USDT", "GLM/USDT", "S/USDT", "XEC/USDT", "LUNC/USDT", "1INCH/USDT", 
    "EIGEN/USDT", "FF/USDT", "W/USDT", "AMP/USDT", "SFP/USDT", "KITE/USDT", 
    "JTO/USDT", "RSR/USDT", "APE/USDT", "SNX/USDT", "DYDX/USDT", "BEAMX/USDT", 
    "MET/USDT", "FORM/USDT", "SUPER/USDT", "TFUEL/USDT", "FLOW/USDT", "COW/USDT", 
    "MOVE/USDT", "CKB/USDT", "KAITO/USDT", "ME/USDT", "ZRX/USDT", "DGB/USDT", 
    "RVN/USDT", "XVG/USDT", "TURBO/USDT", "ACH/USDT", "ZIL/USDT", "T/USDT", 
    "MINA/USDT", "AWE/USDT", "ROSE/USDT", "EDU/USDT", "1MBABYDOGE/USDT", "BLUR/USDT", 
    "ID/USDT", "LINEA/USDT", "SUSHI/USDT", "KAVA/USDT", "HOME/USDT", "STG/USDT", 
    "ASTR/USDT", "SC/USDT", "HOT/USDT", "NXPC/USDT", "OM/USDT", "AXL/USDT", 
    "REQ/USDT", "VTHO/USDT", "CELO/USDT", "PNUT/USDT", "IOTX/USDT", "PROVE/USDT", 
    "RED/USDT", "AVNT/USDT", "DUSK/USDT", "LRC/USDT", "ANKR/USDT", "SAHARA/USDT", 
    "MEME/USDT", "HUMA/USDT", "ALT/USDT", "POLYX/USDT", "SKL/USDT", "ICX/USDT", 
    "BB/USDT", "SIGN/USDT", "ENJ/USDT", "ONE/USDT", "LUNA/USDT", "STORJ/USDT", 
    "NOT/USDT", "ONT/USDT", "ARDR/USDT", "LA/USDT", "BAND/USDT", "GMT/USDT", 
    "WOO/USDT", "PLUME/USDT", "COTI/USDT", "RONIN/USDT", "ARK/USDT", "POWR/USDT", 
    "HIVE/USDT", "BIGTIME/USDT", "PEOPLE/USDT", "SPK/USDT", "NEIRO/USDT", 
    "BABY/USDT", "YGG/USDT", "IOST/USDT", "G/USDT", "LAYER/USDT", "USUAL/USDT", 
    "LISTA/USDT", "BNT/USDT", "FLUX/USDT", "LSK/USDT", "ARKM/USDT", "SPELL/USDT", 
    "IO/USDT", "SCRT/USDT", "STRAX/USDT", "BICO/USDT", "BOME/USDT", "SXP/USDT", 
    "KNC/USDT", "SOMI/USDT", "OSMO/USDT", "PARTI/USDT", "ANIME/USDT", "AUDIO/USDT", 
    "AT/USDT", "CTK/USDT", "IQ/USDT", "CHR/USDT", "WAXP/USDT", "LQTY/USDT", 
    "ONG/USDT", "USTC/USDT", "AEVO/USDT", "API3/USDT", "SXT/USDT", "1000SATS/USDT", 
    "OPEN/USDT", "BANANAS31/USDT", "MANTA/USDT", "XAI/USDT", "GUN/USDT", "RIF/USDT", 
    "MTL/USDT", "FIDA/USDT", "ACX/USDT", "DIA/USDT", "SLP/USDT", "MAGIC/USDT", 
    "ERA/USDT", "PHA/USDT", "CTSI/USDT", "TNSR/USDT"
]

# --- SETUP ---
exchanges = {
    'binance': ccxt.binance({'enableRateLimit': True}),
    'gateio': ccxt.gateio({'enableRateLimit': True}),
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎛️ Pusat Kontrol")
    run_sentinel = st.checkbox("🔴 AKTIFKAN POS RONDA (AUTO-SCAN)", value=False)
    
    st.write("---")
    st.write("**Setting Target:**")
    target_pct = st.slider("Target Cuan (%)", 2.0, 50.0, 5.0)
    kurs_usd_idr = st.number_input("Kurs USD", value=16200)

# --- FUNGSI ALARM ---
def play_alarm():
    # Suara Beep Keras (Base64)
    audio_html = """
    <audio autoplay>
    <source src="https://www.soundjay.com/buttons/sounds/button-37.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# --- FUNGSI DATA ---
def get_data(symbol):
    pair = symbol.replace("/IDR", "/USDT")
    df = None
    source = ""
    
    # 1. Binance
    try:
        bars = exchanges['binance'].fetch_ohlcv(pair, timeframe='1h', limit=200)
        if bars:
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
            df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
            df.set_index('time', inplace=True)
            source = "Binance"
    except: pass
    
    # 2. Yahoo (Backup)
    if df is None:
        try:
            yf_sym = pair.replace("/", "-").replace("USDT", "USD")
            data_yf = yf.download(yf_sym, period='5d', interval='1h', progress=False)
            if len(data_yf) > 50:
                if isinstance(data_yf.columns, pd.MultiIndex): data_yf.columns = data_yf.columns.droplevel(1)
                df = data_yf[['Open', 'High', 'Low', 'Close', 'Volume']]
                df.columns = ['open', 'high', 'low', 'close', 'vol']
                df.index = df.index + timedelta(hours=7)
                source = "Yahoo"
        except: pass
        
    return df, source

# --- LOGIKA KETAT (PENGECUT / AMAN) ---
def check_for_golden_moment(symbol):
    df, source = get_data(symbol)
    if df is None or len(df) < 50: return None
    
    close = df['close']
    
    # Indikator
    df['ema200'] = EMAIndicator(close=close, window=200).ema_indicator()
    df['ema50'] = EMAIndicator(close=close, window=50).ema_indicator()
    df['rsi'] = RSIIndicator(close=close, window=14).rsi()
    
    current_price = close.iloc[-1]
    ema200 = df['ema200'].iloc[-1]
    ema50 = df['ema50'].iloc[-1]
    rsi = df['rsi'].iloc[-1]
    
    # SYARAT 1: HARUS UPTREND (Harga > EMA 200)
    # Ini syarat mutlak "Pengecut" biar gak rugi
    if current_price < ema200: return None 
    
    # SYARAT 2: HARUS DISKON (RSI < 45)
    # Kita tidak mau beli di pucuk
    if rsi > 45: return None
    
    # Jika lolos dua syarat di atas = GOLDEN MOMENT
    return {
        "symbol": symbol,
        "entry": current_price,
        "tp": current_price * (1 + target_pct/100),
        "sl": current_price * 0.95,
        "rsi": rsi,
        "source": source,
        "df": df
    }

# --- LOOPING MONITORING (THE SENTINEL) ---
monitor_placeholder = st.empty()
result_placeholder = st.empty()

if run_sentinel:
    st.toast("🛡️ POS RONDA AKTIF! Jangan tutup tab ini.")
    
    while True:
        # 1. Ambil 5 koin acak untuk dicek (supaya tidak kena limit)
        batch = random.sample(WATCHLIST, 5)
        
        # Tampilan Status (Biar tau AI hidup)
        current_time = datetime.now().strftime("%H:%M:%S")
        with monitor_placeholder.container():
            st.info(f"🕒 {current_time} | Sedang meronda: {', '.join(batch)} ...")
        
        # 2. Cek Koin
        found_signal = False
        for coin in batch:
            res = check_for_golden_moment(coin)
            if res:
                found_signal = True
                
                # --- JIKA KETEMU ---
                play_alarm() # BUNYIKAN ALARM
                
                with result_placeholder.container():
                    st.success(f"🚨 **ALARM! PELUANG DITEMUKAN: {res['symbol']}**")
                    st.write(f"RSI: {res['rsi']:.1f} (Murah & Uptrend)")
                    
                    c1, c2 = st.columns(2)
                    c1.metric("BELI SEKARANG", f"${res['entry']:.6f}")
                    c2.metric("JUAL NANTI", f"${res['tp']:.6f}", f"+{target_pct}%")
                    
                    # Grafik
                    df = res['df']
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close']))
                    fig.add_trace(go.Scatter(x=df.index, y=df['ema200'], line=dict(color='blue'), name='EMA 200'))
                    # Kotak Hijau
                    fig.add_shape(type="rect", x0=df.index[-1], y0=res['entry'], x1=df.index[-1]+timedelta(hours=12), y1=res['tp'], fillcolor="rgba(0,255,0,0.2)", line=dict(width=0))
                    
                    st.plotly_chart(fig, use_container_width=True)
                    st.stop() # BERHENTI SCAN SUPAYA USER BISA LIHAT
        
        # 3. Jeda Waktu (Supaya tidak diblokir Binance)
        time.sleep(15) # Istirahat 15 detik sebelum scan lagi
        
else:
    monitor_placeholder.info("👈 Centang **'AKTIFKAN POS RONDA'** di sebelah kiri untuk menyalakan mode otomatis.")
    
    # Tombol Scan Manual Biasa
    if st.button("Scan Manual Sekali Saja"):
        batch = random.sample(WATCHLIST, 20)
        found = False
        progress = st.progress(0)
        for i, c in enumerate(batch):
            res = check_for_golden_moment(c)
            if res:
                st.success(f"✅ DITEMUKAN: {res['symbol']} (RSI {res['rsi']:.1f})")
                found = True
            progress.progress((i+1)/20)
        
        if not found:
            st.warning("Belum ada koin yang lolos filter 'Aman & Murah' di batch ini.")
