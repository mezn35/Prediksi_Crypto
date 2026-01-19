import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
import requests
import plotly.graph_objects as go
import google.generativeai as genai
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from datetime import datetime, timedelta
import time
import random

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI DUAL ENGINE PRO", layout="wide")
st.title("🧠 AI DUAL ENGINE: Agresif vs Moderat")
st.markdown("""
**Sistem 2 Jalur:**
1.  🔥 **SUPER AGRESIF:** Mencari koin *Oversold* parah (RSI < 25). Target: Pantulan Cepat (Rebound).
2.  🛡️ **MODERAT (AKURAT):** Mencari koin *Uptrend* yang sedang diskon. Target: Ikut Tren (Follow Trend).
3.  🌐 **Social & Gemini:** Semua sinyal divalidasi oleh Sentimen Internet & Otak AI.
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
    st.header("🧠 Otak Gemini")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    st.divider()
    st.header("🎛️ Kontrol")
    run_sentinel = st.checkbox("🔴 AKTIFKAN POS RONDA", value=False)
    target_pct = st.slider("Target Profit (%)", 2.0, 50.0, 5.0)
    kurs_usd = st.number_input("Kurs USD", value=16200)

# --- FUNGSI SENTIMEN SOSIAL ---
def get_social_sentiment():
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url)
        data = response.json()
        return int(data['data'][0]['value']), data['data'][0]['value_classification']
    except:
        return 50, "Neutral"

# --- FUNGSI GEMINI (DUAL MODE) ---
def ask_gemini(symbol, price, rsi, trend_status, mode, sentiment_text):
    if not gemini_key: return "⚠️ Pasang API Key dulu."
    
    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        if mode == "AGRESIF":
            prompt = f"""
            Role: Crypto Sniper.
            Context: Analyzing {symbol}. Market Sentiment is {sentiment_text}.
            Data: Price ${price}, RSI {rsi:.1f} (Very Low), Trend: {trend_status}.
            
            Question: This is a falling knife / heavy dip. Is this a potential REBOUND/BOUNCE opportunity?
            Answer YES or NO first, then explain risk (High/Extreme). Be brief.
            """
        else: # MODERAT
            prompt = f"""
            Role: Conservative Trader.
            Context: Analyzing {symbol}. Market Sentiment is {sentiment_text}.
            Data: Price ${price}, RSI {rsi:.1f}, Trend: {trend_status}.
            
            Question: Is this a healthy dip in an uptrend? Is it safe to enter?
            Answer YES or NO first. Be brief.
            """
            
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Gemini Error."

# --- FUNGSI DATA ---
def get_data(symbol):
    pair = symbol.replace("/IDR", "/USDT")
    df = None
    for name, exc in exchanges.items():
        try:
            bars = exc.fetch_ohlcv(pair, timeframe='1h', limit=100)
            if bars:
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
                df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
                df.set_index('time', inplace=True)
                break
        except: continue
        
    if df is None: # Backup Yahoo
        try:
            yf_sym = pair.replace("/", "-").replace("USDT", "USD")
            data_yf = yf.download(yf_sym, period='5d', interval='1h', progress=False)
            if len(data_yf) > 20:
                if isinstance(data_yf.columns, pd.MultiIndex): data_yf.columns = data_yf.columns.droplevel(1)
                df = data_yf[['Open', 'High', 'Low', 'Close', 'Volume']]
                df.columns = ['open', 'high', 'low', 'close', 'vol']
                df.index = df.index + timedelta(hours=7)
        except: pass
    return df

# --- CORE LOGIC: DUAL ENGINE ---
def analyze_dual_engine(symbol, sent_idx, sent_text):
    df = get_data(symbol)
    if df is None: return None
    
    close = df['close']
    curr = close.iloc[-1]
    
    df['ema200'] = EMAIndicator(close=close, window=200).ema_indicator()
    df['rsi'] = RSIIndicator(close=close, window=14).rsi()
    
    rsi = df['rsi'].iloc[-1]
    ema200 = df['ema200'].iloc[-1]
    
    trend_status = "UPTREND" if curr > ema200 else "DOWNTREND"
    
    result = None
    
    # --- MESIN 1: SUPER AGRESIF (Cari Pantulan/Rebound) ---
    # Syarat: RSI Hancur (< 30) atau (< 35 jika pasar Fear)
    limit_rsi = 35 if sent_idx < 40 else 30
    
    if rsi < limit_rsi:
        gemini_says = ask_gemini(symbol, curr, rsi, trend_status, "AGRESIF", sent_text)
        result = {
            "type": "🔥 AGRESIF",
            "symbol": symbol,
            "entry": curr,
            "tp": curr * (1 + (target_pct*2)/100), # Target profit lebih besar krn risiko besar
            "rsi": rsi,
            "gemini": gemini_says,
            "df": df
        }
        
    # --- MESIN 2: MODERAT (Cari Tren Aman) ---
    # Syarat: Harga > EMA200 DAN RSI < 55 (Koreksi Wajar)
    elif curr > ema200 and rsi < 55:
        gemini_says = ask_gemini(symbol, curr, rsi, trend_status, "MODERAT", sent_text)
        result = {
            "type": "🛡️ MODERAT",
            "symbol": symbol,
            "entry": curr,
            "tp": curr * (1 + target_pct/100),
            "rsi": rsi,
            "gemini": gemini_says,
            "df": df
        }
        
    return result

# --- UI TAMPILAN ---
sent_val, sent_text = get_social_sentiment()
st.metric("Sentimen Sosial (Fear/Greed)", f"{sent_val}/100", sent_text)

# Tabs untuk memisahkan hasil
tab1, tab2 = st.tabs(["🔥 HASIL SUPER AGRESIF", "🛡️ HASIL MODERAT"])

monitor_text = st.empty()

if run_sentinel:
    if not gemini_key:
        st.error("⚠️ Masukkan API Key Gemini dulu di menu kiri!")
    else:
        while True:
            batch = random.sample(WATCHLIST, 5)
            with monitor_text.container():
                st.info(f"Scanning Dual Engine: {', '.join(batch)} ...")
                
                for coin in batch:
                    res = analyze_dual_engine(coin, sent_val, sent_text)
                    time.sleep(1) # Jeda manusia
                    
                    if res:
                        # BUNYIKAN ALARM
                        audio_html = """<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-37.mp3" type="audio/mpeg"></audio>"""
                        st.markdown(audio_html, unsafe_allow_html=True)
                        
                        # TAMPILKAN DI TAB YANG SESUAI
                        if "AGRESIF" in res['type']:
                            with tab1:
                                st.success(f"🚨 **DITEMUKAN: {res['symbol']}**")
                                st.warning(f"🤖 Gemini: {res['gemini']}")
                                st.metric("Harga Entry (Serok)", f"${res['entry']:.5f}", f"RSI: {res['rsi']:.1f}")
                                
                                fig = go.Figure()
                                fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['open'], high=res['df']['high'], low=res['df']['low'], close=res['df']['close']))
                                st.plotly_chart(fig, use_container_width=True)
                                
                        else:
                            with tab2:
                                st.success(f"✅ **DITEMUKAN: {res['symbol']}**")
                                st.info(f"🤖 Gemini: {res['gemini']}")
                                st.metric("Harga Entry (Aman)", f"${res['entry']:.5f}", f"RSI: {res['rsi']:.1f}")
                                
                                fig = go.Figure()
                                fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['open'], high=res['df']['high'], low=res['df']['low'], close=res['df']['close']))
                                fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['ema200'], line=dict(color='orange'), name='EMA 200'))
                                st.plotly_chart(fig, use_container_width=True)
                        
                        st.stop() # Berhenti jika ketemu
            
            time.sleep(5) # Istirahat antar batch

else:
    monitor_text.info("Centang **AKTIFKAN POS RONDA** untuk menyalakan Dua Mesin sekaligus.")
