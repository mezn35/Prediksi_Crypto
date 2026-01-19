import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import plotly.graph_objects as go
from ta.trend import EMAIndicator
from datetime import datetime, timedelta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI VISUAL PRO", layout="wide")
st.title("📈 AI VISUAL PRO: Trend Strategy")
st.markdown("""
**Fokus Tahap 1: Visualisasi Akurat**
Aplikasi ini meniru gaya TradingView untuk menampilkan area **Target Profit (Hijau)** dan **Stop Loss (Merah)** berdasarkan strategi tren EMA.
""")

# --- DATABASE KOIN (Disederhanakan untuk Fokus Akurasi) ---
WATCHLIST = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
    "DOGE/USDT", "AVAX/USDT", "LINK/USDT", "DOT/USDT", "MATIC/USDT",
    "SHIB/USDT", "PEPE/USDT", "WIF/USDT", "BONK/USDT", "FLOKI/USDT",
    "NEAR/USDT", "RNDR/USDT", "FET/USDT", "INJ/USDT", "OP/USDT", "ARB/USDT"
]

# Inisialisasi Binance (Real-Time Accuracy)
exchange = ccxt.binance({'enableRateLimit': True, 'options': {'defaultType': 'spot'}})

# --- SIDEBAR PENGATURAN ---
with st.sidebar:
    st.header("⚙️ Parameter Strategi")
    # Risk Reward Ratio 1:2 artinya siap rugi 1 untuk dapat 2
    rr_ratio = st.number_input("Risk/Reward Ratio (Contoh 2.0 = Target 2x Lipat Risiko)", value=2.0, step=0.5, min_value=1.0)
    risk_pct = st.slider("Risiko per Trade (%) (Jarak Stop Loss)", 1.0, 5.0, 2.0) / 100
    st.divider()
    selected_coin = st.selectbox("Pilih Koin untuk Dianalisa:", WATCHLIST)

# --- FUNGSI 1: AMBIL DATA REAL-TIME ---
def get_data(symbol, timeframe='1h'):
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=300)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7) # WIB
        df.set_index('time', inplace=True)
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data dari Binance: {e}")
        return None

# --- FUNGSI 2: HITUNG STRATEGI (PREDIKSI) ---
def calculate_strategy(df, risk_per_trade, reward_ratio):
    close = df['close']
    
    # Indikator Tren: EMA 50 (Cepat) dan EMA 200 (Lambat)
    df['ema50'] = EMAIndicator(close=close, window=50).ema_indicator()
    df['ema200'] = EMAIndicator(close=close, window=200).ema_indicator()
    
    current_price = close.iloc[-1]
    ema50_now = df['ema50'].iloc[-1]
    ema200_now = df['ema200'].iloc[-1]
    
    # LOGIKA: Hanya Buy jika Harga > EMA50 > EMA200 (Strong Uptrend)
    trend = "NETRAL/DOWN"
    signal_data = None
    
    if current_price > ema50_now and ema50_now > ema200_now:
        trend = "UPTREND (Kuat)"
        
        # Hitung Level Kunci
        entry_price = current_price
        # Stop Loss ditaruh di bawah EMA 50 atau berdasarkan persentase risiko
        stop_loss_price = entry_price * (1 - risk_per_trade)
        
        risk_amount = entry_price - stop_loss_price
        target_price = entry_price + (risk_amount * reward_ratio)
        
        pct_gain = ((target_price - entry_price) / entry_price) * 100
        pct_loss = ((stop_loss_price - entry_price) / entry_price) * 100
        
        signal_data = {
            "entry": entry_price,
            "tp": target_price,
            "sl": stop_loss_price,
            "gain_pct": pct_gain,
            "loss_pct": pct_loss
        }
        
    return df, trend, signal_data

# --- FUNGSI 3: VISUALISASI (MENIRU GAMBAR ANDA) ---
def plot_visual_pro(df, signal_data, coin_name):
    fig = go.Figure()

    # 1. Candlestick Chart
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        name='Harga'
    ))

    # 2. Garis EMA (Indikator Tren)
    fig.add_trace(go.Scatter(x=df.index, y=df['ema50'], line=dict(color='yellow', width=1), name='EMA 50'))
    fig.add_trace(go.Scatter(x=df.index, y=df['ema200'], line=dict(color='blue', width=2), name='EMA 200 (Tren Utama)'))

    # JIKA ADA SINYAL BUY, GAMBAR KOTAK HIJAU/MERAH
    if signal_data:
        entry = signal_data['entry']
        tp = signal_data['tp']
        sl = signal_data['sl']
        
        # Waktu terakhir + masa depan (untuk menggambar kotak)
        last_time = df.index[-1]
        future_time = last_time + timedelta(hours=24) # Gambar kotak sampai besok
        
        # KOTAK HIJAU (PROFIT ZONE)
        fig.add_shape(type="rect",
            x0=last_time, y0=entry, x1=future_time, y1=tp,
            fillcolor="rgba(0, 255, 0, 0.3)", line=dict(color="green", width=2),
        )
        
        # KOTAK MERAH (LOSS ZONE)
        fig.add_shape(type="rect",
            x0=last_time, y0=sl, x1=future_time, y1=entry,
            fillcolor="rgba(255, 0, 0, 0.3)", line=dict(color="red", width=2),
        )
        
        # Label Harga di Kanan
        fig.add_annotation(x=future_time, y=tp, text=f"Target: ${tp:.4f}", showarrow=False, xanchor="left", font=dict(color="green"))
        fig.add_annotation(x=future_time, y=entry, text=f"Entry: ${entry:.4f}", showarrow=False, xanchor="left")
        fig.add_annotation(x=future_time, y=sl, text=f"Stop Loss: ${sl:.4f}", showarrow=False, xanchor="left", font=dict(color="red"))

    # Styling agar mirip TradingView
    fig.update_layout(
        title=f"Analisa Visual: {coin_name}",
        yaxis_title='Harga (USDT)',
        xaxis_rangeslider_visible=False,
        height=600,
        template="plotly_dark",
        showlegend=True
    )
    
    return fig

# --- LOGIKA UTAMA ---
if st.button("▶️ ANALISA SEKARANG", type="primary"):
    with st.spinner(f"Mengambil data Real-Time {selected_coin}..."):
        # 1. Ambil Data
        df_raw = get_data(selected_coin)
        
        if df_raw is not None and len(df_raw) > 200:
            # 2. Hitung Strategi
            df_calc, trend_status, signal = calculate_strategy(df_raw, risk_pct, rr_ratio)
            
            # 3. Tampilkan Hasil
            col_res, col_chart = st.columns([1, 3])
            
            with col_res:
                st.subheader("Hasil Analisa")
                st.write(f"Status Tren: **{trend_status}**")
                
                if signal:
                    st.success("✅ SINYAL BUY TERKONFIRMASI")
                    st.metric("ENTRY (Beli)", f"${signal['entry']:.4f}")
                    st.metric("TARGET (Jual)", f"${signal['tp']:.4f}", delta=f"+{signal['gain_pct']:.2f}%")
                    st.metric("STOP LOSS", f"${signal['sl']:.4f}", delta=f"{signal['loss_pct']:.2f}%", delta_color="inverse")
                    st.info(f"Rasio Risk:Reward = 1 : {rr_ratio}")
                else:
                    st.warning("⛔ BELUM ADA SINYAL BUY")
                    st.write("Alasan: Harga masih di bawah garis tren (EMA), atau tren belum kuat. Jangan masuk dulu.")
                    
            with col_chart:
                # 4. Gambar Grafik Visual
                fig = plot_visual_pro(df_calc, signal, selected_coin)
                st.plotly_chart(fig, use_container_width=True)
                
        else:
            st.error("Data tidak cukup untuk analisa tren jangka panjang.")
