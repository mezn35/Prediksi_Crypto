import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
import plotly.graph_objects as go
from ta.trend import EMAIndicator
from datetime import datetime, timedelta
import random

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI MICIN HUNTER", layout="wide")
st.title("🦐 AI MICIN HUNTER: Auto-Pilot (< Rp 10k)")
st.markdown("""
**Spesifikasi Khusus:**
1.  🚫 **No Whale Coins:** BTC, ETH, dan koin mahal lainnya DIBLOKIR.
2.  🎯 **Fokus Micin:** Hanya scan daftar koin murah pilihan Anda.
3.  🚀 **Strategi:** Mencari koin murah yang sedang **UPTREND** (Siap Terbang).
""")

# --- DATABASE KHUSUS (DARI ANDA) ---
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
    "ERA/USDT", "PHA/USDT", "CTSI/USDT", "TNSR/USDT", 
    # Koin Pasangan IDR (Data akan diambil via USDT)
    "DOGE/IDR", "ADA/IDR", "HBAR/IDR", "POL/IDR", "WLD/IDR", "ARB/IDR", "ONDO/IDR", 
    "TIA/IDR", "FLOKI/IDR", "WIF/IDR", "ZIL/IDR", "NEIRO/IDR", "BOME/IDR", 
    "MANTA/IDR", "DOGS/IDR", "SCR/IDR"
]

# Inisialisasi Binance
exchange = ccxt.binance({'enableRateLimit': True, 'options': {'defaultType': 'spot'}})

# --- SIDEBAR PENGATURAN ---
with st.sidebar:
    st.header("⚙️ Strategi Trading Micin")
    rr_ratio = st.number_input("Target Profit (RR Ratio)", value=2.0, step=0.5, help="2.0 = Target Untung 2x dari Risiko Rugi.")
    risk_pct = st.slider("Stop Loss (Toleransi Rugi)", 1.0, 10.0, 5.0) / 100
    st.info(f"Database memuat {len(WATCHLIST)} koin micin/low cap.")

# --- FUNGSI 1: DATA ROBUST (ANTI-BLOKIR) ---
def get_data_robust(symbol):
    df = None
    source = ""
    
    # Konversi IDR ke USDT untuk data global
    target_symbol = symbol.replace("/IDR", "/USDT")
    
    # 1. COBA BINANCE
    try:
        # Fetch Data Candle
        bars = exchange.fetch_ohlcv(target_symbol, timeframe='1h', limit=200)
        if bars:
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
            df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7) # WIB
            df.set_index('time', inplace=True)
            source = "Binance"
    except:
        pass 

    # 2. COBA YAHOO (BACKUP)
    if df is None:
        try:
            # Format Yahoo: HEI-USD
            yf_sym = target_symbol.replace("/", "-").replace("USDT", "USD")
            data_yf = yf.download(yf_sym, period='1mo', interval='1h', progress=False)
            if len(data_yf) > 50:
                if isinstance(data_yf.columns, pd.MultiIndex): data_yf.columns = data_yf.columns.droplevel(1)
                df = data_yf[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
                df.columns = ['open', 'high', 'low', 'close', 'vol']
                df.index = df.index + timedelta(hours=7) # WIB
                source = "Yahoo"
        except:
            pass

    return df, source

# --- FUNGSI 2: ANALISA SINYAL (UPTREND ONLY) ---
def analyze_coin(symbol):
    df, source = get_data_robust(symbol)
    if df is None or len(df) < 50: return None
    
    close = df['close']
    
    # Indikator EMA (Trend Filter)
    df['ema50'] = EMAIndicator(close=close, window=50).ema_indicator()
    df['ema200'] = EMAIndicator(close=close, window=200).ema_indicator()
    
    current_price = close.iloc[-1]
    ema50 = df['ema50'].iloc[-1]
    ema200 = df['ema200'].iloc[-1]
    
    # LOGIKA UPTREND: Harga > EMA 50 > EMA 200
    # (Pastikan kita hanya beli saat tren NAIK)
    if current_price > ema50 and ema50 > ema200:
        
        entry = current_price
        sl = entry * (1 - risk_pct)
        risk = entry - sl
        tp = entry + (risk * rr_ratio)
        
        # Hitung persentase
        gain_pct = ((tp - entry) / entry) * 100
        loss_pct = risk_pct * 100
        
        return {
            "symbol": symbol,
            "entry": entry,
            "tp": tp,
            "sl": sl,
            "gain_pct": gain_pct,
            "loss_pct": loss_pct,
            "source": source,
            "df": df
        }
    return None

# --- UI UTAMA ---
st.markdown("### 🕵️ Scanner Micin (Auto-Pilot)")
if st.button("🚀 SCAN PASAR SEKARANG", type="primary"):
    
    # Ambil sampel acak 30 koin dari daftar micin
    batch = random.sample(WATCHLIST, 30)
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, coin in enumerate(batch):
        status_text.text(f"Mengecek {coin}...")
        res = analyze_coin(coin)
        if res:
            results.append(res)
        progress_bar.progress((i + 1) / 30)
        
    status_text.empty()
    progress_bar.empty()
    
    # --- TAMPILKAN HASIL ---
    if results:
        # Urutkan: Prioritaskan yang potensi untungnya (persentase) paling besar
        results.sort(key=lambda x: x['gain_pct'], reverse=True)
        
        best_coin = results[0]
        
        # --- JUARA 1 ---
        st.success(f"💎 **REKOMENDASI TERBAIK: {best_coin['symbol']}**")
        st.caption(f"Data: {best_coin['source']} | Tren: SUPER BULLISH 🚀")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("ENTRY (Beli)", f"${best_coin['entry']:.6f}")
        c2.metric("TARGET (Jual)", f"${best_coin['tp']:.6f}", f"+{best_coin['gain_pct']:.2f}%")
        c3.metric("STOP LOSS", f"${best_coin['sl']:.6f}", f"-{best_coin['loss_pct']:.2f}%")
        
        # Grafik TradingView Style
        df = best_coin['df']
        fig = go.Figure()

        # Candlestick
        fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Harga'))
        
        # EMA Lines
        fig.add_trace(go.Scatter(x=df.index, y=df['ema50'], line=dict(color='orange', width=1), name='EMA 50'))
        fig.add_trace(go.Scatter(x=df.index, y=df['ema200'], line=dict(color='blue', width=2), name='EMA 200'))

        # Visual Area
        last_time = df.index[-1]
        future_time = last_time + timedelta(hours=12)
        
        # Hijau (Profit)
        fig.add_shape(type="rect", x0=last_time, y0=best_coin['entry'], x1=future_time, y1=best_coin['tp'],
            fillcolor="rgba(0, 255, 0, 0.2)", line=dict(width=1, color="green"))
        
        # Merah (Loss)
        fig.add_shape(type="rect", x0=last_time, y0=best_coin['sl'], x1=future_time, y1=best_coin['entry'],
            fillcolor="rgba(255, 0, 0, 0.2)", line=dict(width=1, color="red"))

        fig.update_layout(title=f"Setup Trading {best_coin['symbol']}", height=500, xaxis_rangeslider_visible=False, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        # --- DAFTAR LAINNYA ---
        st.write("---")
        st.write("### 📋 Micin Potensial Lainnya")
        
        rows = []
        for r in results[1:]:
            rows.append([r['symbol'], f"${r['entry']:.6f}", f"${r['tp']:.6f} (+{r['gain_pct']:.1f}%)"])
        
        st.table(pd.DataFrame(rows, columns=["Koin", "Harga Beli", "Target Jual (Estimasi)"]))
        
    else:
        st.warning("⚠️ Batch ini tidak menemukan koin yang memenuhi syarat UPTREND KUAT.")
        st.write("Pasar micin sangat volatil. Coba klik tombol SCAN lagi untuk mengambil sampel koin yang berbeda.")

else:
    st.info("👆 Klik tombol **SCAN PASAR** di atas. AI akan mencari koin murah yang siap terbang.")
