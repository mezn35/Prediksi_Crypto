import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
import plotly.graph_objects as go
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from datetime import datetime, timedelta
import time
import random

# --- KONFIGURASI ---
st.set_page_config(page_title="CRYPTO COMMANDER", layout="wide")
st.title("🛡️ CRYPTO COMMANDER: Money Manager + USDT Radar")

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
    'tokocrypto': ccxt.tokocrypto({'enableRateLimit': True}), # KHUSUS USDT/BIDR
}

# --- SIDEBAR: USDT RADAR & MONEY MANAGER ---
with st.sidebar:
    st.title("🇮🇩 USDT RADAR")
    usdt_placeholder = st.empty() # Tempat update harga USDT
    
    st.divider()
    
    st.header("💰 Dompet & Risiko")
    saldo_usdt = st.number_input("Total Saldo USDT Anda", value=100.0, step=10.0)
    resiko_persen = st.slider("Siap Rugi per Trade (%)", 1.0, 10.0, 2.0)
    st.info(f"Maksimal Rugi: **${saldo_usdt * resiko_persen / 100:.2f}**")
    
    st.divider()
    
    st.header("🎛️ Kontrol")
    run_sentinel = st.checkbox("🔴 AKTIFKAN POS RONDA", value=False)

# --- FUNGSI CEK HARGA USDT/IDR (TOKO) ---
def check_usdt_rate():
    try:
        # Ambil data USDT/BIDR dari Tokocrypto (Paling akurat buat orang Indo)
        ticker = exchanges['tokocrypto'].fetch_ticker('USDT/BIDR')
        current_price = ticker['last']
        
        # Ambil data historis 100 candle 4 jam untuk hitung Bollinger Bands
        bars = exchanges['tokocrypto'].fetch_ohlcv('USDT/BIDR', timeframe='4h', limit=100)
        df = pd.DataFrame(bars, columns=['time','open','high','low','close','vol'])
        
        # Indikator BB
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_high'] = bb.bollinger_hband()
        df['bb_low'] = bb.bollinger_lband()
        df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
        
        rsi = df['rsi'].iloc[-1]
        bb_high = df['bb_high'].iloc[-1]
        bb_low = df['bb_low'].iloc[-1]
        
        # LOGIKA SARAN BELI USDT
        status = "NETRAL"
        color = "blue"
        
        if current_price <= bb_low or rsi < 35:
            status = "✅ DISKON! BELI USDT SKRG"
            color = "green"
        elif current_price >= bb_high or rsi > 65:
            status = "⛔ MAHAL! JANGAN BELI USDT"
            color = "red"
        else:
            status = "⚖️ HARGA WAJAR"
            color = "orange"
            
        return current_price, status, color
    except:
        return 16200, "Offline", "grey"

# --- FUNGSI DATA ---
def get_data(symbol):
    pair = symbol.replace("/IDR", "/USDT")
    df = None; source = ""
    for name, exc in exchanges.items():
        if name == 'tokocrypto': continue # Skip toko utk altcoin global biar cepat
        try:
            bars = exc.fetch_ohlcv(pair, timeframe='1h', limit=200)
            if bars:
                df = pd.DataFrame(bars, columns=['time','open','high','low','close','vol'])
                df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
                df.set_index('time', inplace=True)
                source = name.upper(); break
        except: continue
    
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

# --- FUNGSI MONEY MANAGER ---
def calculate_position(entry_price, stop_loss_price, total_equity, risk_pct):
    risk_amount = total_equity * (risk_pct / 100)
    sl_distance_pct = abs(entry_price - stop_loss_price) / entry_price
    if sl_distance_pct == 0: return 0
    position_size_usdt = risk_amount / sl_distance_pct
    if position_size_usdt > (total_equity * 0.5): position_size_usdt = total_equity * 0.5
    return position_size_usdt

# --- ANALISA UTAMA ---
def analyze_pure_math(symbol):
    df, src = get_data(symbol)
    if df is None: return None
    
    close = df['close']; curr = close.iloc[-1]
    
    df['ema200'] = EMAIndicator(close, window=200).ema_indicator()
    df['ema50'] = EMAIndicator(close, window=50).ema_indicator()
    df['rsi'] = RSIIndicator(close, window=14).rsi()
    
    rsi = df['rsi'].iloc[-1]
    ema200 = df['ema200'].iloc[-1]
    
    if curr > ema200 and rsi < 55:
        sl_price = curr * 0.95 
        buy_size = calculate_position(curr, sl_price, saldo_usdt, resiko_persen)
        
        # Volume Check
        vol_24h_usdt = (df['vol'] * df['close']).rolling(24).sum().iloc[-1]
        max_safe_buy = vol_24h_usdt * 0.01 
        
        warn = ""
        if buy_size > max_safe_buy:
            buy_size = max_safe_buy
            warn = "⚠️ Volume Sepi! Size dikecilkan otomatis."
            
        return {
            "symbol": symbol, "entry": curr, "sl": sl_price,
            "tp1": curr * 1.05, "size": buy_size, "src": src, "df": df, "warn": warn, "vol": vol_24h_usdt
        }
    return None

# --- UI LOOP ---
ph = st.empty(); res_ph = st.empty()

if run_sentinel:
    while True:
        # 1. Update USDT Radar (Sidebar)
        usdt_price, usdt_status, usdt_color = check_usdt_rate()
        with usdt_placeholder.container():
            st.metric("Kurs USDT/IDR (Tokocrypto)", f"Rp {usdt_price:,.0f}")
            if usdt_color == "green": st.success(usdt_status)
            elif usdt_color == "red": st.error(usdt_status)
            else: st.warning(usdt_status)
            
        # 2. Scan Micin
        batch = random.sample(WATCHLIST, 5)
        with ph.container():
            st.info(f"🔄 Scanning Koin: {', '.join(batch)} ...")
            
            for coin in batch:
                res = analyze_pure_math(coin)
                time.sleep(0.5)
                
                if res:
                    st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-37.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)
                    with res_ph.container():
                        st.success(f"💎 **BELI: {res['symbol']}**")
                        if res['warn']: st.warning(res['warn'])
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("💵 BELI (USDT)", f"${res['size']:.2f}")
                        c2.metric("🎯 ENTRY", f"${res['entry']:.5f}")
                        c3.metric("🛑 CUT LOSS", f"${res['sl']:.5f}")
                        
                        with st.expander("📉 Strategi Jaring (Layering)"):
                            c_a, c_b = st.columns(2)
                            c_a.info(f"**Jaring 1 (Market)**: ${res['size']*0.4:.2f}")
                            c_b.warning(f"**Jaring 2 (-3%)**: ${res['size']*0.6:.2f}")
                        
                        fig = go.Figure()
                        d = res['df']
                        fig.add_trace(go.Candlestick(x=d.index, open=d['open'], high=d['high'], low=d['low'], close=d['close']))
                        fig.add_trace(go.Scatter(x=d.index, y=d['ema200'], line=dict(color='blue'), name='EMA 200'))
                        st.plotly_chart(fig, use_container_width=True)
                        st.stop()
        time.sleep(2)
else:
    ph.info("Masukkan Saldo USDT -> Klik Aktifkan Pos Ronda.")
    # Preview USDT Radar saat standby
    usdt_price, usdt_status, usdt_color = check_usdt_rate()
    with usdt_placeholder.container():
        st.metric("Kurs USDT/IDR", f"Rp {usdt_price:,.0f}")
        st.caption(usdt_status)
