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
st.set_page_config(page_title="THE ULTIMATE SENTINEL", layout="wide")
st.title("🚨 THE ULTIMATE SENTINEL: Dual Engine + Gemini + Pos Ronda")
st.markdown("""
**Sistem Pertahanan 3 Lapis:**
1.  🔥 **Super Agresif:** Mencari koin hancur (RSI < 25) untuk serok bawah.
2.  🛡️ **Moderat (Akurat):** Mencari koin uptrend (EMA 200) yang sedang diskon.
3.  🤖 **Gemini & Sosmed:** Validasi logika AI Google + Sentimen Pasar (Fear/Greed).
""")

# --- DATABASE KOIN MICIN ---
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
    st.header("🧠 Otak Gemini (Wajib)")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    st.divider()
    st.header("🎛️ Kontrol Pos Ronda")
    run_sentinel = st.checkbox("🔴 AKTIFKAN POS RONDA (AUTO)", value=False)
    
    st.write("---")
    target_pct = st.slider("Target Cuan (%)", 2.0, 50.0, 5.0)
    kurs_usd = st.number_input("Kurs USD", value=16200)

# --- FUNGSI 1: SENTIMEN SOSIAL/INTERNET ---
def get_social_sentiment():
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url)
        data = response.json()
        value = int(data['data'][0]['value'])
        status = data['data'][0]['value_classification']
        return value, status
    except:
        return 50, "Neutral"

# --- FUNGSI 2: ASK GEMINI ---
def ask_gemini(symbol, price, rsi, trend_status, mode, sentiment_text):
    if not gemini_key: return "⚠️ API Key Gemini belum diisi."
    
    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Role: Crypto Expert.
        Coin: {symbol}. Price: ${price}. RSI: {rsi:.1f}. Trend: {trend_status}.
        Market Sentiment (Social Media/News): {sentiment_text}.
        Mode: {mode} (Aggressive/Moderate).
        
        Question: Based on Technicals + Market Sentiment, is this a good buy? 
        Answer YES/NO and give 1 short reason.
        """
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Gemini Error."

# --- FUNGSI 3: GET DATA (ROBUST) ---
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

# --- FUNGSI 4: DUAL ENGINE LOGIC ---
def analyze_dual_engine(symbol, sent_val, sent_text):
    df = get_data(symbol)
    if df is None: return None
    
    close = df['close']
    curr = close.iloc[-1]
    
    df['ema200'] = EMAIndicator(close=close, window=200).ema_indicator()
    df['rsi'] = RSIIndicator(close=close, window=14).rsi()
    
    rsi = df['rsi'].iloc[-1]
    ema200 = df['ema200'].iloc[-1]
    
    trend = "UPTREND" if curr > ema200 else "DOWNTREND"
    
    res = None
    
    # --- ENGINE 1: SUPER AGRESIF (Serok Bawah) ---
    # Jika pasar FEAR (Sentimen < 40), RSI harus < 30.
    # Jika pasar NORMAL, RSI harus < 25 (Lebih ketat).
    limit_rsi = 30 if sent_val < 40 else 25
    
    if rsi < limit_rsi:
        gemini = ask_gemini(symbol, curr, rsi, trend, "AGRESIF", sent_text)
        res = {
            "type": "🔥 SUPER AGRESIF",
            "symbol": symbol,
            "entry": curr,
            "tp": curr * (1 + (target_pct*2)/100), # Target tinggi
            "rsi": rsi,
            "gemini": gemini,
            "df": df
        }
        
    # --- ENGINE 2: MODERAT (Akurat) ---
    # Syarat: Harga > EMA200 DAN RSI < 55
    elif curr > ema200 and rsi < 55:
        gemini = ask_gemini(symbol, curr, rsi, trend, "MODERAT", sent_text)
        res = {
            "type": "🛡️ MODERAT (AMAN)",
            "symbol": symbol,
            "entry": curr,
            "tp": curr * (1 + target_pct/100),
            "rsi": rsi,
            "gemini": gemini,
            "df": df
        }
        
    return res

# --- FUNGSI ALARM ---
def play_alarm():
    audio_html = """<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-37.mp3" type="audio/mpeg"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- UI UTAMA ---
sent_val, sent_text = get_social_sentiment()
st.metric("Sentimen Internet (News/Social)", f"{sent_val}/100", sent_text)

monitor_ph = st.empty()
result_ph = st.empty()

# --- POS RONDA LOOP ---
if run_sentinel:
    if not gemini_key:
        st.error("⚠️ Masukkan API Key Gemini dulu di Sidebar!")
    else:
        while True:
            # Ambil 5 koin acak
            batch = random.sample(WATCHLIST, 5)
            
            with monitor_ph.container():
                st.info(f"🔄 Pos Ronda (Dual Engine) sedang scan: {', '.join(batch)} ...")
                
                for coin in batch:
                    res = analyze_dual_engine(coin, sent_val, sent_text)
                    
                    if res:
                        # KETEMU!
                        play_alarm()
                        
                        with result_ph.container():
                            if "AGRESIF" in res['type']:
                                st.error(f"🚨 {res['type']}: {res['symbol']}")
                            else:
                                st.success(f"🚨 {res['type']}: {res['symbol']}")
                                
                            st.info(f"🧠 **Analisa Gemini:** {res['gemini']}")
                            
                            c1, c2 = st.columns(2)
                            c1.metric("BELI SEKARANG", f"${res['entry']:.6f}", f"Rp {res['entry']*kurs_usd:,.0f}")
                            c2.metric("JUAL NANTI", f"${res['tp']:.6f}")
                            
                            # Grafik
                            fig = go.Figure()
                            df = res['df']
                            fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close']))
                            fig.add_trace(go.Scatter(x=df.index, y=df['ema200'], line=dict(color='orange'), name='EMA 200'))
                            
                            # Kotak Target
                            fig.add_shape(type="rect", x0=df.index[-1], y0=res['entry'], x1=df.index[-1]+timedelta(hours=12), y1=res['tp'], fillcolor="rgba(0,255,0,0.2)", line=dict(width=0))
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.warning("Matikan centang 'Pos Ronda' untuk scan ulang.")
                            st.stop() # Freeze layar
                            
                    time.sleep(1) # Jeda antar koin
            
            # Jeda antar batch biar ga diblokir
            time.sleep(5)

else:
    monitor_ph.info("👈 Centang **'AKTIFKAN POS RONDA'** di menu kiri untuk memulai Auto-Scan 24 Jam.")
