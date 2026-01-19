import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
import requests # Untuk ambil data Fear & Greed
import plotly.graph_objects as go
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from datetime import datetime, timedelta
import time
import random

# --- KONFIGURASI ---
st.set_page_config(page_title="AI SOCIAL PRO", layout="wide")
st.title("🌐 AI SOCIAL PRO: Grafik + Sentimen Internet")
st.markdown("""
**Fitur Baru:**
1.  📢 **Social Sentinel:** Mengambil data "Fear & Greed Index" (Rangkuman Hype Medsos & Google).
2.  🧠 **Smart Logic:** Menyesuaikan strategi berdasarkan suasana hati pasar (Serakah vs Takut).
3.  🛡️ **Pos Ronda:** Tetap memantau 24 jam.
""")

# --- DATABASE KOIN ---
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

# --- SETUP EXCHANGE ---
exchanges = {
    'binance': ccxt.binance({'enableRateLimit': True}),
    'gateio': ccxt.gateio({'enableRateLimit': True}),
    'mexc': ccxt.mexc({'enableRateLimit': True}),
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎛️ Kontrol")
    run_sentinel = st.checkbox("🔴 AKTIFKAN POS RONDA", value=False)
    st.write("---")
    target_pct = st.slider("Target Cuan (%)", 2.0, 50.0, 5.0)
    kurs_usd = st.number_input("Kurs USD", value=16200)

# --- FUNGSI 1: AMBIL SENTIMEN SOSIAL (FEAR & GREED) ---
def get_social_sentiment():
    try:
        # Mengambil data dari API Alternative.me (Standard Industri)
        url = "https://api.alternative.me/fng/"
        response = requests.get(url)
        data = response.json()
        
        value = int(data['data'][0]['value'])
        status = data['data'][0]['value_classification']
        
        return value, status
    except:
        return 50, "Neutral" # Default jika error

# --- FUNGSI 2: DATA MARKET ---
def get_data(symbol):
    pair = symbol.replace("/IDR", "/USDT")
    df = None
    source = ""
    
    # Cek Multi-Exchange
    for name, exc in exchanges.items():
        try:
            bars = exc.fetch_ohlcv(pair, timeframe='1h', limit=100)
            if bars:
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
                df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
                df.set_index('time', inplace=True)
                source = name.upper()
                break
        except: continue
        
    # Backup Yahoo
    if df is None:
        try:
            yf_sym = pair.replace("/", "-").replace("USDT", "USD")
            data_yf = yf.download(yf_sym, period='5d', interval='1h', progress=False)
            if len(data_yf) > 20:
                if isinstance(data_yf.columns, pd.MultiIndex): data_yf.columns = data_yf.columns.droplevel(1)
                df = data_yf[['Open', 'High', 'Low', 'Close', 'Volume']]
                df.columns = ['open', 'high', 'low', 'close', 'vol']
                df.index = df.index + timedelta(hours=7)
                source = "Yahoo (Delay)"
        except: pass
        
    return df, source

# --- FUNGSI 3: ANALISA CERDAS (GRAFIK + SENTIMEN) ---
def analyze_smart(symbol, sentiment_score):
    df, source = get_data(symbol)
    if df is None: return None
    
    close = df['close']
    current_price = close.iloc[-1]
    
    # Indikator
    df['ema200'] = EMAIndicator(close=close, window=200).ema_indicator()
    df['rsi'] = RSIIndicator(close=close, window=14).rsi()
    
    rsi = df['rsi'].iloc[-1]
    ema200 = df['ema200'].iloc[-1]
    
    # --- LOGIKA SOCIAL SENTIMENT ---
    # Jika Internet lagi "EXTREME FEAR" (Nilai < 20) -> Saatnya Serok Bawah (Diskon Besar)
    # Jika Internet lagi "EXTREME GREED" (Nilai > 75) -> Hati-hati Pucuk (Jangan Beli)
    
    is_buy = False
    reason = ""
    
    # KONDISI 1: PASAR TAKUT (Fear < 30) -> Kita cari pantulan (Rebound)
    if sentiment_score < 30:
        if rsi < 30: # RSI juga Oversold
            is_buy = True
            reason = "💎 GEM: Pasar Panik + Harga Murah (Serok!)"
            
    # KONDISI 2: PASAR NORMAL (30-70) -> Kita cari Tren (Uptrend)
    elif 30 <= sentiment_score <= 70:
        if current_price > ema200 and rsi < 50:
            is_buy = True
            reason = "🚀 TREND: Pasar Stabil + Uptrend Sehat"
            
    # KONDISI 3: PASAR SERAKAH (Greed > 70) -> Sangat Selektif
    else:
        # Kalau pasar lagi gila (Greed), kita cuma beli kalau koreksi dalam banget
        if current_price > ema200 and rsi < 40:
            is_buy = True
            reason = "⚠️ RISKY: Beli Koreksi di tengah FOMO"

    if is_buy:
        return {
            "symbol": symbol,
            "entry": current_price,
            "tp": current_price * (1 + target_pct/100),
            "source": source,
            "reason": reason,
            "df": df
        }
    return None

# --- UI UTAMA ---
# TAMPILKAN SENTIMEN INTERNET DI ATAS
sent_val, sent_text = get_social_sentiment()

col_sent1, col_sent2 = st.columns([1, 4])
with col_sent1:
    st.metric("Sentimen Internet", f"{sent_val}/100", sent_text)

with col_sent2:
    if sent_val < 25:
        st.error("📉 STATUS: EXTREME FEAR (Pasar Panik). Waktunya cari diskon!")
    elif sent_val > 75:
        st.warning("📈 STATUS: EXTREME GREED (Pasar Serakah). Hati-hati nyangkut di pucuk!")
    else:
        st.info("⚖️ STATUS: NETRAL. Cari koin yang tren-nya bagus.")

# --- POS RONDA ---
placeholder = st.empty()

if run_sentinel:
    while True:
        batch = random.sample(WATCHLIST, 3)
        with placeholder.container():
            st.write(f"Mencari peluang di tengah sentimen **{sent_text}**...")
            
            for coin in batch:
                res = analyze_smart(coin, sent_val)
                time.sleep(1) # Santai biar ga di-banned
                
                if res:
                    st.success(f"🚨 **DITEMUKAN: {res['symbol']}**")
                    st.caption(f"Alasan: {res['reason']}")
                    
                    c1, c2 = st.columns(2)
                    c1.metric("BELI", f"${res['entry']:.5f}", f"Rp {res['entry']*kurs_usd:,.0f}")
                    c2.metric("JUAL", f"${res['tp']:.5f}")
                    
                    # Grafik
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['open'], high=res['df']['high'], low=res['df']['low'], close=res['df']['close']))
                    fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['ema200'], line=dict(color='orange'), name='EMA 200'))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Suara
                    audio_html = """<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-37.mp3" type="audio/mpeg"></audio>"""
                    st.markdown(audio_html, unsafe_allow_html=True)
                    
                    st.stop()
        
        time.sleep(5)

else:
    placeholder.info("Centang **AKTIFKAN POS RONDA** untuk memulai.")
