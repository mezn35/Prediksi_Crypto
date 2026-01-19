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
st.set_page_config(page_title="AI MASTER COMMANDER", layout="wide")
st.title("🎛️ AI MASTER COMMANDER: Pilih Senjatamu")

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

# --- SIDEBAR: PILIH SENJATA ---
with st.sidebar:
    st.header("🎮 Pilih Mode AI")
    mode_operasi = st.radio(
        "Mau Jalankan Mode Apa?",
        (
            "🔥 MODE 1: Super Agresif (Gemini)",
            "🧠 MODE 2: Moderat Cerdas (Gemini)",
            "🛡️ MODE 3: Sentinel Klasik (Tanpa AI)"
        )
    )
    
    st.divider()
    
    if "MODE 3" not in mode_operasi:
        st.header("🧠 Kunci Otak Gemini")
        gemini_key = st.text_input("Gemini API Key", type="password")
    else:
        gemini_key = None # Mode 3 tidak butuh Gemini
        st.info("Mode 3 tidak butuh API Key Gemini.")

    st.divider()
    st.header("🎛️ Kontrol")
    run_sentinel = st.checkbox("🔴 AKTIFKAN POS RONDA", value=False)
    target_pct = st.slider("Target Cuan (%)", 2.0, 50.0, 5.0)
    kurs_usd = st.number_input("Kurs USD", value=16200)

# --- FUNGSI 1: SENTIMEN SOSIAL ---
def get_social_sentiment():
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url)
        data = response.json()
        return int(data['data'][0]['value']), data['data'][0]['value_classification']
    except:
        return 50, "Neutral"

# --- FUNGSI 2: ASK GEMINI (DENGAN DETEKSI ERROR) ---
def ask_gemini(symbol, price, rsi, trend_status, mode, sentiment_text):
    if not gemini_key: return "⚠️ API Key Kosong"
    
    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Role: Crypto Sniper. Context: Coin {symbol}, Price ${price}, RSI {rsi:.1f}, Trend {trend_status}.
        Market Sentiment: {sentiment_text}. Mode: {mode}.
        Is this a good entry? Yes/No and why? Short answer.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}" # INI AKAN KASIH TAU ERRORNYA APA

# --- FUNGSI 3: DATA ENGINE ---
def get_data(symbol):
    pair = symbol.replace("/IDR", "/USDT")
    df = None
    source = ""
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
    
    if df is None: # Backup
        try:
            yf_sym = pair.replace("/", "-").replace("USDT", "USD")
            data_yf = yf.download(yf_sym, period='5d', interval='1h', progress=False)
            if len(data_yf) > 20:
                if isinstance(data_yf.columns, pd.MultiIndex): data_yf.columns = data_yf.columns.droplevel(1)
                df = data_yf[['Open', 'High', 'Low', 'Close', 'Volume']]
                df.columns = ['open', 'high', 'low', 'close', 'vol']
                df.index = df.index + timedelta(hours=7)
                source = "Yahoo"
        except: pass
    return df, source

# --- ANALISA UTAMA ---
def analyze_market(symbol, mode_choice, sent_idx, sent_text):
    df, source = get_data(symbol)
    if df is None: return None
    
    close = df['close']
    curr = close.iloc[-1]
    
    df['ema200'] = EMAIndicator(close=close, window=200).ema_indicator()
    df['rsi'] = RSIIndicator(close=close, window=14).rsi()
    
    rsi = df['rsi'].iloc[-1]
    ema200 = df['ema200'].iloc[-1]
    trend = "UPTREND" if curr > ema200 else "DOWNTREND"
    
    res = None
    gemini_msg = "-"
    
    # === LOGIKA MODE 1: SUPER AGRESIF ===
    if "MODE 1" in mode_choice:
        # Syarat: RSI < 35 (Diskon) - Tidak peduli tren
        if rsi < 35:
            gemini_msg = ask_gemini(symbol, curr, rsi, trend, "AGRESIF", sent_text)
            res = {"type": "🔥 AGRESIF", "reason": "RSI Oversold"}

    # === LOGIKA MODE 2: MODERAT CERDAS ===
    elif "MODE 2" in mode_choice:
        # Syarat: Uptrend (Harga > EMA200) + RSI < 55
        if curr > ema200 and rsi < 55:
            gemini_msg = ask_gemini(symbol, curr, rsi, trend, "MODERAT", sent_text)
            res = {"type": "🧠 MODERAT", "reason": "Uptrend + Diskon"}

    # === LOGIKA MODE 3: SENTINEL KLASIK ===
    elif "MODE 3" in mode_choice:
        # Syarat: Uptrend (Harga > EMA200) + RSI < 45 (Lebih ketat)
        # Tanpa Gemini, langsung sinyal
        if curr > ema200 and rsi < 45:
            res = {"type": "🛡️ SENTINEL", "reason": "Pure Technical Uptrend"}
            gemini_msg = "Non-Aktif (Mode Klasik)"

    # JIKA KETEMU HASIL
    if res:
        res.update({
            "symbol": symbol, "entry": curr, 
            "tp": curr * (1 + target_pct/100),
            "rsi": rsi, "gemini": gemini_msg, "df": df, "source": source
        })
        return res
        
    return None

# --- UI UTAMA ---
sent_val, sent_text = get_social_sentiment()
st.metric("Sentimen Pasar", f"{sent_val}/100", sent_text)

# INDIKATOR MODE AKTIF
st.info(f"Sistem Berjalan di: **{mode_operasi}**")

monitor_ph = st.empty()
result_ph = st.empty()

if run_sentinel:
    # Cek Wajib API Key untuk Mode 1 & 2
    if "MODE 3" not in mode_operasi and not gemini_key:
        st.error("⚠️ API Key Gemini WAJIB diisi untuk Mode ini!")
    else:
        while True:
            batch = random.sample(WATCHLIST, 5)
            with monitor_ph.container():
                st.write(f"Scanning ({mode_operasi}): {', '.join(batch)} ...")
                
                for coin in batch:
                    res = analyze_market(coin, mode_operasi, sent_val, sent_text)
                    time.sleep(1)
                    
                    if res:
                        # BUNYIKAN ALARM
                        audio_html = """<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-37.mp3" type="audio/mpeg"></audio>"""
                        st.markdown(audio_html, unsafe_allow_html=True)
                        
                        with result_ph.container():
                            st.success(f"🚨 **SINYAL DITEMUKAN: {res['symbol']}**")
                            st.caption(f"Mode: {res['type']} | Sumber: {res['source']}")
                            
                            # Tampilkan Gemini jika bukan Mode 3
                            if "MODE 3" not in mode_operasi:
                                st.info(f"🤖 **Kata Gemini:** {res['gemini']}")
                            
                            c1, c2 = st.columns(2)
                            c1.metric("BELI", f"${res['entry']:.5f}", f"RSI: {res['rsi']:.1f}")
                            c2.metric("JUAL", f"${res['tp']:.5f}")
                            
                            fig = go.Figure()
                            df = res['df']
                            fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close']))
                            fig.add_trace(go.Scatter(x=df.index, y=df['ema200'], line=dict(color='orange'), name='EMA 200'))
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.stop()
            
            time.sleep(5)
else:
    monitor_ph.info("Pilih Mode di menu kiri, lalu centang **AKTIFKAN POS RONDA**.")
