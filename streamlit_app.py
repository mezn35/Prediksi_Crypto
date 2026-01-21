import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
import plotly.graph_objects as go
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from datetime import datetime, timedelta
import time
import random

# --- KONFIGURASI ---
st.set_page_config(page_title="CRYPTO MONEY MANAGER", layout="wide")
st.title("🛡️ CRYPTO MONEY MANAGER: Kalkulator Anti-Rungkad")
st.markdown("""
**Strategi Keselamatan Aset:**
1.  **Volume Check:** Mencegah Anda membeli di koin "mati" atau menjadi mangsa bandar.
2.  **Smart Sizing:** Menghitung jumlah beli berdasarkan risiko kekalahan (bukan asal Hajar Kanan).
3.  **Layering:** Memecah pembelian menjadi 3 posisi untuk mendapatkan harga rata-rata terbaik.
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

# --- SIDEBAR: MONEY MANAGEMENT ---
with st.sidebar:
    st.header("💰 Dompet & Risiko")
    
    saldo_usdt = st.number_input("Total Saldo USDT Anda", value=100.0, step=10.0)
    resiko_persen = st.slider("Siap Rugi per Trade (%)", 1.0, 10.0, 2.0, help="Jika rugi, hanya hilang sekian % dari saldo.")
    
    st.info(f"Maksimal Rugi: **${saldo_usdt * resiko_persen / 100:.2f}**")
    
    st.divider()
    st.header("🎛️ Kontrol")
    run_sentinel = st.checkbox("🔴 AKTIFKAN POS RONDA", value=False)
    kurs_usd = st.number_input("Kurs USD (IDR)", value=16200)

# --- FUNGSI DATA ---
def get_data(symbol):
    pair = symbol.replace("/IDR", "/USDT")
    df = None; source = ""
    # Coba Multi Exchange
    for name, exc in exchanges.items():
        try:
            bars = exc.fetch_ohlcv(pair, timeframe='1h', limit=200)
            if bars:
                df = pd.DataFrame(bars, columns=['time','open','high','low','close','vol'])
                df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
                df.set_index('time', inplace=True)
                source = name.upper(); break
        except: continue
    
    # Backup Yahoo
    if df is None:
        try:
            yf_sym = pair.replace("/", "-").replace("USDT", "USD")
            d = yf.download(yf_sym, period='5d', interval='1h', progress=False)
            if len(d) > 20:
                if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.droplevel(1)
                df = d[['Open','High','Low','Close','Volume']]
                df.columns = ['open','high','low','close','vol']
                df.index = df.index + timedelta(hours=7)
                source = "Yahoo"
        except: pass
    return df, source

# --- FUNGSI HITUNG POSISI ---
def calculate_position(entry_price, stop_loss_price, total_equity, risk_pct):
    # Rumus: Risk Amount / % Jarak Stop Loss
    risk_amount = total_equity * (risk_pct / 100)
    sl_distance_pct = abs(entry_price - stop_loss_price) / entry_price
    
    if sl_distance_pct == 0: return 0
    
    position_size_usdt = risk_amount / sl_distance_pct
    
    # Safety Check: Jangan beli lebih dari 50% saldo di 1 koin micin
    if position_size_usdt > (total_equity * 0.5):
        position_size_usdt = total_equity * 0.5
        
    return position_size_usdt

# --- ANALISA TEKNIKAL MURNI ---
def analyze_pure_math(symbol):
    df, src = get_data(symbol)
    if df is None: return None
    
    close = df['close']; curr = close.iloc[-1]
    high = df['high'].iloc[-1]; low = df['low'].iloc[-1]
    
    # Indikator
    df['ema200'] = EMAIndicator(close, window=200).ema_indicator()
    df['ema50'] = EMAIndicator(close, window=50).ema_indicator()
    df['rsi'] = RSIIndicator(close, window=14).rsi()
    df['atr'] = high - low # Sederhana ATR
    
    rsi = df['rsi'].iloc[-1]
    ema200 = df['ema200'].iloc[-1]
    
    # RULE: Tren Naik (Aman) & Diskon (RSI < 55)
    if curr > ema200 and rsi < 55:
        # Tentukan Stop Loss (Low candle sebelumnya atau 3% di bawah harga)
        sl_price = curr * 0.95 
        
        # Hitung Uang
        buy_size = calculate_position(curr, sl_price, saldo_usdt, resiko_persen)
        
        # Cek Volume (Bahaya Exit Liquidity)
        # Estimasi volume 24jam terakhir (jumlahkan 24 candle terakhir)
        vol_24h_usdt = (df['vol'] * df['close']).rolling(24).sum().iloc[-1]
        
        # Jangan beli lebih dari 1% volume harian (Supaya tidak jadi paus nyangkut)
        max_safe_buy = vol_24h_usdt * 0.01 
        
        warning = ""
        if buy_size > max_safe_buy:
            buy_size = max_safe_buy # Turunkan ukuran beli
            warning = "⚠️ Ukuran dikecilkan karena volume koin sepi (Bahaya nyangkut!)"
            
        return {
            "symbol": symbol, "entry": curr, "sl": sl_price,
            "tp1": curr * 1.05, "tp2": curr * 1.10, "tp3": curr * 1.20,
            "size": buy_size, "rsi": rsi, "src": src, "df": df, "warn": warning,
            "vol": vol_24h_usdt
        }
    return None

# --- TAMPILAN UTAMA ---
ph = st.empty(); res_ph = st.empty()

if run_sentinel:
    while True:
        batch = random.sample(WATCHLIST, 5)
        with ph.container():
            st.info(f"🔄 Menghitung Risiko: {', '.join(batch)} ...")
            
            for coin in batch:
                res = analyze_pure_math(coin)
                time.sleep(0.5)
                
                if res:
                    st.markdown("""<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-37.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)
                    
                    with res_ph.container():
                        st.success(f"💎 **REKOMENDASI BELI: {res['symbol']}**")
                        
                        if res['warn']:
                            st.warning(res['warn'])
                        
                        # BAGIAN PENTING: STRATEGI UANG
                        c1, c2, c3 = st.columns(3)
                        c1.metric("💵 TOTAL BELI (USDT)", f"${res['size']:.2f}", f"Rp {res['size']*kurs_usd:,.0f}")
                        c2.metric("🎯 ENTRY PRICE", f"${res['entry']:.5f}")
                        c3.metric("🛑 STOP LOSS (Wajib)", f"${res['sl']:.5f}", "-5%")
                        
                        # STRATEGI LAYERING
                        with st.expander("📉 Strategi Jaring (Anti-Pucuk)", expanded=True):
                            st.write(f"Jangan beli ${res['size']:.2f} sekaligus! Pasang antrian (Limit Order):")
                            col_a, col_b, col_c = st.columns(3)
                            
                            # Jaring 1: 30% dana di harga sekarang
                            amt1 = res['size'] * 0.30
                            col_a.info(f"**Jaring 1 (Sekarang)**\n\nBeli: ${amt1:.2f}\nHarga: Market")
                            
                            # Jaring 2: 30% dana di harga diskon 2%
                            amt2 = res['size'] * 0.30
                            price2 = res['entry'] * 0.98
                            col_b.warning(f"**Jaring 2 (-2%)**\n\nBeli: ${amt2:.2f}\nHarga: ${price2:.5f}")
                            
                            # Jaring 3: 40% dana di harga diskon 4%
                            amt3 = res['size'] * 0.40
                            price3 = res['entry'] * 0.96
                            col_c.error(f"**Jaring 3 (-4%)**\n\nBeli: ${amt3:.2f}\nHarga: ${price3:.5f}")
                        
                        st.caption(f"Volume 24 Jam: ${res['vol']:,.0f} | Sumber: {res['src']}")
                        
                        # Grafik
                        fig = go.Figure()
                        d = res['df']
                        fig.add_trace(go.Candlestick(x=d.index, open=d['open'], high=d['high'], low=d['low'], close=d['close']))
                        fig.add_trace(go.Scatter(x=d.index, y=d['ema200'], line=dict(color='blue'), name='EMA 200 (Tren)'))
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.stop() # Berhenti biar user bisa baca hitungannya
        time.sleep(2)
else:
    ph.info("Masukkan Saldo USDT di kiri, lalu centang **AKTIFKAN POS RONDA**.")
