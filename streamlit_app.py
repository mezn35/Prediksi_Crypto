import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import requests # Kita pakai jalur HTTP standar
import plotly.graph_objects as go
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from datetime import datetime, timedelta
import time
import random

# --- KONFIGURASI ---
st.set_page_config(page_title="AI TRINITY: GROQ LLaMA 3", layout="wide")
st.title("🎛️ AI TRINITY: LLaMA 3 Edition (Super Fast)")

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
    st.header("🎮 MODE SCANNER")
    mode_operasi = st.radio(
        "Strategi:",
        ("🔥 MODE 1: Super Agresif", "🧠 MODE 2: Moderat Cerdas", "🛡️ MODE 3: Sentinel Klasik")
    )
    
    st.divider()
    if "MODE 3" not in mode_operasi:
        st.header("🧠 OTAK AI (GROQ)")
        st.caption("Dapatkan key di console.groq.com (Gratis & Cepat)")
        groq_key = st.text_input("Groq API Key (gsk_...)", type="password")
        
        if st.button("🛠️ TES KONEKSI AI"):
            if not groq_key:
                st.error("Isi Key dulu bos!")
            else:
                try:
                    r = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                        json={"model": "llama3-70b-8192", "messages": [{"role": "user", "content": "hi"}]}
                    )
                    if r.status_code == 200: st.success("✅ AI LLaMA 3 SIAP TEMPUR!")
                    else: st.error(f"❌ Gagal: {r.status_code} - {r.text}")
                except Exception as e: st.error(f"Error: {e}")
    else:
        groq_key = None

    st.divider()
    st.header("🎛️ KONTROL")
    run_sentinel = st.checkbox("🔴 AKTIFKAN POS RONDA", value=False)
    target_pct = st.slider("Target Cuan (%)", 2.0, 50.0, 5.0)
    kurs_usd = st.number_input("Kurs USD", value=16200)

# --- FUNGSI SENTIMEN ---
def get_social_sentiment():
    try:
        r = requests.get("https://api.alternative.me/fng/")
        d = r.json()
        return int(d['data'][0]['value']), d['data'][0]['value_classification']
    except: return 50, "Neutral"

# --- FUNGSI ASK AI (GROQ LLaMA 3) ---
def ask_ai_groq(symbol, price, rsi, trend, mode, sentiment):
    if not groq_key: return "⚠️ Pasang API Key Groq"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    Act as a Senior Crypto Scalper.
    Coin: {symbol}, Price: ${price}, RSI: {rsi:.1f}, Trend: {trend}.
    Market Sentiment: {sentiment}. Strategy Mode: {mode}.
    
    Is this a valid entry? Answer with YES or NO and a very short reason (max 1 sentence).
    """
    
    payload = {
        "model": "llama3-70b-8192", # Model LLaMA 3 yang sangat cepat
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 50
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error AI: {response.status_code}"
    except Exception as e:
        return f"Koneksi AI Putus: {str(e)}"

# --- FUNGSI DATA ---
def get_data(symbol):
    pair = symbol.replace("/IDR", "/USDT")
    df = None; source = ""
    for name, exc in exchanges.items():
        try:
            bars = exc.fetch_ohlcv(pair, timeframe='1h', limit=100)
            if bars:
                df = pd.DataFrame(bars, columns=['time','open','high','low','close','vol'])
                df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
                df.set_index('time', inplace=True)
                source = name.upper(); break
        except: continue
    
    if df is None: # Backup Yahoo
        try:
            d = yf.download(pair.replace("/","-").replace("USDT","USD"), period='5d', interval='1h', progress=False)
            if len(d) > 20:
                if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.droplevel(1)
                df = d[['Open','High','Low','Close','Volume']]
                df.columns = ['open','high','low','close','vol']
                df.index = df.index + timedelta(hours=7)
                source = "Yahoo"
        except: pass
    return df, source

# --- ANALISA CORE ---
def analyze(symbol, mode, sent_idx, sent_text):
    df, src = get_data(symbol)
    if df is None: return None
    
    close = df['close']; curr = close.iloc[-1]
    df['ema200'] = EMAIndicator(close, window=200).ema_indicator()
    df['ema50'] = EMAIndicator(close, window=50).ema_indicator()
    df['rsi'] = RSIIndicator(close, window=14).rsi()
    
    rsi = df['rsi'].iloc[-1]; ema200 = df['ema200'].iloc[-1]
    trend = "UPTREND" if curr > ema200 else "DOWNTREND"
    
    res = None; ai_msg = "-"
    
    if "MODE 1" in mode: # Agresif
        if rsi < 35:
            ai_msg = ask_ai_groq(symbol, curr, rsi, trend, "SCALPING/REBOUND", sent_text)
            res = {"type": "🔥 AGRESIF", "reason": "RSI Oversold"}
            
    elif "MODE 2" in mode: # Moderat
        if curr > ema200 and rsi < 55:
            ai_msg = ask_ai_groq(symbol, curr, rsi, trend, "SWING/TREND", sent_text)
            res = {"type": "🧠 MODERAT", "reason": "Trend Pullback"}
            
    elif "MODE 3" in mode: # Klasik
        if curr > ema200 and curr > df['ema50'].iloc[-1] and rsi < 45:
            res = {"type": "🛡️ SENTINEL", "reason": "Technical Only"}
            ai_msg = "Non-Aktif"

    if res:
        res.update({"symbol": symbol, "entry": curr, "tp": curr*(1+target_pct/100), "rsi": rsi, "ai": ai_msg, "df": df, "src": src})
        return res
    return None

# --- UI DISPLAY ---
s_val, s_txt = get_social_sentiment()
st.metric("Sentimen Pasar", f"{s_val}/100", s_txt)
st.info(f"🚀 ENGINE: **{mode_operasi}**")

ph = st.empty(); res_ph = st.empty()

if run_sentinel:
    if "MODE 3" not in mode_operasi and not groq_key:
        st.error("⚠️ Masukkan Groq API Key Dulu!")
    else:
        while True:
            batch = random.sample(WATCHLIST, 5)
            with ph.container():
                st.write(f"Scanning {', '.join(batch)} ...")
                for coin in batch:
                    r = analyze(coin, mode_operasi, s_val, s_txt)
                    time.sleep(0.5) # Groq cepat, delay bisa dikurangi
                    if r:
                        # Audio
                        st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-37.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)
                        with res_ph.container():
                            st.success(f"🚨 **SINYAL: {r['symbol']}**")
                            if "MODE 3" not in mode_operasi:
                                st.warning(f"🤖 **Analisa LLaMA 3:** {r['ai']}")
                            
                            c1, c2 = st.columns(2)
                            c1.metric("Entry", f"${r['entry']:.5f}", f"RSI: {r['rsi']:.1f}")
                            c2.metric("Target", f"${r['tp']:.5f}", f"+{target_pct}%")
                            
                            fig = go.Figure()
                            d = r['df']
                            fig.add_trace(go.Candlestick(x=d.index, open=d['open'], high=d['high'], low=d['low'], close=d['close']))
                            fig.add_trace(go.Scatter(x=d.index, y=d['ema200'], line=dict(color='orange'), name='EMA 200'))
                            st.plotly_chart(fig, use_container_width=True)
                            st.stop()
            time.sleep(3)
else:
    ph.info("Siap Meronda. Masukkan Key & Klik Aktifkan.")
