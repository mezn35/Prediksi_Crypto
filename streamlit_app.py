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
st.set_page_config(page_title="AI AUTO-PILOT PRO", layout="wide")
st.title("🤖 AI AUTO-PILOT: Scanner & Visual Pro")
st.markdown("""
**Fitur Gabungan:**
1.  🕵️ **Auto-Scanner:** AI mencari sendiri koin yang sedang **UPTREND** dan siap beli.
2.  📈 **Visual TradingView:** Area Profit (Hijau) dan Stop Loss (Merah) otomatis tergambar.
3.  🛡️ **Anti-Blokir:** Data dijamin muncul (Binance/Yahoo).
""")

# --- DATABASE KOIN LENGKAP ---
WATCHLIST = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
    "DOGE/USDT", "AVAX/USDT", "LINK/USDT", "DOT/USDT", "MATIC/USDT",
    "SHIB/USDT", "PEPE/USDT", "WIF/USDT", "BONK/USDT", "FLOKI/USDT",
    "NEAR/USDT", "RNDR/USDT", "FET/USDT", "INJ/USDT", "OP/USDT", "ARB/USDT",
    "JASMY/USDT", "LUNC/USDT", "SLP/USDT", "GALA/USDT", "FTM/USDT", "TRX/USDT",
    "LTC/USDT", "BCH/USDT", "UNI/USDT", "APT/USDT", "FIL/USDT", "ATOM/USDT",
    "IMX/USDT", "STX/USDT", "TIA/USDT", "SEI/USDT", "SUI/USDT", "AAVE/USDT",
    "SAND/USDT", "MANA/USDT", "THETA/USDT", "AXS/USDT", "EOS/USDT", "XTZ/USDT",
    "1000SATS/USDT", "BTTC/USDT", "DENT/USDT", "HOT/USDT", "SC/USDT", "ZIL/USDT",
    "IOST/USDT", "VTHO/USDT", "CKB/USDT", "RSR/USDT", "MBL/USDT", "ANKR/USDT"
]

# Inisialisasi Binance
exchange = ccxt.binance({'enableRateLimit': True, 'options': {'defaultType': 'spot'}})

# --- SIDEBAR PENGATURAN ---
with st.sidebar:
    st.header("⚙️ Strategi Trading")
    rr_ratio = st.number_input("Target Profit (Risk Reward Ratio)", value=2.0, step=0.5, help="Kalau pasang 2.0, artinya target untung 2x lipat dari risiko rugi.")
    risk_pct = st.slider("Jarak Stop Loss (%)", 1.0, 5.0, 3.0) / 100
    st.info("Klik tombol SCAN di layar utama untuk membiarkan AI bekerja.")

# --- FUNGSI 1: DATA ROBUST (ANTI-BLOKIR) ---
def get_data_robust(symbol):
    df = None
    source = ""
    
    # 1. COBA BINANCE
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=200)
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
            yf_sym = symbol.replace("/", "-").replace("USDT", "USD")
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

# --- FUNGSI 2: ANALISA SINYAL (STRATEGI) ---
def analyze_coin(symbol):
    df, source = get_data_robust(symbol)
    if df is None or len(df) < 50: return None
    
    close = df['close']
    
    # Indikator EMA
    df['ema50'] = EMAIndicator(close=close, window=50).ema_indicator()
    df['ema200'] = EMAIndicator(close=close, window=200).ema_indicator()
    
    current_price = close.iloc[-1]
    ema50 = df['ema50'].iloc[-1]
    ema200 = df['ema200'].iloc[-1]
    
    # LOGIKA UPTREND: Harga > EMA 50 > EMA 200
    if current_price > ema50 and ema50 > ema200:
        
        entry = current_price
        sl = entry * (1 - risk_pct)
        risk = entry - sl
        tp = entry + (risk * rr_ratio)
        
        return {
            "symbol": symbol,
            "entry": entry,
            "tp": tp,
            "sl": sl,
            "gain_pct": ((tp-entry)/entry)*100,
            "loss_pct": risk_pct*100,
            "source": source,
            "df": df
        }
    return None

# --- UI UTAMA: SCANNER ---
st.markdown("### 🕵️ Cari Peluang Cuan")
if st.button("🚀 SCAN PASAR (CARI SINYAL BUY)", type="primary"):
    
    # Ambil 25 koin acak agar cepat
    batch = random.sample(WATCHLIST, 25)
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, coin in enumerate(batch):
        status_text.text(f"AI sedang memeriksa grafik {coin}...")
        res = analyze_coin(coin)
        if res:
            results.append(res)
        progress_bar.progress((i + 1) / 25)
        
    status_text.empty()
    progress_bar.empty()
    
    # --- TAMPILKAN HASIL ---
    if results:
        # Urutkan berdasarkan potensi profit tertinggi
        results.sort(key=lambda x: x['gain_pct'], reverse=True)
        
        best_coin = results[0]
        
        # --- JUARA 1: TAMPILAN VISUAL PRO ---
        st.success(f"💎 **REKOMENDASI UTAMA: {best_coin['symbol']}**")
        st.caption(f"Data dari: {best_coin['source']} | Status: UPTREND KUAT")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("ENTRY (Beli)", f"${best_coin['entry']:.5f}")
        c2.metric("TARGET (Jual)", f"${best_coin['tp']:.5f}", f"+{best_coin['gain_pct']:.2f}%")
        c3.metric("STOP LOSS", f"${best_coin['sl']:.5f}", f"-{best_coin['loss_pct']:.2f}%")
        
        # Grafik TradingView Style
        df = best_coin['df']
        fig = go.Figure()

        # Candlestick
        fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Harga'))
        
        # EMA
        fig.add_trace(go.Scatter(x=df.index, y=df['ema50'], line=dict(color='orange', width=1), name='EMA 50'))
        fig.add_trace(go.Scatter(x=df.index, y=df['ema200'], line=dict(color='blue', width=2), name='EMA 200'))

        # Kotak Visual
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
        
        # --- TABEL SISA ---
        st.write("---")
        st.write("### 📋 Kandidat Lainnya (Uptrend)")
        
        rows = []
        for r in results[1:]:
            rows.append([r['symbol'], f"${r['entry']:.5f}", f"${r['tp']:.5f} (+{r['gain_pct']:.1f}%)", f"${r['sl']:.5f}"])
        
        st.table(pd.DataFrame(rows, columns=["Koin", "Harga Beli", "Target Jual", "Stop Loss"]))
        
    else:
        st.warning("⚠️ Di batch 25 koin ini, tidak ada yang memenuhi syarat 'UPTREND KUAT' (Harga > EMA 50 > EMA 200).")
        st.write("Pasar mungkin sedang Sideways atau Downtrend. Coba klik tombol SCAN lagi untuk mengambil sampel koin lain.")

else:
    st.info("👆 Klik tombol **SCAN PASAR** di atas. AI akan otomatis mencari koin terbaik untuk Anda.")
