import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import plotly.graph_objects as go
from datetime import timedelta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Oracle AI Crypto (WIB)", layout="wide")

# --- JUDUL UTAMA ---
st.title("👁️ ORACLE AI: Penjelajah Masa Depan (WIB)")
st.markdown("""
**Fitur Baru:**
1.  ✅ **Waktu Otomatis WIB (Jakarta):** Tidak perlu pusing hitung jam London.
2.  ✅ **Mode Dewa:** Mencari koin dengan potensi cuan tertinggi.
3.  ✅ **Estimasi Rupiah:** Langsung hitung potensi keuntungan uang Anda.
""")

# --- DAFTAR KOIN ---
WATCHLIST = [
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 
    'DOGE-USD', 'SHIB-USD', 'PEPE-USD', 'ADA-USD', 'AVAX-USD',
    'TRX-USD', 'LINK-USD', 'MATIC-USD', 'DOT-USD', 'LTC-USD',
    'BCH-USD', 'NEAR-USD', 'UNI-USD', 'ICP-USD', 'FIL-USD',
    'GALA-USD', 'SAND-USD', 'MANA-USD', 'ARB-USD', 'SUI-USD'
]

# --- SIDEBAR ---
st.sidebar.header("💰 Pusat Komando")
modal_input = st.sidebar.number_input("Modal Investasi (Rupiah)", min_value=100000, value=1000000, step=100000)
interval_pilihan = st.sidebar.selectbox("Pilih Timeframe", ["30m (30 Menit)", "1h (Per Jam)", "90m (1.5 Jam)"])

yf_interval = "1h"
if interval_pilihan == "30m": yf_interval = "30m"
elif interval_pilihan == "90m": yf_interval = "90m"

# --- FUNGSI AI (DENGAN PERBAIKAN WIB) ---
def ramal_koin(ticker, modal_idr):
    try:
        # 1. Ambil Data
        data = yf.download(ticker, period='5d', interval=yf_interval, progress=False)
        
        if len(data) < 20: return None
        
        # Fix MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
            
        df = data[['Close']].dropna()
        
        # --- PERBAIKAN ZONA WAKTU (UBAH KE WIB) ---
        # Kita paksa geser jamnya +7 jam agar sesuai Jakarta
        df.index = df.index + pd.Timedelta(hours=7)
        
        current_price = df['Close'].iloc[-1]
        if isinstance(current_price, pd.Series): current_price = current_price.item()

        # 2. Persiapan Data LSTM
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(df.values)
        
        lookback = 15 # Kita perpendek lookback agar lebih responsif untuk scalping
        
        x_train, y_train = [], []
        for i in range(lookback, len(scaled_data)):
            x_train.append(scaled_data[i-lookback:i, 0])
            y_train.append(scaled_data[i, 0])
            
        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

        # 3. Model AI
        model = Sequential()
        model.add(LSTM(units=30, return_sequences=False, input_shape=(x_train.shape[1], 1)))
        model.add(Dense(units=1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(x_train, y_train, epochs=5, batch_size=16, verbose=0)

        # 4. Prediksi Masa Depan
        future_prices = []
        last_sequence = scaled_data[-lookback:]
        current_step = last_sequence.reshape(1, lookback, 1)
        
        for _ in range(5): 
            next_val = model.predict(current_step, verbose=0)
            future_prices.append(next_val[0, 0])
            current_step = np.append(current_step[:, 1:, :], [next_val], axis=1)
            
        future_prices = scaler.inverse_transform(np.array(future_prices).reshape(-1, 1))
        final_future_price = float(future_prices[-1][0])
        
        # Hitung Profit
        change_pct = ((final_future_price - current_price) / current_price) * 100
        estimasi_profit_idr = (change_pct / 100) * modal_idr
        
        return {
            "ticker": ticker,
            "current_price": current_price,
            "future_price": final_future_price,
            "change_pct": change_pct,
            "profit_idr": estimasi_profit_idr,
            "history_df": df,
            "future_array": future_prices
        }

    except Exception as e:
        return None

# --- UI UTAMA ---
st.write("---")

tab1, tab2 = st.tabs(["🚀 SCANNER (Cari Cuan)", "📈 ANALISA MANUAL"])

# === TAB 1: SCANNER ===
with tab1:
    st.header("🔍 Scanner Sinyal Terbaik (WIB)")
    if st.button("Mulai Scanning Pasar ⚡"):
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, coin in enumerate(WATCHLIST):
            status_text.text(f"Sedang membedah otak {coin}...")
            res = ramal_koin(coin, modal_input)
            if res:
                results.append(res)
            progress_bar.progress((i + 1) / len(WATCHLIST))
            
        status_text.text("Selesai!")
        
        # Urutkan
        results.sort(key=lambda x: x['change_pct'], reverse=True)
        best_coin = results[0]
        
        st.success(f"💎 **JUARA HARI INI: {best_coin['ticker']}**")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Harga Saat Ini", f"${best_coin['current_price']:,.5f}")
        col2.metric("Target Nanti", f"${best_coin['future_price']:,.5f}", delta=f"{best_coin['change_pct']:.2f}%")
        col3.metric("Estimasi Cuan", f"Rp {best_coin['profit_idr']:,.0f}")
        
        # --- PLOT GRAFIK ---
        st.subheader(f"Grafik Masa Depan: {best_coin['ticker']}")
        
        df_hist = best_coin['history_df']
        future_vals = best_coin['future_array'].flatten()
        
        # Bikin Tanggal Masa Depan (Start dari data terakhir yg sudah +7 jam)
        last_date = df_hist.index[-1]
        freq = '1h' if '1h' in yf_interval else '30min'
        future_dates = pd.date_range(start=last_date + pd.Timedelta(minutes=30), periods=5, freq=freq)
        
        fig = go.Figure()
        # Garis Biru
        fig.add_trace(go.Scatter(x=df_hist.index[-50:], y=df_hist['Close'].iloc[-50:], mode='lines', name='Waktu WIB (Nyata)', line=dict(color='cyan')))
        
        # Garis Merah (Sambungan)
        connect_x = [df_hist.index[-1], future_dates[0]]
        connect_y = [df_hist['Close'].iloc[-1], future_vals[0]]
        fig.add_trace(go.Scatter(x=connect_x, y=connect_y, mode='lines', showlegend=False, line=dict(color='red', dash='dot')))
        
        # Garis Merah (Masa Depan)
        fig.add_trace(go.Scatter(x=future_dates, y=future_vals, mode='lines+markers', name='PREDIKSI MASA DEPAN', line=dict(color='red', width=3)))
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("---")
        st.write("**Top 5 Alternatif Lain:**")
        # Tabel Top 5
        ranking_data = []
        for r in results[1:6]:
            ranking_data.append([r['ticker'], f"{r['change_pct']:.2f}%", f"Rp {r['profit_idr']:,.0f}"])
        st.table(pd.DataFrame(ranking_data, columns=["Koin", "Potensi", "Estimasi Cuan"]))

# === TAB 2: MANUAL ===
with tab2:
    st.header("Cek Koin Pilihan Anda")
    manual_ticker = st.text_input("Kode Koin", "PEPE-USD").upper()
    
    if st.button("Ramal Koin Ini"):
        with st.spinner("AI sedang berpikir..."):
            res = ramal_koin(manual_ticker, modal_input)
            
            if res:
                st.metric("Potensi Profit", f"{res['change_pct']:.2f}%", f"Rp {res['profit_idr']:,.0f}")
                
                df_hist = res['history_df']
                future_vals = res['future_array'].flatten()
                last_date = df_hist.index[-1]
                freq = '1h' if '1h' in yf_interval else '30min'
                future_dates = pd.date_range(start=last_date + pd.Timedelta(minutes=30), periods=5, freq=freq)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_hist.index[-50:], y=df_hist['Close'].iloc[-50:], mode='lines', name='WIB Sekarang', line=dict(color='cyan')))
                
                fig.add_trace(go.Scatter(x=[df_hist.index[-1], future_dates[0]], y=[df_hist['Close'].iloc[-1], future_vals[0]], mode='lines', showlegend=False, line=dict(color='red', dash='dot')))
                
                fig.add_trace(go.Scatter(x=future_dates, y=future_vals, mode='lines+markers', name='MASA DEPAN', line=dict(color='red', width=3)))
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Gagal. Cek kode koin.")
