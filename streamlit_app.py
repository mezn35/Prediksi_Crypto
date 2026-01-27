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
st.title("🛡️ CRYPTO COMMANDER: Smart Exit Strategy")

# --- DATABASE KOIN ---
WATCHLIST = [
    "PUMP/USDT", "AXL/USDT", "SXP/USDT", "HEMI/USDT", "TURTLE/USDT", "LISTA/USDT",
    "HEI/USDT", "BROCCOLI714/USDT", "PENGU/USDT", "BIO/USDT", "A2Z/USDT", 
    "VELODROME/USDT", "1000CHEEMS/USDT", "MDT/USDT", "ACA/USDT", 
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

# --- SIDEBAR ---
with st.sidebar:
    st.header("🇮🇩 USDT RADAR")
    usdt_placeholder = st.empty()
    st.divider()

    st.header("🎮 PILIH STRATEGI")
    mode_operasi = st.radio(
        "Gaya Trading:",
        (
            "🚀 MOMENTUM (Kejar Pump)", # <-- INI BUAT MENANGKAP PUMP
            "🔥 AGRESIF (Serok Bawah)",
            "🧠 MODERAT (Tren Sehat)"
        )
    )
    if "MOMENTUM" in mode_operasi:
        st.info("ℹ️ Mode ini mencari koin yg sedang naik 5-20%. Targetnya bisa 100%!")

    st.divider()
    
    st.header("💰 MANAJEMEN UANG")
    saldo_usdt = st.number_input("Saldo USDT", value=100.0, step=10.0)
    resiko_persen = st.slider("Risiko Rugi (%)", 1.0, 5.0, 2.0)
    
    st.divider()
    
    st.header("🎛️ KONTROL")
    run_sentinel = st.checkbox("🔴 AKTIFKAN SCANNER", value=False)
    # SLIDER TARGET PROFIT (TP AKHIR)
    target_pct = st.slider("Target 'Moonbag' (%)", 10.0, 200.0, 50.0)

# --- FUNGSI CEK USDT ---
def check_usdt_rate():
    try:
        ticker = exchanges['tokocrypto'].fetch_ticker('USDT/BIDR')
        current_price = ticker['last']
        return current_price
    except: return 16200

# --- FUNGSI DATA ---
def get_data(symbol):
    pair = symbol.replace("/IDR", "/USDT")
    df = None; source = ""
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
    return df, source

# --- FUNGSI MONEY MANAGER ---
def calculate_position(entry, sl, equity, risk):
    risk_amt = equity * (risk / 100)
    dist = abs(entry - sl) / entry
    if dist == 0: return 0
    size = risk_amt / dist
    if size > (equity * 0.5): size = equity * 0.5
    return size

# --- ANALISA UTAMA ---
def analyze_market(symbol, mode):
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
    
    # === LOGIKA PENCARIAN ===
    if "MOMENTUM" in mode:
        # Cari yg lagi naik daun (Tren pendek naik + RSI kuat tapi belum 85)
        if curr > ema20 and 50 < rsi < 85:
            if close.iloc[-1] > df['open'].iloc[-1]: # Candle hijau
                signal = True
                reason = f"🚀 Momentum Naik! RSI: {rsi:.1f}"

    elif "AGRESIF" in mode:
        if rsi < 30: # Cari diskon
            signal = True
            reason = f"📉 Oversold ({rsi:.1f})"

    elif "MODERAT" in mode:
        if ema200 > 0 and curr > ema200 and rsi < 55:
            signal = True
            reason = "✅ Tren Sehat"

    if signal:
        # HITUNG STOP LOSS
        sl_pct = 0.96 if "MOMENTUM" in mode else 0.95
        sl_price = curr * sl_pct
        
        # HITUNG SIZE
        size = calculate_position(curr, sl_price, saldo_usdt, resiko_persen)
        vol_usdt = (df['vol'] * df['close']).rolling(24).sum().iloc[-1]
        if size > (vol_usdt * 0.01): size = vol_usdt * 0.01 # Safety Volume

        # HITUNG TARGET JUAL (SMART EXIT)
        # TP1 (Aman): Entry + Jarak Risk (Ratio 1:1)
        risk_dist = curr - sl_price
        tp1 = curr + risk_dist       # 1:1 (Biasanya 3-5%)
        tp2 = curr + (risk_dist * 2) # 1:2 (Biasanya 8-10%)
        tp3 = curr * (1 + target_pct/100) # Target Moonbag user

        # STRATEGI JARING (BELI)
        layers = []
        if "MOMENTUM" in mode:
            layers.append({"step": "Jaring 1 (Market)", "type": "Market", "amount": size*0.5, "price": "Sekarang"})
            layers.append({"step": "Jaring 2 (Support)", "type": "Limit", "amount": size*0.5, "price": curr*0.99})
        else:
            layers.append({"step": "Jaring 1 (Market)", "type": "Market", "amount": size*0.3, "price": "Sekarang"})
            layers.append({"step": "Jaring 2 (Bawah)", "type": "Limit", "amount": size*0.7, "price": curr*0.96})

        return {
            "symbol": symbol, "entry": curr, "sl": sl_price,
            "tp1": tp1, "tp2": tp2, "tp3": tp3,
            "size": size, "src": src, "df": df, "reason": reason, "layers": layers
        }
    return None

# --- UI LOOP ---
ph = st.empty(); res_ph = st.empty()

if run_sentinel:
    while True:
        u_price = check_usdt_rate()
        with usdt_placeholder.container():
            st.metric("Kurs USDT (Toko)", f"Rp {u_price:,.0f}")
        
        batch = random.sample(WATCHLIST, 8)
        with ph.container():
            st.write(f"Scanning ({mode_operasi}): {', '.join(batch)} ...")
            for coin in batch:
                res = analyze_market(coin, mode_operasi)
                time.sleep(0.1)
                if res:
                    st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-37.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)
                    with res_ph.container():
                        st.success(f"💎 **SINYAL: {res['symbol']}**")
                        st.caption(f"Reason: {res['reason']} | Src: {res['src']}")
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("BELI (USDT)", f"${res['size']:.2f}")
                        c2.metric("ENTRY", f"${res['entry']:.5f}")
                        c3.metric("STOP LOSS", f"${res['sl']:.5f}")
                        
                        # --- FITUR BARU: TABEL JUAL PINTAR ---
                        st.info("🎯 **TARGET JUAL (SMART EXIT STRATEGY)**")
                        col_t1, col_t2, col_t3 = st.columns(3)
                        col_t1.write(f"**TP 1 (Aman)**\n${res['tp1']:.5f}\n*(Jual 50%)*")
                        col_t2.write(f"**TP 2 (Cuan)**\n${res['tp2']:.5f}\n*(Jual 30%)*")
                        col_t3.write(f"**TP 3 (Moon)**\n${res['tp3']:.5f}\n*(Hold Sisa)*")
                        
                        with st.expander("📋 Instruksi Beli (Klik untuk lihat)"):
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
                        st.stop()
        time.sleep(1)
else:
    ph.info("Pilih Strategi -> Klik Aktifkan.")
