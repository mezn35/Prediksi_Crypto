import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
import plotly.graph_objects as go
from ta.trend import EMAIndicator
from datetime import datetime, timedelta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI VISUAL PRO (ANTI-BLOKIR)", layout="wide")
st.title("📈 AI VISUAL PRO: TradingView Style")
st.markdown("""
**Fitur Lengkap:**
1.  🛡️ **Anti-Blokir:** Otomatis pakai Yahoo Finance jika Binance memblokir server.
2.  🎯 **Visual Pro:** Area Target (Hijau) dan Stop Loss (Merah).
3.  🧠 **Strategi Tren:** Hanya sinyal saat tren EMA valid.
""")

# --- DATABASE KOIN ---
WATCHLIST = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
    "DOGE/USDT", "AVAX/USDT", "LINK/USDT", "DOT/USDT", "MATIC/USDT",
    "SHIB/USDT", "PEPE/USDT", "WIF/USDT", "BONK/USDT", "FLOKI/USDT",
    "NEAR/USDT", "RNDR/USDT", "FET/USDT", "INJ/USDT", "OP/USDT", "ARB/USDT",
    "JASMY/USDT", "LUNC/USDT", "SLP/USDT", "GALA/USDT", "FTM/USDT"
]

# Inisialisasi Binance
exchange = ccxt.binance({'enableRateLimit': True, 'options': {'defaultType': 'spot'}})

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Pengaturan")
    rr_ratio = st.number_input("Risk/Reward Ratio", value=2.0, step=0.5)
    risk_pct = st.slider("Risiko Stop Loss (%)", 1.0, 5.0, 3.0) / 100
    st.divider()
    selected_coin = st.selectbox("Pilih Koin:", WATCHLIST)

# --- FUNGSI DATA (ANTI-BLOKIR / HYBRID) ---
def get_data_robust(symbol):
    df = None
    source = ""
    
    # 1. COBA BINANCE
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=300)
        if bars:
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
            df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7) # WIB
            df.set_index('time', inplace=True)
            source = "⚡ Binance (Real-Time)"
    except:
        pass # Jika error 451/blokir, lanjut ke bawah

    # 2. COBA YAHOO (BACKUP)
    if df is None:
        try:
            # Ubah format BTC/USDT -> BTC-USD
            yf_sym = symbol.replace("/", "-").replace("USDT", "USD")
            data_yf = yf.download(yf_sym, period='1mo', interval='1h', progress=False)
            
            if len(data_yf) > 50:
                if isinstance(data_yf.columns, pd.MultiIndex): data_yf.columns = data_yf.columns.droplevel(1)
                df = data_yf[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
                df.columns = ['open', 'high', 'low', 'close', 'vol']
                df.index = df.index + timedelta(hours=7) # WIB
                source = "⚠️ Yahoo Finance (Backup)"
        except Exception as e:
            st.error(f"Yahoo Error: {e}")

    return df, source

# --- LOGIKA STRATEGI ---
def calculate_strategy(df, risk_per_trade, reward_ratio):
    close = df['close']
    
    # Indikator
    df['ema50'] = EMAIndicator(close=close, window=50).ema_indicator()
    df['ema200'] = EMAIndicator(close=close, window=200).ema_indicator()
    
    current_price = close.iloc[-1]
    ema50 = df['ema50'].iloc[-1]
    ema200 = df['ema200'].iloc[-1]
    
    signal_data = None
    trend_status = "NETRAL"
    
    # Syarat Buy: Harga > EMA 50 > EMA 200 (Uptrend Sehat)
    if current_price > ema50 and ema50 > ema200:
        trend_status = "UPTREND (BULLISH)"
        
        entry = current_price
        sl = entry * (1 - risk_per_trade) # Stop Loss di bawah
        risk = entry - sl
        tp = entry + (risk * reward_ratio) # Target Profit
        
        signal_data = {
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "risk_pct": risk_per_trade * 100,
            "reward_pct": (risk_per_trade * reward_ratio) * 100
        }
    elif current_price < ema200:
        trend_status = "DOWNTREND (BEARISH)"
        
    return df, trend_status, signal_data

# --- VISUALISASI PRO (KOTAK HIJAU/MERAH) ---
def plot_chart(df, signal, symbol):
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        name='Harga'
    ))

    # EMA Lines
    fig.add_trace(go.Scatter(x=df.index, y=df['ema50'], line=dict(color='orange', width=1), name='EMA 50'))
    fig.add_trace(go.Scatter(x=df.index, y=df['ema200'], line=dict(color='blue', width=2), name='EMA 200 (Tren Utama)'))

    if signal:
        # Waktu
        last_time = df.index[-1]
        future_time = last_time + timedelta(hours=12) # Gambar kotak ke kanan
        
        entry = signal['entry']
        tp = signal['tp']
        sl = signal['sl']
        
        # KOTAK HIJAU (PROFIT)
        fig.add_shape(type="rect",
            x0=last_time, y0=entry, x1=future_time, y1=tp,
            fillcolor="rgba(0, 255, 0, 0.2)", line=dict(width=1, color="green"),
        )
        
        # KOTAK MERAH (LOSS)
        fig.add_shape(type="rect",
            x0=last_time, y0=sl, x1=future_time, y1=entry,
            fillcolor="rgba(255, 0, 0, 0.2)", line=dict(width=1, color="red"),
        )
        
        # Label Teks
        fig.add_annotation(x=future_time, y=tp, text=f"TARGET: ${tp:.4f}", showarrow=False, font=dict(color="green"))
        fig.add_annotation(x=future_time, y=sl, text=f"STOP LOSS: ${sl:.4f}", showarrow=False, font=dict(color="red"))

    fig.update_layout(
        title=f"Analisa {symbol}", 
        yaxis_title="Harga (USDT)", 
        xaxis_rangeslider_visible=False,
        height=600,
        template="plotly_dark"
    )
    return fig

# --- UI UTAMA ---
if st.button("🚀 ANALISA SEKARANG", type="primary"):
    with st.spinner(f"Mengambil data {selected_coin} (Mencoba jalur anti-blokir)..."):
        
        # 1. Ambil Data (Robust)
        df_raw, source_name = get_data_robust(selected_coin)
        
        if df_raw is not None and len(df_raw) > 100:
            st.success(f"Data Berhasil Diambil dari: **{source_name}**")
            
            # 2. Hitung Strategi
            df_calc, trend, sig = calculate_strategy(df_raw, risk_pct, rr_ratio)
            
            # 3. Tampilkan
            c1, c2 = st.columns([1, 3])
            
            with c1:
                st.metric("Status Tren", trend)
                if sig:
                    st.success("✅ SINYAL BUY VALID")
                    st.write(f"**Entry:** ${sig['entry']:.4f}")
                    st.write(f"**Target:** ${sig['tp']:.4f} (+{sig['reward_pct']:.1f}%)")
                    st.write(f"**Stop Loss:** ${sig['sl']:.4f} (-{sig['risk_pct']:.1f}%)")
                else:
                    st.warning("⛔ TIDAK ADA SINYAL")
                    st.write("Harga belum memenuhi syarat Tren Naik Kuat (EMA 50 > EMA 200).")
            
            with c2:
                chart = plot_chart(df_calc, sig, selected_coin)
                st.plotly_chart(chart, use_container_width=True)
                
        else:
            st.error("Gagal mengambil data. Server mungkin sedang maintenance atau koin tidak ditemukan di Yahoo/Binance.")
