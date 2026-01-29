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
st.set_page_config(page_title="Prediksi Crypto", layout="wide")
st.title("🛡️ Prediksi Crypto")

# --- DATABASE KOIN (LENGKAP) ---
WATCHLIST = [
    "PUMP/USDT", "AXL/USDT", "SXP/USDT", "HEMI/USDT", "TURTLE/USDT", "LISTA/USDT",
    "HEI/USDT", "BROCCOLI714/USDT", "PENGU/USDT", "BIO/USDT", "A2Z/USDT", 
    "VELODROME/USDT", "1000CHEEMS/USDT", "MDT/USDT", "ACA/USDT", "XRP/USDT",
    "COS/USDT", "ACM/USDT", "CHESS/USDT", "DATA/USDT", "NBT/USDT", "CVC/USDT", 
    "ALPINE/USDT", "BEL/USDT", "HOOK/USDT", "NKN/USDT", "QUICK/USDT", "DEGO/USDT", 
    "D/USDT", "IDEX/USDT", "GHST/USDT", "UTK/USDT", "FIO/USDT", "TRU/USDT", 
    "ENSO/USDT", "RDNT/USDT", "MITO/USDT", "DODO/USDT", "BAR/USDT", "VIC/USDT", 
    "EDEN/USDT", "SYN/USDT", "DF/USDT", "TST/USDT", "TKO/USDT", "WAN/USDT", 
    "HAEDAL/USDT", "NFP/USDT", "ADX/USDT", "BMT/USDT", "GTC/USDT", "TUT/USDT", 
    "TREE/USDT", "INIT/USDT", "SHELL/USDT", "PORTAL/USDT", "PIVX/USDT", 
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

# --- SIDEBAR: KONTROL ---
with st.sidebar:
    st.header("🔍 CEK KOIN MANUAL")
    manual_coin = st.text_input("Ketik Simbol (Cth: BTC/USDT)", "").upper()
    btn_manual = st.button("Analisa Koin Ini")
    
    st.divider()
    
    st.header("🇮🇩 USDT RADAR")
    usdt_placeholder = st.empty()
    
    st.divider()

    st.header("🎮 MODE STRATEGI")
    mode_operasi = st.radio(
        "Pilih Gaya Trading:",
        (
            "🚀 MOMENTUM (Kejar Pump)", 
            "🔥 AGRESIF (Serok Bawah)",
            "🧠 MODERAT (Tren Sehat)",
            "🛡️ KONSERVATIF (Super Aman)"
        )
    )

    st.divider()
    
    st.header("💰 MANAJEMEN UANG")
    saldo_usdt = st.number_input("Saldo USDT", value=100.0, step=10.0)
    resiko_persen = st.slider("Risiko Rugi per Trade (%)", 1.0, 5.0, 2.0)
    
    st.divider()
    
    st.header("🎛️ SCANNER OTOMATIS")
    run_sentinel = st.checkbox("🔴 AKTIFKAN AUTO-SCAN", value=False)
    target_pct = st.slider("Target 'Moonbag' (%)", 10.0, 200.0, 50.0)

# --- FUNGSI 1: CEK SENTIMEN ---
def get_social_sentiment():
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url, timeout=5)
        data = response.json()
        return int(data['data'][0]['value']), data['data'][0]['value_classification']
    except:
        return 50, "Neutral"

# --- FUNGSI 2: CEK USDT ---
def check_usdt_rate():
    try:
        ticker = exchanges['tokocrypto'].fetch_ticker('USDT/BIDR')
        current_price = ticker['last']
        bars = exchanges['tokocrypto'].fetch_ohlcv('USDT/BIDR', timeframe='4h', limit=50)
        df = pd.DataFrame(bars, columns=['time','open','high','low','close','vol'])
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_low'] = bb.bollinger_lband()
        df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
        status = "NETRAL (WAIT)"; color = "orange"
        if current_price <= df['bb_low'].iloc[-1] or df['rsi'].iloc[-1] < 40:
            status = "✅ DISKON (BUY)"; color = "green"
        elif df['rsi'].iloc[-1] > 65:
            status = "⛔ MAHAL (HOLD)"; color = "red"
        return current_price, status, color
    except: return 16200, "Offline", "grey"

# --- FUNGSI 3: DATA ENGINE ---
def get_data(symbol):
    pair = symbol.replace("/IDR", "/USDT")
    df = None; source = ""
    # Prioritas Exchange
    priority = ['gateio', 'mexc', 'binance']
    for name in priority:
        exc = exchanges[name]
        try:
            bars = exc.fetch_ohlcv(pair, timeframe='1h', limit=100)
            if bars and len(bars) > 20:
                df = pd.DataFrame(bars, columns=['time','open','high','low','close','vol'])
                df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
                df.set_index('time', inplace=True)
                source = name.upper()
                break
        except: continue
    
    if df is None: # Fallback Yahoo
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
    if size > (equity * 0.5): size = equity * 0.5
    return size

# --- ANALISA UTAMA ---
def analyze_market(symbol, mode, manual_check=False):
    df, src = get_data(symbol)
    if df is None: return None
    
    close = df['close']; curr = close.iloc[-1]
    df['ema20'] = EMAIndicator(close, window=20).ema_indicator()
    df['ema200'] = EMAIndicator(close, window=200).ema_indicator()
    df['rsi'] = RSIIndicator(close, window=14).rsi()
    
    rsi = df['rsi'].iloc[-1]
    ema20 = df['ema20'].iloc[-1]
    ema200 = df['ema200'].iloc[-1] if len(df) > 200 else 0
    
    signal = False; reason = ""
    
    # LOGIKA MANUAL: Kalau user ketik sendiri, selalu tampilkan datanya
    if manual_check:
        signal = True
        reason = f"Analisa Manual (RSI: {rsi:.1f})"
    else:
        # LOGIKA OTOMATIS (FILTER)
        if "MOMENTUM" in mode:
            if curr > ema20 and 50 < rsi < 90 and close.iloc[-1] > df['open'].iloc[-1]:
                signal = True; reason = f"🚀 Momentum Naik! RSI: {rsi:.1f}"
        elif "AGRESIF" in mode:
            if rsi < 30: 
                signal = True; reason = f"📉 Oversold ({rsi:.1f})"
        elif "MODERAT" in mode:
            if ema200 > 0 and curr > ema200 and rsi < 55:
                signal = True; reason = "✅ Tren Sehat"
        elif "KONSERVATIF" in mode:
            if curr > ema200 and curr > df['ema20'].iloc[-1] and rsi < 45:
                signal = True; reason = "🛡️ Setup Perfect"

    if signal:
        sl_pct = 0.96 if "MOMENTUM" in mode else 0.95
        sl_price = curr * sl_pct
        size = calculate_position(curr, sl_price, saldo_usdt, resiko_persen)
        
        # Smart Exit
        risk_dist = curr - sl_price
        tp1 = curr + risk_dist
        tp2 = curr + (risk_dist * 2)
        tp3 = curr * (1 + target_pct/100)

        # Layering
        layers = []
        if "MOMENTUM" in mode:
            layers.append({"step": "Jaring 1", "type": "Market", "amount": size*0.5, "price": "Sekarang"})
            layers.append({"step": "Jaring 2", "type": "Limit", "amount": size*0.5, "price": curr*0.99})
        else:
            layers.append({"step": "Jaring 1", "type": "Market", "amount": size*0.3, "price": "Sekarang"})
            layers.append({"step": "Jaring 2", "type": "Limit", "amount": size*0.7, "price": curr*0.96})

        return {
            "symbol": symbol, "entry": curr, "sl": sl_price,
            "tp1": tp1, "tp2": tp2, "tp3": tp3,
            "size": size, "src": src, "df": df, "reason": reason, "layers": layers, "rsi": rsi
        }
    return None

# --- UI VISUALIZATION HELPER ---
def show_result(res):
    st.success(f"💎 **HASIL ANALISA: {res['symbol']}**")
    st.caption(f"Status: {res['reason']} | Sumber: {res['src']}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("BELI (USDT)", f"${res['size']:.2f}")
    c2.metric("ENTRY", f"${res['entry']:.5f}")
    c3.metric("STOP LOSS", f"${res['sl']:.5f}")
    
    st.info("🎯 **TARGET JUAL (SMART EXIT)**")
    col_t1, col_t2, col_t3 = st.columns(3)
    col_t1.write(f"**TP 1 (Aman)**\n${res['tp1']:.5f}\n*(Jual 50%)*")
    col_t2.write(f"**TP 2 (Cuan)**\n${res['tp2']:.5f}\n*(Jual 30%)*")
    col_t3.write(f"**TP 3 (Moon)**\n${res['tp3']:.5f}\n*(Hold Sisa)*")
    
    with st.expander("📋 Instruksi Beli (Layering)"):
        for l in res['layers']:
            if l['type'] == "Market":
                st.write(f"✅ **{l['step']}**: Beli **${l['amount']:.2f}** (Market)")
            else:
                st.write(f"⏳ **{l['step']}**: Limit Buy **${l['amount']:.2f}** @ **${l['price']:.5f}**")
    
    fig = go.Figure()
    d = res['df']
    fig.add_trace(go.Candlestick(x=d.index, open=d['open'], high=d['high'], low=d['low'], close=d['close']))
    fig.add_trace(go.Scatter(x=d.index, y=d['ema20'], line=dict(color='cyan'), name='EMA 20'))
    st.plotly_chart(fig, use_container_width=True)

# --- BAGIAN UTAMA (MAIN LOOP) ---
s_val, s_txt = get_social_sentiment()
st.metric("Sentimen Global (Fear/Greed)", f"{s_val}/100", s_txt)

# 1. FITUR MANUAL CHECK (DIPRIORITASKAN)
if btn_manual and manual_coin:
    st.divider()
    st.subheader(f"🔎 Analisa Manual: {manual_coin}")
    with st.spinner("Sedang menganalisa..."):
        res_man = analyze_market(manual_coin, mode_operasi, manual_check=True)
        if res_man:
            show_result(res_man)
        else:
            st.error("Koin tidak ditemukan atau data belum tersedia.")

st.divider()

# 2. FITUR AUTO SCANNER
ph = st.empty()

if run_sentinel:
    while True:
        # Update USDT Radar
        u_price, u_stat, u_col = check_usdt_rate()
        with usdt_placeholder.container():
            st.metric("Kurs USDT (Toko)", f"Rp {u_price:,.0f}")
            if u_col == "green": st.success(u_stat)
            elif u_col == "red": st.error(u_stat)
            else: st.warning(u_stat)
        
        # Scan Random Batch
        batch = random.sample(WATCHLIST, 8)
        with ph.container():
            st.info(f"🔄 Scanning ({mode_operasi}): {', '.join(batch)} ...")
            for coin in batch:
                res = analyze_market(coin, mode_operasi)
                time.sleep(0.1)
                if res:
                    st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-37.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)
                    show_result(res)
                    st.stop() # Stop biar user bisa baca
        time.sleep(1)
else:
    ph.info("Pilih Strategi di Kiri -> Klik Aktifkan Auto-Scan.")
    # Preview USDT saat standby
    u_price, u_stat, u_col = check_usdt_rate()
    with usdt_placeholder.container():
        st.metric("Kurs USDT", f"Rp {u_price:,.0f}")
        st.caption(u_stat)
