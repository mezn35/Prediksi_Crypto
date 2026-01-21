import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
import requests
import plotly.graph_objects as go
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from datetime import datetime, timedelta
import time
import random

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="CRYPTO COMMANDER PRO", layout="wide")
st.title("🛡️ CRYPTO COMMANDER: Paket Lengkap (No Error)")

# --- DATABASE KOIN (FULL LIST) ---
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
    'tokocrypto': ccxt.tokocrypto({'enableRateLimit': True}),
}

# --- SIDEBAR: SEMUA KONTROL ADA DI SINI ---
with st.sidebar:
    # 1. USDT RADAR
    st.header("🇮🇩 USDT RADAR")
    usdt_placeholder = st.empty()
    
    st.divider()

    # 2. STRATEGI SELECTOR (FITUR LAMA DIKEMBALIKAN)
    st.header("🎮 MODE STRATEGI")
    mode_operasi = st.radio(
        "Pilih Gaya Trading:",
        (
            "🔥 AGRESIF (Serok Bawah/Rebound)",
            "🧠 MODERAT (Tren Sehat)",
            "🛡️ KONSERVATIF (Super Aman)"
        )
    )

    st.divider()
    
    # 3. MONEY MANAGEMENT
    st.header("💰 MANAJEMEN RISIKO")
    saldo_usdt = st.number_input("Total Saldo USDT", value=100.0, step=10.0)
    resiko_persen = st.slider("Risiko per Trade (%)", 1.0, 10.0, 2.0)
    st.info(f"Maksimal Rugi: **${saldo_usdt * resiko_persen / 100:.2f}**")
    
    st.divider()
    
    # 4. START BUTTON
    st.header("🎛️ KONTROL")
    run_sentinel = st.checkbox("🔴 AKTIFKAN POS RONDA", value=False)
    target_pct = st.slider("Target Profit (%)", 2.0, 50.0, 5.0)

# --- FUNGSI 1: CEK SENTIMEN (EXTERNAL DATA) ---
def get_social_sentiment():
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url, timeout=5)
        data = response.json()
        return int(data['data'][0]['value']), data['data'][0]['value_classification']
    except:
        return 50, "Neutral"

# --- FUNGSI 2: CEK USDT (TOKO) ---
def check_usdt_rate():
    try:
        ticker = exchanges['tokocrypto'].fetch_ticker('USDT/BIDR')
        current_price = ticker['last']
        
        # Analisa BB
        bars = exchanges['tokocrypto'].fetch_ohlcv('USDT/BIDR', timeframe='4h', limit=50)
        df = pd.DataFrame(bars, columns=['time','open','high','low','close','vol'])
        
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_low'] = bb.bollinger_lband()
        df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
        
        status = "NETRAL (WAIT)"; color = "orange"
        if current_price <= df['bb_low'].iloc[-1] or df['rsi'].iloc[-1] < 40:
            status = "✅ DISKON (BUY)"; color = "green"
        elif df['rsi'].iloc[-1] > 65:
            status = "⛔ MAHAL (DONT BUY)"; color = "red"
            
        return current_price, status, color
    except:
        return 16200, "Offline", "grey"

# --- FUNGSI 3: DATA ENGINE ---
def get_data(symbol):
    pair = symbol.replace("/IDR", "/USDT")
    df = None; source = ""
    for name, exc in exchanges.items():
        if name == 'tokocrypto': continue
        try:
            bars = exc.fetch_ohlcv(pair, timeframe='1h', limit=100)
            if bars:
                df = pd.DataFrame(bars, columns=['time','open','high','low','close','vol'])
                df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
                df.set_index('time', inplace=True)
                source = name.upper(); break
        except: continue
    
    # Fallback Yahoo
    if df is None:
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

# --- FUNGSI 4: MONEY MANAGER ---
def calculate_position(entry, sl, equity, risk):
    risk_amt = equity * (risk / 100)
    dist = abs(entry - sl) / entry
    if dist == 0: return 0
    size = risk_amt / dist
    if size > (equity * 0.5): size = equity * 0.5 # Max 50% saldo
    return size

# --- CORE LOGIC: ANALISA MATEMATIKA (3 MODE) ---
def analyze_market(symbol, mode):
    df, src = get_data(symbol)
    if df is None: return None
    
    close = df['close']; curr = close.iloc[-1]
    
    # Indikator
    df['ema200'] = EMAIndicator(close, window=200).ema_indicator()
    df['ema50'] = EMAIndicator(close, window=50).ema_indicator()
    df['rsi'] = RSIIndicator(close, window=14).rsi()
    
    rsi = df['rsi'].iloc[-1]
    ema200 = df['ema200'].iloc[-1]
    ema50 = df['ema50'].iloc[-1]
    
    signal = False
    reason = ""
    
    # === LOGIKA 1: AGRESIF (Serok Bawah) ===
    if "AGRESIF" in mode:
        # Cari yang oversold parah (RSI < 30) tanpa peduli tren
        if rsi < 30:
            signal = True
            reason = f"RSI Oversold Ekstrem ({rsi:.1f})"

    # === LOGIKA 2: MODERAT (Tren Sehat) ===
    elif "MODERAT" in mode:
        # Uptrend (Harga > EMA200) + Diskon (RSI < 55)
        if curr > ema200 and rsi < 55:
            signal = True
            reason = "Uptrend + Koreksi Wajar"

    # === LOGIKA 3: KONSERVATIF (Super Aman) ===
    elif "KONSERVATIF" in mode:
        # Strong Uptrend (Harga > EMA200 & EMA50) + RSI Murah (< 45)
        if curr > ema200 and curr > ema50 and rsi < 45:
            signal = True
            reason = "Strong Uptrend Perfect Setup"

    if signal:
        sl_price = curr * 0.95 # SL 5%
        size = calculate_position(curr, sl_price, saldo_usdt, resiko_persen)
        
        # Volume Warning
        vol_usdt = (df['vol'] * df['close']).rolling(24).sum().iloc[-1]
        warn = ""
        if size > (vol_usdt * 0.01):
            size = vol_usdt * 0.01
            warn = "⚠️ Volume Kecil! Size dikurangi."

        return {
            "symbol": symbol, "entry": curr, "sl": sl_price, "tp": curr*(1+target_pct/100),
            "size": size, "src": src, "df": df, "reason": reason, "warn": warn
        }
    return None

# --- TAMPILAN UTAMA ---
s_val, s_txt = get_social_sentiment()
st.metric("Sentimen Pasar (Fear & Greed)", f"{s_val}/100", s_txt)
st.info(f"🚀 MODE AKTIF: **{mode_operasi}**")

ph = st.empty(); res_ph = st.empty()

if run_sentinel:
    while True:
        # 1. Update USDT Radar
        u_price, u_stat, u_col = check_usdt_rate()
        with usdt_placeholder.container():
            st.metric("Kurs USDT (Toko)", f"Rp {u_price:,.0f}")
            if u_col == "green": st.success(u_stat)
            elif u_col == "red": st.error(u_stat)
            else: st.warning(u_stat)
        
        # 2. Scanning
        batch = random.sample(WATCHLIST, 5)
        with ph.container():
            st.write(f"Scanning ({mode_operasi}): {', '.join(batch)} ...")
            
            for coin in batch:
                res = analyze_market(coin, mode_operasi)
                time.sleep(0.5)
                
                if res:
                    st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-37.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)
                    with res_ph.container():
                        st.success(f"💎 **SINYAL: {res['symbol']}**")
                        st.caption(f"Alasan: {res['reason']} | Sumber: {res['src']}")
                        if res['warn']: st.warning(res['warn'])
                        
                        # Money Management Display
                        c1, c2, c3 = st.columns(3)
                        c1.metric("💵 BELI (USDT)", f"${res['size']:.2f}")
                        c2.metric("🎯 ENTRY", f"${res['entry']:.5f}")
                        c3.metric("🛑 STOP LOSS", f"${res['sl']:.5f}")
                        
                        # Layering Strategy
                        with st.expander("📉 Strategi Jaring (Layering)"):
                            c_a, c_b = st.columns(2)
                            c_a.info(f"**Jaring 1 (Market)**: ${res['size']*0.4:.2f}")
                            c_b.warning(f"**Jaring 2 (-3%)**: ${res['size']*0.6:.2f}")
                            st.caption("Pasang antrian di dua harga ini untuk hasil maksimal.")

                        # Chart
                        fig = go.Figure()
                        d = res['df']
                        fig.add_trace(go.Candlestick(x=d.index, open=d['open'], high=d['high'], low=d['low'], close=d['close']))
                        fig.add_trace(go.Scatter(x=d.index, y=d['ema200'], line=dict(color='orange'), name='EMA 200'))
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.stop() # Freeze layar
        time.sleep(3)
else:
    ph.info("Siap! Atur Saldo & Mode, lalu klik 'Aktifkan Pos Ronda'.")
    # Preview USDT saat standby
    u_price, u_stat, u_col = check_usdt_rate()
    with usdt_placeholder.container():
        st.metric("Kurs USDT", f"Rp {u_price:,.0f}")
        st.caption(u_stat)
