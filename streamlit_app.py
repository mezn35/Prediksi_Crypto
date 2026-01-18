import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
from ta.volatility import BollingerBands, AverageTrueRange
from ta.momentum import RSIIndicator, StochasticOscillator
from datetime import datetime, timedelta
import plotly.graph_objects as go
import random

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="SWING MASTER 30%", layout="wide")
st.title("🏹 SWING MASTER: Target Profit 30%")
st.markdown("""
**Strategi Big Profit:**
* 🎯 **Target:** Minimal 30% Kenaikan.
* 📅 **Waktu:** Menghitung estimasi tanggal panen berdasarkan kecepatan koin.
* 📊 **Visual:** Grafik Candlestick dengan Zona Beli & Jual.
""")

# --- DATABASE KOIN ---
WATCHLIST = [
    # --- USDT PAIRS (Prioritas Micin & Volatil) ---
    "HEI/USDT", "KOM/USDT", "BROCCOLI714/USDT", "PENGU/USDT", "BIO/USDT", "VANA/USDT", 
    "A2Z/USDT", "VELODROME/USDT", "1000CHEEMS/USDT", "TURTLE/USDT", "MDT/USDT", "ACA/USDT", 
    "CITY/USDT", "ATM/USDT", "COS/USDT", "ACM/USDT", "CHESS/USDT", "DATA/USDT", "NBT/USDT", 
    "CREO/USDT", "CVC/USDT", "ALPINE/USDT", "BEL/USDT", "JUV/USDT", "HOOK/USDT", "NKN/USDT", 
    "QUICK/USDT", "DEGO/USDT", "D/USDT", "IDEX/USDT", "GHST/USDT", "UTK/USDT", "FIO/USDT", 
    "TRU/USDT", "ENSO/USDT", "RDNT/USDT", "MITO/USDT", "DODO/USDT", "FARM/USDT", "BAR/USDT", 
    "VIC/USDT", "PSG/USDT", "EDEN/USDT", "SYN/USDT", "DF/USDT", "TST/USDT", "LAZIO/USDT", 
    "TKO/USDT", "MLN/USDT", "WAN/USDT", "HAEDAL/USDT", "NFP/USDT", "ADX/USDT", "BMT/USDT", 
    "ASR/USDT", "GTC/USDT", "TUT/USDT", "TREE/USDT", "INIT/USDT", "SHELL/USDT", "PORTAL/USDT", 
    "HEMI/USDT", "PIVX/USDT", "BIFI/USDT", "TLM/USDT", "SCR/USDT", "HMSTR/USDT", "A/USDT", 
    "PORTO/USDT", "SOLV/USDT", "OG/USDT", "LUMIA/USDT", "RAD/USDT", "TOWNS/USDT", "ALICE/USDT", 
    "SYS/USDT", "HIGH/USDT", "ATA/USDT", "PHB/USDT", "NTRN/USDT", "MBOX/USDT", "F/USDT", 
    "OGN/USDT", "KERNEL/USDT", "MUBARAK/USDT", "HFT/USDT", "SAGA/USDT", "EPIC/USDT", "AI/USDT", 
    "FUN/USDT", "ARPA/USDT", "ALCX/USDT", "STO/USDT", "NOM/USDT", "RARE/USDT", "DOGS/USDT", 
    "CATI/USDT", "NEWT/USDT", "ZBT/USDT", "PYR/USDT", "COOKIE/USDT", "MAV/USDT", "VANRY/USDT", 
    "DENT/USDT", "GNS/USDT", "BANK/USDT", "JOE/USDT", "QI/USDT", "GPS/USDT", "OXT/USDT", 
    "C98/USDT", "ACE/USDT", "CETUS/USDT", "ACT/USDT", "C/USDT", "MBL/USDT", "BANANA/USDT", 
    "WIN/USDT", "AGLD/USDT", "YB/USDT", "MOVR/USDT", "RESOLV/USDT", "ZKC/USDT", "DOLO/USDT", 
    "GLMR/USDT", "FORTH/USDT", "AVA/USDT", "WCT/USDT", "AIXBT/USDT", "PIXEL/USDT", "CELR/USDT", 
    "REZ/USDT", "HOLO/USDT", "POND/USDT", "THE/USDT", "DYM/USDT", "QKC/USDT", "CGPT/USDT", 
    "MIRA/USDT", "HYPER/USDT", "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "SOL/USDT", 
    "USDC/USDT", "TRX/USDT", "1000CAT/USDT", "DOGE/USDT", "ADA/USDT", "WBETH/USDT", "BCH/USDT", 
    "LINK/USDT", "XLM/USDT", "SUI/USDT", "USDE/USDT", "AVAX/USDT", "LTC/USDT", "HBAR/USDT", 
    "SHIB/USDT", "WLFI/USDT", "TON/USDT", "DOT/USDT", "USD1/USDT", "UNI/USDT", "TAO/USDT", 
    "AAVE/USDT", "PEPE/USDT", "ICP/USDT", "NEAR/USDT", "BFUSD/USDT", "ETC/USDT", "ASTER/USDT", 
    "PAXG/USDT", "ENA/USDT", "POL/USDT", "WLD/USDT", "SKY/USDT", "APT/USDT", "ARB/USDT", 
    "ATOM/USDT", "ONDO/USDT", "ALGO/USDT", "FIL/USDT", "RENDER/USDT", "TRUMP/USDT", "VET/USDT", 
    "QNT/USDT", "PUMP/USDT", "BONK/USDT", "SEI/USDT", "CAKE/USDT", "JUP/USDT", "OP/USDT", 
    "STX/USDT", "XTZ/USDT", "NEXO/USDT", "FET/USDT", "CRV/USDT", "CHZ/USDT", "VIRTUAL/USDT", 
    "IMX/USDT", "INJ/USDT", "LDO/USDT", "ETHFI/USDT", "MORPHO/USDT", "FDUSD/USDT", "TUSD/USDT", 
    "TIA/USDT", "ZRO/USDT", "FLOKI/USDT", "GRT/USDT", "2Z/USDT", "STRK/USDT", "SYRUP/USDT", 
    "CFX/USDT", "JASMY/USDT", "TWT/USDT", "SUN/USDT", "BTTC/USDT", "SAND/USDT", "DCR/USDT", 
    "IOTA/USDT", "ENS/USDT", "GNO/USDT", "PYTH/USDT", "WIF/USDT", "ZK/USDT", "KAIA/USDT", 
    "GALA/USDT", "JST/USDT", "PENDLE/USDT", "FARTCOIN/USDT", "THETA/USDT", "AXS/USDT", 
    "MANA/USDT", "BAT/USDT", "RAY/USDT", "NEO/USDT", "DEXE/USDT", "AR/USDT", "COMP/USDT", 
    "WAL/USDT", "XPL/USDT", "GLM/USDT", "RUNE/USDT", "S/USDT", "XEC/USDT", "LUNC/USDT", 
    "CVX/USDT", "1INCH/USDT", "EIGEN/USDT", "ZEN/USDT", "FF/USDT", "W/USDT", "EGLD/USDT", 
    "0G/USDT", "AMP/USDT", "SFP/USDT", "KITE/USDT", "BARD/USDT", "JTO/USDT", "RSR/USDT", 
    "APE/USDT", "ATH/USDT", "SNX/USDT", "LPT/USDT", "DYDX/USDT", "BEAMX/USDT", "QTUM/USDT", 
    "MET/USDT", "FORM/USDT", "SUPER/USDT", "TFUEL/USDT", "FLOW/USDT", "COW/USDT", "GAS/USDT", 
    "KSM/USDT", "BERA/USDT", "MOVE/USDT", "CKB/USDT", "KAITO/USDT", "ME/USDT", "YFI/USDT", 
    "ZRX/USDT", "DGB/USDT", "RVN/USDT", "XVG/USDT", "TURBO/USDT", "ACH/USDT", "ZIL/USDT", 
    "T/USDT", "MINA/USDT", "VELO/USDT", "ORDI/USDT", "AWE/USDT", "ROSE/USDT", "EDU/USDT", 
    "1MBABYDOGE/USDT", "BLUR/USDT", "XNO/USDT", "ID/USDT", "LINEA/USDT", "SUSHI/USDT", 
    "KAVA/USDT", "HOME/USDT", "FRAX/USDT", "STG/USDT", "ASTR/USDT", "SC/USDT", "XVS/USDT", 
    "HOT/USDT", "NXPC/USDT", "OM/USDT", "AXL/USDT", "REQ/USDT", "VTHO/USDT", "CELO/USDT", 
    "PNUT/USDT", "GMX/USDT", "IOTX/USDT", "PROVE/USDT", "NMR/USDT", "RED/USDT", "AVNT/USDT", 
    "DUSK/USDT", "FXS/USDT", "LRC/USDT", "ANKR/USDT", "SAHARA/USDT", "UMA/USDT", "ORCA/USDT", 
    "MEME/USDT", "HUMA/USDT", "MASK/USDT", "ALT/USDT", "POLYX/USDT", "SKL/USDT", "ICX/USDT", 
    "SSV/USDT", "BB/USDT", "SIGN/USDT", "ENJ/USDT", "ONE/USDT", "LUNA/USDT", "TRB/USDT", 
    "GIGGLE/USDT", "PROM/USDT", "STORJ/USDT", "NOT/USDT", "ONT/USDT", "ARDR/USDT", "LA/USDT", 
    "RLC/USDT", "BAND/USDT", "GMT/USDT", "WOO/USDT", "PLUME/USDT", "COTI/USDT", "AEUR/USDT", 
    "RONIN/USDT", "ARK/USDT", "POWR/USDT", "HIVE/USDT", "BIGTIME/USDT", "PEOPLE/USDT", 
    "SPK/USDT", "NEIRO/USDT", "BABY/USDT", "EUL/USDT", "YGG/USDT", "IOST/USDT", "G/USDT", 
    "RPL/USDT", "LAYER/USDT", "USUAL/USDT", "EURI/USDT", "LISTA/USDT", "BNT/USDT", "USDP/USDT", 
    "FLUX/USDT", "LSK/USDT", "ARKM/USDT", "SPELL/USDT", "IO/USDT", "SCRT/USDT", "STRAX/USDT", 
    "BICO/USDT", "BOME/USDT", "SXP/USDT", "KNC/USDT", "CYBER/USDT", "SOMI/USDT", "ILV/USDT", 
    "OSMO/USDT", "PARTI/USDT", "ANIME/USDT", "AUDIO/USDT", "AT/USDT", "CTK/USDT", "IQ/USDT", 
    "METIS/USDT", "XUSD/USDT", "CHR/USDT", "WAXP/USDT", "LQTY/USDT", "ONG/USDT", "USTC/USDT", 
    "AEVO/USDT", "API3/USDT", "SXT/USDT", "1000SATS/USDT", "OPEN/USDT", "BANANAS31/USDT", 
    "MANTA/USDT", "SANTOS/USDT", "XAI/USDT", "GUN/USDT", "RIF/USDT", "MTL/USDT", "AUCTION/USDT", 
    "FIDA/USDT", "ACX/USDT", "DIA/USDT", "SLP/USDT", "MAGIC/USDT", "ERA/USDT", "PHA/USDT", 
    "CTSI/USDT", "TNSR/USDT",
    
    # --- IDR PAIRS ---
    "BTC/IDR", "ETH/IDR", "USDT/IDR", "BNB/IDR", "XRP/IDR", "SOL/IDR", "USDC/IDR", 
    "DOGE/IDR", "ADA/IDR", "SUI/IDR", "AVAX/IDR", "HBAR/IDR", "TON/IDR", "TAO/IDR", 
    "ASTER/IDR", "POL/IDR", "WLD/IDR", "ARB/IDR", "ONDO/IDR", "RENDER/IDR", "VIRTUAL/IDR", 
    "SPX/IDR", "TIA/IDR", "FLOKI/IDR", "WIF/IDR", "SOON/IDR", "ALCH/IDR", "ZIL/IDR", 
    "VELO/IDR", "MEW/IDR", "POPCAT/IDR", "GRASS/IDR", "MOODENG/IDR", "JELLYJELLY/IDR", 
    "CARV/IDR", "NEIRO/IDR", "BOME/IDR", "MANTA/IDR", "GOAT/IDR", "DOGS/IDR", "SCR/IDR"
]

# --- KONEKSI ---
exchange = ccxt.binance({'enableRateLimit': True})

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Pengaturan")
    modal_awal = st.number_input("Modal Trading (Rp)", value=1000000)
    kurs_usd_idr = st.number_input("Kurs USD/IDR", value=16100)
    st.divider()
    st.warning("⚠️ Target 30% membutuhkan waktu (bisa berhari-hari). Ini bukan scalping 5 menit.")

# --- FUNGSI HYBRID DATA (Binance -> Yahoo) ---
def get_data(symbol):
    df = None
    source = ""
    
    # 1. Coba Binance (Realtime)
    try:
        target = symbol.replace("/IDR", "/USDT")
        # Mapping khusus
        if "JELLY" in target: target = "JELLY/USDT" 
        
        bars = exchange.fetch_ohlcv(target, timeframe='1h', limit=100) # Timeframe 1 Jam untuk Swing
        if bars:
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
            df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
            df.set_index('time', inplace=True)
            source = "Realtime"
    except:
        pass

    # 2. Coba Yahoo (Backup)
    if df is None:
        try:
            yf_sym = symbol.replace("/", "-").replace("USDT", "USD").replace("IDR", "USD")
            data_yf = yf.download(yf_sym, period='1mo', interval='1h', progress=False)
            if len(data_yf) > 10:
                if isinstance(data_yf.columns, pd.MultiIndex): data_yf.columns = data_yf.columns.droplevel(1)
                df = data_yf[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
                df.columns = ['open', 'high', 'low', 'close', 'vol']
                df.index = df.index + timedelta(hours=7)
                source = "Backup (Delay)"
        except:
            pass
            
    return df, source

# --- ANALISA SWING 30% ---
def analyze_swing(symbol):
    df, source = get_data(symbol)
    if df is None: return None
    
    close = df['close']
    
    # 1. Hitung Volatilitas (ATR) untuk Estimasi Waktu
    df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=close, window=14).average_true_range()
    current_atr = df['atr'].iloc[-1]
    last_price = close.iloc[-1]
    
    # Berapa % rata-rata pergerakan per jam?
    hourly_move_pct = (current_atr / last_price) * 100
    if hourly_move_pct == 0: hourly_move_pct = 0.5 # Default jika data flat
    
    # 2. Hitung Estimasi Waktu untuk mencapai 30%
    # Rumus: 30% / (% Gerak per Jam) = Jam yang dibutuhkan
    hours_needed = 30 / hourly_move_pct
    days_needed = hours_needed / 24
    
    # Waktu
    buy_time = df.index[-1]
    sell_time_est = buy_time + timedelta(hours=hours_needed)
    
    # 3. Target Harga
    price_idr = last_price * kurs_usd_idr
    tp_price_idr = price_idr * 1.30 # Target 30%
    sl_price_idr = price_idr * 0.90 # Stop Loss 10% (Risk Reward 1:3)
    
    # 4. Sinyal Masuk (Cari yang lagi Murah/Diskon)
    df['rsi'] = RSIIndicator(close=close, window=14).rsi()
    rsi = df['rsi'].iloc[-1]
    
    signal = "WAIT"
    reason = "Harga Normal"
    score = 0
    
    if rsi < 40:
        signal = "BUY SETUP"
        reason = "Harga Diskon (RSI Rendah)"
        score = 80
        if rsi < 30:
            score = 95
            reason = "SUPER DISKON (Oversold)"
            
    profit_est = modal_awal * 0.30
    
    return {
        "ticker": symbol,
        "price_idr": price_idr,
        "tp": tp_price_idr,
        "sl": sl_price_idr,
        "buy_date": buy_time,
        "sell_date": sell_time_est,
        "days": days_needed,
        "signal": signal,
        "reason": reason,
        "score": score,
        "df": df,
        "source": source
    }

# --- UI UTAMA ---
col_scan, col_info = st.columns([1, 3])
with col_scan:
    if st.button("🔎 CARI KOIN POTENSI 30% (ACAK)", type="primary"):
        st.session_state['scan_results'] = []
        batch = random.sample(WATCHLIST, 40)
        
        progress = st.progress(0)
        for i, coin in enumerate(batch):
            res = analyze_swing(coin)
            if res and res['score'] > 0: # Hanya simpan yang ada setup
                st.session_state['scan_results'].append(res)
            progress.progress((i+1)/40)
        progress.empty()

# TAMPILKAN HASIL
if 'scan_results' in st.session_state and st.session_state['scan_results']:
    results = st.session_state['scan_results']
    results.sort(key=lambda x: x['score'], reverse=True)
    
    best = results[0] # Ambil yang terbaik
    
    st.success(f"💎 **REKOMENDASI TERBAIK: {best['ticker']}** ({best['source']})")
    
    # --- DETAIL WAKTU BELI & JUAL ---
    c1, c2, c3 = st.columns(3)
    c1.metric("BELI SEKARANG", f"Rp {best['price_idr']:,.0f}", help=f"Tanggal: {best['buy_date'].strftime('%d-%b %H:%M')}")
    c2.metric("JUAL DI (TARGET 30%)", f"Rp {best['tp']:,.0f}", f"Est: {best['sell_date'].strftime('%d-%b')}")
    c3.metric("STOP LOSS (AMANKAN)", f"Rp {best['sl']:,.0f}", "-10%")
    
    st.info(f"⏳ **Estimasi Waktu Tahan:** {best['days']:.1f} Hari (Tergantung volatilitas pasar)")
    
    # --- GRAFIK PRO (CANDLESTICK + BOX) ---
    st.subheader(f"Grafik Trading Plan: {best['ticker']}")
    
    df = best['df']
    last_idx = df.index[-1]
    future_idx = best['sell_date']
    
    fig = go.Figure()
    
    # 1. Candlestick
    fig.add_trace(go.Candlestick(x=df.index,
                    open=df['open'], high=df['high'],
                    low=df['low'], close=df['close'],
                    name='Harga'))
    
    # 2. Kotak Hijau (Profit Area)
    fig.add_shape(type="rect",
        x0=last_idx, y0=best['price_idr']/kurs_usd_idr,
        x1=future_idx, y1=best['tp']/kurs_usd_idr,
        line=dict(color="green", width=0),
        fillcolor="rgba(0, 255, 0, 0.2)", # Transparan Hijau
    )
    
    # 3. Kotak Merah (Loss Area)
    fig.add_shape(type="rect",
        x0=last_idx, y0=best['sl']/kurs_usd_idr,
        x1=future_idx, y1=best['price_idr']/kurs_usd_idr,
        line=dict(color="red", width=0),
        fillcolor="rgba(255, 0, 0, 0.2)", # Transparan Merah
    )
    
    # 4. Garis Target
    fig.add_trace(go.Scatter(
        x=[last_idx, future_idx], 
        y=[best['tp']/kurs_usd_idr, best['tp']/kurs_usd_idr],
        mode="lines+text",
        name="Target 30%",
        line=dict(color="green", dash="dash"),
        text=[f"", f"TP: +30%"],
        textposition="top right"
    ))

    fig.update_layout(xaxis_rangeslider_visible=False, height=500, title="Visualisasi Area Profit (Hijau) vs Risiko (Merah)")
    st.plotly_chart(fig, use_container_width=True)
    
    # --- TABEL SISA ---
    st.write("---")
    st.write("**Opsi Lain yang Sedang Murah:**")
    rows = []
    for r in results[1:]:
        rows.append([r['ticker'], f"Rp {r['price_idr']:,.0f}", f"Rp {r['tp']:,.0f}", f"{r['days']:.1f} Hari"])
    st.table(pd.DataFrame(rows, columns=["Koin", "Harga Beli", "Harga Jual (30%)", "Est. Waktu"]))

else:
    st.info("Klik tombol **CARI KOIN** untuk memulai analisa.")
