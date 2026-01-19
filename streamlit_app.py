import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
import plotly.graph_objects as go
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from datetime import datetime, timedelta
import random

# --- KONFIGURASI ---
st.set_page_config(page_title="AI MICIN PRO V5", layout="wide")
st.title("🦐 AI MICIN PRO: Multi-Server + Ghost Projection")
st.markdown("""
**Upgrade Akurasi:**
1.  📡 **Multi-Exchange:** Cek Binance -> Gate.io -> MEXC (Cari data Real-Time di mana saja).
2.  👻 **Ghost Projection:** Jika terpaksa pakai data delay, AI memproyeksikan harga sekarang berdasarkan momentum (Garis Putus-Putus).
3.  🎯 **Visual Pro:** Area Profit & Loss otomatis.
""")

# --- DATABASE MICIN (FILTER < 10k) ---
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

# --- INISIALISASI MULTI-EXCHANGE ---
exchanges = {
    'binance': ccxt.binance({'enableRateLimit': True}),
    'gateio': ccxt.gateio({'enableRateLimit': True}),
    'mexc': ccxt.mexc({'enableRateLimit': True}),
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Strategi")
    target_pct = st.slider("Target Profit (%)", 2.0, 20.0, 5.0)
    stop_loss_pct = st.slider("Stop Loss (%)", 1.0, 10.0, 3.0)
    kurs_usd_idr = st.number_input("Kurs USD/IDR", value=16200)

# --- FUNGSI 1: AMBIL DATA (MULTI-SOURCE) ---
def get_data_multi_source(symbol):
    target_pair = symbol.replace("/IDR", "/USDT")
    df = None
    source_name = ""
    is_realtime = False
    
    # 1. Cek Exchange Real-Time Satu per Satu
    for name, exchange_obj in exchanges.items():
        try:
            # Ambil 100 candle 1 jam
            bars = exchange_obj.fetch_ohlcv(target_pair, timeframe='1h', limit=100)
            if bars and len(bars) > 0:
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
                df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
                df.set_index('time', inplace=True)
                source_name = f"⚡ {name.upper()} (Real-Time)"
                is_realtime = True
                break # Berhenti jika sudah ketemu
        except:
            continue # Lanjut ke exchange berikutnya
            
    # 2. Jika Semua Exchange Gagal, Pakai Yahoo (Backup)
    if df is None:
        try:
            yf_sym = target_pair.replace("/", "-").replace("USDT", "USD")
            data_yf = yf.download(yf_sym, period='5d', interval='1h', progress=False)
            if len(data_yf) > 20:
                if isinstance(data_yf.columns, pd.MultiIndex): data_yf.columns = data_yf.columns.droplevel(1)
                df = data_yf[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
                df.columns = ['open', 'high', 'low', 'close', 'vol']
                df.index = df.index + timedelta(hours=7)
                source_name = "⚠️ Yahoo (Delay - Ghost Mode Aktif)"
                is_realtime = False
        except:
            pass
            
    return df, source_name, is_realtime

# --- FUNGSI 2: ANALISA + GHOST PROJECTION ---
def analyze_micin(symbol):
    df, source, is_realtime = get_data_multi_source(symbol)
    if df is None: return None
    
    close = df['close']
    
    # Indikator
    df['ema50'] = EMAIndicator(close=close, window=50).ema_indicator()
    df['ema200'] = EMAIndicator(close=close, window=200).ema_indicator()
    
    # GHOST PROJECTION LOGIC
    # Jika data delay (Yahoo), kita proyeksikan harga "sekarang" berdasarkan tren terakhir
    last_candle_time = df.index[-1]
    current_time = datetime.now() + timedelta(hours=7)
    time_diff_minutes = (current_time - last_candle_time).total_seconds() / 60
    
    projected_price = close.iloc[-1]
    
    # Jika delay > 10 menit, hitung proyeksi
    if not is_realtime and time_diff_minutes > 10:
        # Hitung momentum 3 candle terakhir
        momentum = (close.iloc[-1] - close.iloc[-3]) / 3
        # Proyeksikan (Jangan terlalu agresif, dikali faktor redaman 0.5)
        # Artinya: "Lanjutin trennya, tapi pelan-pelan"
        projection = momentum * (time_diff_minutes / 60) * 0.5 
        projected_price = close.iloc[-1] + projection
        
        # Tambahkan baris bayangan ke dataframe untuk grafik
        new_row = pd.DataFrame({
            'open': [close.iloc[-1]], 'high': [projected_price], 
            'low': [close.iloc[-1]], 'close': [projected_price], 'vol': [0]
        }, index=[current_time])
        df = pd.concat([df, new_row])
        
    current_price = df['close'].iloc[-1]
    ema50 = df['ema50'].iloc[-2] # Pakai candle confirm sebelumnya
    ema200 = df['ema200'].iloc[-2]
    
    # LOGIKA UPTREND
    if current_price > ema50 and ema50 > ema200:
        entry = current_price
        tp = entry * (1 + target_pct/100)
        sl = entry * (1 - stop_loss_pct/100)
        
        return {
            "symbol": symbol,
            "entry": entry,
            "tp": tp,
            "sl": sl,
            "source": source,
            "df": df,
            "is_projected": not is_realtime,
            "gain": target_pct
        }
    return None

# --- UI UTAMA ---
if st.button("🚀 SCANNER MICIN PINTAR (ACAK 30)", type="primary"):
    batch = random.sample(WATCHLIST, 30)
    results = []
    
    prog = st.progress(0)
    log = st.empty()
    
    for i, c in enumerate(batch):
        log.caption(f"Mencari data {c} di berbagai server...")
        res = analyze_micin(c)
        if res: results.append(res)
        prog.progress((i+1)/30)
        
    log.empty()
    prog.empty()
    
    if results:
        results.sort(key=lambda x: x['gain'], reverse=True)
        best = results[0]
        
        # --- TAMPILAN JUARA ---
        st.success(f"💎 **HASIL TERBAIK: {best['symbol']}**")
        st.caption(f"Sumber Data: {best['source']}")
        
        if best['is_projected']:
            st.warning("👻 **GHOST MODE:** Data delay terdeteksi. Grafik putus-putus adalah prediksi AI tentang posisi harga SEKARANG.")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("ENTRY (Estimasi)", f"Rp {best['entry']*kurs_usd_idr:,.0f}", f"${best['entry']:.5f}")
        c2.metric("TARGET", f"Rp {best['tp']*kurs_usd_idr:,.0f}", f"+{target_pct}%")
        c3.metric("STOP LOSS", f"Rp {best['sl']*kurs_usd_idr:,.0f}", f"-{stop_loss_pct}%")
        
        # --- GRAFIK ---
        df = best['df']
        fig = go.Figure()
        
        # Candle Asli
        fig.add_trace(go.Candlestick(x=df.index[:-1], open=df['open'][:-1], high=df['high'][:-1], low=df['low'][:-1], close=df['close'][:-1], name='History'))
        
        # EMA
        fig.add_trace(go.Scatter(x=df.index, y=df['ema50'], line=dict(color='orange'), name='EMA 50'))
        
        # GHOST PROJECTION (Jika Delay)
        if best['is_projected']:
            fig.add_trace(go.Scatter(
                x=[df.index[-2], df.index[-1]],
                y=[df['close'].iloc[-2], df['close'].iloc[-1]],
                mode='lines+markers',
                line=dict(color='white', width=3, dash='dot'),
                name='AI PROJECTION (Ghost)'
            ))
            
        # KOTAK HIJAU (PROFIT)
        fig.add_shape(type="rect",
            x0=df.index[-1], y0=best['entry'], x1=df.index[-1] + timedelta(hours=12), y1=best['tp'],
            fillcolor="rgba(0, 255, 0, 0.2)", line=dict(width=0)
        )
        
        # KOTAK MERAH (LOSS)
        fig.add_shape(type="rect",
            x0=df.index[-1], y0=best['sl'], x1=df.index[-1] + timedelta(hours=12), y1=best['entry'],
            fillcolor="rgba(255, 0, 0, 0.2)", line=dict(width=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # DAFTAR LAIN
        st.write("---")
        st.write("### Opsi Lainnya:")
        rows = []
        for r in results[1:]:
            rows.append([r['symbol'], r['source'], f"${r['entry']:.5f}", f"${r['tp']:.5f}"])
        st.table(pd.DataFrame(rows, columns=["Koin", "Sumber", "Entry USD", "Target USD"]))
        
    else:
        st.warning("Tidak ada sinyal Uptrend yang valid di batch ini.")
