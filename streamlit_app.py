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
st.title("🛡️ CRYPTO COMMANDER: Multi-Strategy")

# --- DATABASE KOIN (UPDATE LENGKAP) ---
# Saya tambahkan koin-koin dari screenshot Bapak (PUMP, AXL, SXP, HEMI, TURTLE)
WATCHLIST = [
    "PUMP/USDT", "AXL/USDT", "SXP/USDT", "HEMI/USDT", "TURTLE/USDT",
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
    # MODE 4 DITAMBAHKAN UNTUK MENANGKAP KOIN PUMPING
    mode_operasi = st.radio(
        "Gaya Trading:",
        (
            "🚀 MOMENTUM (Kejar Naik/Hype)", # <-- PILIH INI KALAU PASAR HIJAU
            "🔥 AGRESIF (Serok Bawah)",
            "🧠 MODERAT (Tren Sehat)",
            "🛡️ KONSERVATIF (Super Aman)"
        )
    )
    st.caption("ℹ️ Pilih 'MOMENTUM' untuk menangkap koin yang sedang naik +5% s/d +15%.")

    st.divider()
    
    st.header("💰 MANAJEMEN UANG")
    saldo_usdt = st.number_input("Saldo USDT", value=100.0, step=10.0)
    resiko_persen = st.slider("Risiko Rugi (%)", 1.0, 5.0, 2.0)
    st.info(f"Maksimal Rugi per Trade: **${saldo_usdt * resiko_persen / 100:.2f}**")
    
    st.divider()
    
    st.header("🎛️ KONTROL")
    run_sentinel = st.checkbox("🔴 AKTIFKAN POS RONDA", value=False)
    target_pct = st.slider("Target Profit (%)", 2.0, 50.0, 5.0)

# --- FUNGSI CEK USDT ---
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

# --- FUNGSI DATA ---
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

# --- FUNGSI MONEY MANAGER ---
def calculate_position(entry, sl, equity, risk):
    risk_amt = equity * (risk / 100)
    dist = abs(entry - sl) / entry
    if dist == 0: return 0
    size = risk_amt / dist
    if size > (equity * 0.5): size = equity * 0.5
    return size

# --- ANALISA UTAMA (4 MODE) ---
def analyze_market(symbol, mode):
    df, src = get_data(symbol)
    if df is None: return None
    
    close = df['close']; curr = close.iloc[-1]
    df['ema200'] = EMAIndicator(close, window=200).ema_indicator()
    df['ema50'] = EMAIndicator(close, window=50).ema_indicator()
    df['rsi'] = RSIIndicator(close, window=14).rsi()
    
    rsi = df['rsi'].iloc[-1]
    ema200 = df['ema200'].iloc[-1]
    ema50 = df['ema50'].iloc[-1]
    
    signal = False; reason = ""
    
    # === MODE 1: MOMENTUM (KEJAR KERETA/PUMP) ===
    # Ini yang Bapak cari untuk koin +10% s/d +20%
    if "MOMENTUM" in mode:
        # Syarat: Harga > EMA200 (Wajib Uptrend)
        # RSI > 50 (Tenaga Beli Kuat) TAPI RSI < 80 (Belum mentok banget)
        if curr > ema200 and 50 < rsi < 80:
            # Cek candle terakhir hijau tebal?
            if close.iloc[-1] > df['open'].iloc[-1]: 
                signal = True
                reason = f"🚀 Momentum Kuat! RSI: {rsi:.1f} (Lagi Ngegas)"

    # === MODE 2: AGRESIF (SEROK BAWAH) ===
    elif "AGRESIF" in mode:
        if rsi < 30: # Oversold parah
            signal = True
            reason = f"📉 Oversold Ekstrem ({rsi:.1f}) - Potensi Mantul"

    # === MODE 3: MODERAT (NORMAL) ===
    elif "MODERAT" in mode:
        if curr > ema200 and rsi < 55: # Uptrend tapi lagi diskon
            signal = True
            reason = "✅ Tren Naik + Koreksi Wajar"

    # === MODE 4: KONSERVATIF (AMAN) ===
    elif "KONSERVATIF" in mode:
        if curr > ema200 and curr > ema50 and rsi < 45:
            signal = True
            reason = "🛡️ Setup Perfect (Aman)"

    if signal:
        # Stop Loss Logis
        # Kalau Momentum (Lagi naik kencang), SL harus lebih ketat (3%)
        sl_pct = 0.97 if "MOMENTUM" in mode else 0.95 
        sl_price = curr * sl_pct
        
        size = calculate_position(curr, sl_price, saldo_usdt, resiko_persen)
        
        # Volume Warning
        vol_usdt = (df['vol'] * df['close']).rolling(24).sum().iloc[-1]
        warn = ""
        if size > (vol_usdt * 0.01):
            size = vol_usdt * 0.01
            warn = "⚠️ Volume Kecil! Size dikurangi."

        # Strategi Jaring
        layers = []
        if "MOMENTUM" in mode:
            # Kalau lagi ngegas, jangan ngantri terlalu bawah, nanti ditinggal
            layers.append({"step": "Jaring 1 (Market)", "type": "Market", "amount": size*0.5, "price": "Sekarang"})
            layers.append({"step": "Jaring 2 (Support)", "type": "Limit", "amount": size*0.5, "price": curr*0.98}) # Antri dikit aja -2%
        else:
            # Kalau serok bawah, antri lebih dalam
            layers.append({"step": "Jaring 1 (Market)", "type": "Market", "amount": size*0.3, "price": "Sekarang"})
            layers.append({"step": "Jaring 2 (Bawah)", "type": "Limit", "amount": size*0.3, "price": curr*0.97})
            layers.append({"step": "Jaring 3 (Dalam)", "type": "Limit", "amount": size*0.4, "price": curr*0.94})

        return {
            "symbol": symbol, "entry": curr, "sl": sl_price, "tp": curr*(1+target_pct/100),
            "size": size, "src": src, "df": df, "reason": reason, "warn": warn, "layers": layers
        }
    return None

# --- UI LOOP ---
ph = st.empty(); res_ph = st.empty()

if run_sentinel:
    while True:
        u_price, u_stat, u_col = check_usdt_rate()
        with usdt_placeholder.container():
            st.metric("Kurs USDT", f"Rp {u_price:,.0f}")
            if u_col=="green": st.success(u_stat); 
            elif u_col=="red": st.error(u_stat); 
            else: st.warning(u_stat)
        
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
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("BELI (USDT)", f"${res['size']:.2f}")
                        c2.metric("ENTRY", f"${res['entry']:.5f}")
                        c3.metric("STOP LOSS", f"${res['sl']:.5f}")
                        
                        st.markdown("### 📋 INSTRUKSI EKSEKUSI")
                        for l in res['layers']:
                            if l['type'] == "Market":
                                st.info(f"1️⃣ **{l['step']}**: Beli **${l['amount']:.2f}** sekarang (Market).")
                            else:
                                st.warning(f"2️⃣ **{l['step']}**: Pasang Limit Buy **${l['amount']:.2f}** di harga **${l['price']:.5f}**.")
                        
                        st.write(f"🎯 **TARGET JUAL (TP):** ${res['tp']:.5f}")
                        
                        fig = go.Figure()
                        d = res['df']
                        fig.add_trace(go.Candlestick(x=d.index, open=d['open'], high=d['high'], low=d['low'], close=d['close']))
                        fig.add_trace(go.Scatter(x=d.index, y=d['ema200'], line=dict(color='orange'), name='EMA 200'))
                        st.plotly_chart(fig, use_container_width=True)
                        st.stop()
        time.sleep(2)
else:
    ph.info("Pilih Strategi di Kiri -> Aktifkan Pos Ronda.")
