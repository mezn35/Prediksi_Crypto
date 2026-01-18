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
st.set_page_config(page_title="Oracle AI Crypto", layout="wide")

# --- JUDUL UTAMA ---
st.title("👁️ ORACLE AI: Penjelajah Masa Depan")
st.markdown("""
**Mode Dewa Aktif:**
1.  AI mencari sendiri koin terbaik untuk dibeli dari daftar Top Asset.
2.  Grafik Prediksi "Menjalar" ke masa depan (bukan menumpuk data lama).
3.  Prediksi jangka pendek (Per Jam/Menit) dengan estimasi keuntungan Rupiah.
""")

# --- DAFTAR KOIN YANG AKAN DISCAN AI ---
# Kita batasi 20-30 koin top agar server gratisan tidak meledak (timeout)
WATCHLIST = [
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 
    'DOGE-USD', 'SHIB-USD', 'PEPE-USD', 'ADA-USD', 'AVAX-USD',
    'TRX-USD', 'LINK-USD', 'MATIC-USD', 'DOT-USD', 'LTC-USD',
    'BCH-USD', 'NEAR-USD', 'UNI-USD', 'ICP-USD', 'FIL-USD'
]

# --- SIDEBAR PENGATURAN ---
st.sidebar.header("💰 Pusat Komando")
modal_input = st.sidebar.number_input("Modal Investasi Anda (Rupiah)", min_value=100000, value=1000000, step=100000)
kurs_usd_idr = st.sidebar.number_input("Kurs USD ke IDR", value=16000)
interval_pilihan = st.sidebar.selectbox("Pilih Timeframe", ["1h (Per Jam)", "30m (30 Menit)", "90m (1.5 Jam)"])

# Konversi interval untuk Yahoo Finance
yf_interval = "1h"
if interval_pilihan == "30m": yf_interval = "30m"
elif interval_pilihan == "90m": yf_interval = "90m"

# --- FUNGSI OTAK AI ---
def ramal_koin(ticker, modal_idr):
    try:
        # 1. Ambil Data Pendek (7 Hari terakhir tapi per jam/menit untuk presisi)
        # yfinance limitasi: data intraday (jam/menit) cuma tersedia 60 hari terakhir max
        data = yf.download(ticker, period='1mo', interval=yf_interval, progress=False)
        
        if len(data) < 50: return None # Skip jika data tidak cukup
        
        # Bersihkan MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
            
        df = data[['Close']].dropna()
        current_price = df['Close'].iloc[-1]
        if isinstance(current_price, pd.Series): current_price = current_price.item()

        # 2. Persiapan Data LSTM
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(df.values)
        
        lookback = 30 # Belajar dari 30 candle ke belakang
        
        x_train, y_train = [], []
        for i in range(lookback, len(scaled_data)):
            x_train.append(scaled_data[i-lookback:i, 0])
            y_train.append(scaled_data[i, 0])
            
        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

        # 3. Model Ringan (Supaya scanning cepat)
        model = Sequential()
        model.add(LSTM(units=30, return_sequences=False, input_shape=(x_train.shape[1], 1)))
        model.add(Dense(units=1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(x_train, y_train, epochs=5, batch_size=16, verbose=0)

        # 4. Prediksi 5 Langkah ke Depan (Masa Depan)
        future_prices = []
        last_sequence = scaled_data[-lookback:] # Ambil 30 data terakhir asli
        
        current_step = last_sequence.reshape(1, lookback, 1)
        
        for _ in range(5): # Ramal 5 lilin ke depan
            next_val = model.predict(current_step, verbose=0)
            future_prices.append(next_val[0, 0])
            # Update sequence dengan hasil prediksi untuk prediksi berikutnya
            current_step = np.append(current_step[:, 1:, :], [next_val], axis=1)
            
        # Kembalikan ke harga asli
        future_prices = scaler.inverse_transform(np.array(future_prices).reshape(-1, 1))
        final_future_price = float(future_prices[-1][0]) # Harga di ujung prediksi (langkah ke-5)
        
        # Hitung Potensi
        change_pct = ((final_future_price - current_price) / current_price) * 100
        estimasi_profit_idr = (change_pct / 100) * modal_idr
        
        return {
            "ticker": ticker,
            "current_price": current_price,
            "future_price": final_future_price,
            "change_pct": change_pct,
            "profit_idr": estimasi_profit_idr,
            "history_df": df, # Simpan data untuk plotting nanti
            "future_array": future_prices
        }

    except Exception as e:
        return None

# --- UI UTAMA ---
st.write("---")

tab1, tab2 = st.tabs(["🚀 SCANNER (Cari Cuan)", "📈 ANALISA MANUAL"])

# === TAB 1: SCANNER OTOMATIS ===
with tab1:
    st.header("🔍 Scanner Sinyal Terbaik (Top 20 Koin)")
    if st.button("Mulai Scanning Seluruh Pasar (Mungkin butuh 1-2 menit)"):
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Loop scanning
        for i, coin in enumerate(WATCHLIST):
            status_text.text(f"Sedang membedah otak {coin}...")
            res = ramal_koin(coin, modal_input)
            if res:
                results.append(res)
            progress_bar.progress((i + 1) / len(WATCHLIST))
            
        status_text.text("Scanning Selesai!")
        
        # Urutkan dari Profit Tertinggi ke Terendah
        results.sort(key=lambda x: x['change_pct'], reverse=True)
        
        # Tampilkan Sang Juara (Top Pick)
        best_coin = results[0]
        
        st.success(f"💎 **REKOMENDASI AI: {best_coin['ticker']}**")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Harga Sekarang", f"${best_coin['current_price']:,.4f}")
        col2.metric("Target Masa Depan", f"${best_coin['future_price']:,.4f}", delta=f"{best_coin['change_pct']:.2f}%")
        col3.metric("Estimasi Cuan (Rp)", f"Rp {best_coin['profit_idr']:,.0f}")
        
        st.write(f"**Saran AI:** Jika Anda beli **{best_coin['ticker']}** sekarang senilai **Rp {modal_input:,.0f}**, AI memprediksi aset Anda akan menjadi **Rp {(modal_input + best_coin['profit_idr']):,.0f}** dalam beberapa jam ke depan.")
        
        # --- PLOT GRAFIK MASA DEPAN SANG JUARA ---
        st.subheader(f"Grafik Masa Depan: {best_coin['ticker']}")
        
        df_hist = best_coin['history_df']
        future_vals = best_coin['future_array'].flatten()
        
        # Bikin Tanggal Masa Depan
        last_date = df_hist.index[-1]
        freq = '1h' if '1h' in yf_interval else '30min'
        future_dates = pd.date_range(start=last_date + pd.Timedelta(minutes=30), periods=5, freq=freq)
        
        fig = go.Figure()
        # Garis Biru (Masa Lalu)
        fig.add_trace(go.Scatter(x=df_hist.index, y=df_hist['Close'], mode='lines', name='Harga Historis (Nyata)', line=dict(color='cyan')))
        # Garis Merah Putus-putus (Masa Depan)
        # Kita sambungkan titik terakhir historis ke titik pertama prediksi biar garisnya nyambung
        connect_x = [df_hist.index[-1], future_dates[0]]
        connect_y = [df_hist['Close'].iloc[-1], future_vals[0]]
        fig.add_trace(go.Scatter(x=connect_x, y=connect_y, mode='lines', showlegend=False, line=dict(color='red', dash='dot')))
        
        fig.add_trace(go.Scatter(x=future_dates, y=future_vals, mode='lines+markers', name='PREDIKSI AI (Future)', line=dict(color='red', width=3)))
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("---")
        st.write("**Peringkat Koin Lainnya:**")
        # Tampilkan tabel sisa
        ranking_data = []
        for r in results[1:]:
            ranking_data.append([r['ticker'], f"{r['change_pct']:.2f}%", f"Rp {r['profit_idr']:,.0f}"])
        st.table(pd.DataFrame(ranking_data, columns=["Koin", "Potensi Naik", "Estimasi Cuan"]))

# === TAB 2: MANUAL INPUT ===
with tab2:
    st.header("Analisa Koin Pilihan Sendiri")
    manual_ticker = st.text_input("Ketik Kode Koin (Contoh: PEPE-USD, GALA-USD)", "PEPE-USD").upper()
    
    if st.button("Ramal Koin Ini"):
        with st.spinner("AI sedang menerawang..."):
            res = ramal_koin(manual_ticker, modal_input)
            
            if res:
                st.metric("Potensi Profit", f"{res['change_pct']:.2f}%", f"Rp {res['profit_idr']:,.0f}")
                
                # Visualisasi Sama seperti di atas
                df_hist = res['history_df']
                future_vals = res['future_array'].flatten()
                last_date = df_hist.index[-1]
                freq = '1h' if '1h' in yf_interval else '30min'
                future_dates = pd.date_range(start=last_date + pd.Timedelta(minutes=30), periods=5, freq=freq)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_hist.index, y=df_hist['Close'], mode='lines', name='Sekarang', line=dict(color='cyan')))
                
                # Garis Sambung
                fig.add_trace(go.Scatter(
                    x=[df_hist.index[-1], future_dates[0]], 
                    y=[df_hist['Close'].iloc[-1], future_vals[0]], 
                    mode='lines', showlegend=False, line=dict(color='red', dash='dot')
                ))
                
                fig.add_trace(go.Scatter(x=future_dates, y=future_vals, mode='lines+markers', name='MASA DEPAN', line=dict(color='red', width=3)))
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Gagal mengambil data koin tersebut. Coba kode lain.")
