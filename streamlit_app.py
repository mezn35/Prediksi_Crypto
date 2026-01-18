import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI Crypto Pro", layout="wide")

st.title("🧠 AI Crypto Analyst (Level: Advanced)")
st.markdown("""
Sistem ini menggunakan **Multivariate LSTM** (Deep Learning).
Ia tidak hanya melihat harga, tapi juga membaca **RSI, MACD, dan Volume** layaknya trader profesional.
""")

# --- SIDEBAR ---
st.sidebar.header("🎛️ Pusat Kontrol")
ticker = st.sidebar.text_input("Simbol Crypto", "BTC-USD").upper()
epochs_setting = st.sidebar.slider("Tingkat Kecerdasan (Epochs)", 10, 50, 20)
st.sidebar.info("Semakin tinggi Epochs, semakin pintar tapi semakin lama prosesnya (bisa 3-5 menit).")

if st.sidebar.button("Jalankan Analisa Mendalam ⚡"):
    
    with st.spinner('Sedang mengunduh data, menghitung indikator, dan melatih otak AI... (Mohon bersabar)'):
        try:
            # 1. AMBIL DATA (Lebih banyak data: 4 Tahun)
            data = yf.download(ticker, period='4y', interval='1d', progress=False)
            
            if len(data) < 200:
                st.error("Data tidak cukup untuk analisa tingkat lanjut. Pilih koin yang lebih tua.")
                st.stop()

            # 2. FEATURE ENGINEERING (Menambahkan Indikator Teknis)
            df = data.copy()
            
            # Tambahkan RSI (Kekuatan Pasar)
            rsi = RSIIndicator(close=df['Close'], window=14)
            df['RSI'] = rsi.rsi()
            
            # Tambahkan MACD (Tren Momentum)
            macd = MACD(close=df['Close'])
            df['MACD'] = macd.macd()
            
            # Bersihkan data yang kosong (NaN) akibat perhitungan indikator
            df.dropna(inplace=True)
            
            # Kita hanya ambil kolom penting
            # Fitur yang dipelajari AI: Harga Close, Volume, RSI, MACD
            features = ['Close', 'Volume', 'RSI', 'MACD']
            dataset = df[features].values
            
            # 3. NORMALISASI DATA (Agar AI mudah belajar)
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(dataset)
            
            # 4. MEMBUAT DATA LATIHAN (MULTIVARIATE)
            lookback = 60 # Melihat 60 hari ke belakang
            
            X, y = [], []
            for i in range(lookback, len(scaled_data)):
                X.append(scaled_data[i-lookback:i, :]) # Ambil semua fitur (Close, Vol, RSI, MACD)
                y.append(scaled_data[i, 0]) # Target yang ditebak hanya 'Close' (indeks ke-0)
                
            X, y = np.array(X), np.array(y)
            
            # Pisahkan Data Latih (80%) dan Data Uji (20%) untuk Validasi Akurasi
            train_size = int(len(X) * 0.8)
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]

            # 5. BANGUN MODEL AI YANG LEBIH KOMPLEKS
            model = Sequential()
            # Layer 1
            model.add(LSTM(units=100, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
            model.add(Dropout(0.3))
            # Layer 2
            model.add(LSTM(units=100, return_sequences=False))
            model.add(Dropout(0.3))
            # Output Layer
            model.add(Dense(units=1))

            model.compile(optimizer='adam', loss='mean_squared_error')
            model.fit(X_train, y_train, epochs=epochs_setting, batch_size=32, verbose=0)

            # 6. PENGUJIAN AKURASI (BACKTESTING)
            # Prediksi pada data uji (masa lalu yang belum dilihat AI saat latihan)
            predicted_test = model.predict(X_test)
            
            # Kembalikan angka desimal 0-1 ke harga asli Dolar
            # Kita perlu trik karena scaler memuat 4 fitur, tapi kita cuma mau inverse 'Close'
            # Buat dummy array dengan bentuk yang sama
            dummy_array = np.zeros((len(predicted_test), len(features)))
            dummy_array[:, 0] = predicted_test.flatten()
            inverse_pred = scaler.inverse_transform(dummy_array)[:, 0]
            
            # Kembalikan harga asli y_test juga
            dummy_y = np.zeros((len(y_test), len(features)))
            dummy_y[:, 0] = y_test
            inverse_actual = scaler.inverse_transform(dummy_y)[:, 0]
            
            # 7. PREDIKSI MASA DEPAN (BESOK)
            last_60_days = scaled_data[-lookback:]
            X_future = np.array([last_60_days])
            pred_future_scaled = model.predict(X_future)
            
            dummy_future = np.zeros((1, len(features)))
            dummy_future[:, 0] = pred_future_scaled.flatten()
            future_price = scaler.inverse_transform(dummy_future)[0, 0]
            
            current_price = df['Close'].iloc[-1]
            diff = future_price - current_price
            change_pct = (diff / current_price) * 100

            # --- TAMPILAN HASIL ---
            st.divider()
            st.subheader(f"🔍 Analisa AI untuk {ticker}")
            
            # Metrik Utama
            col1, col2, col3 = st.columns(3)
            col1.metric("Harga Terakhir", f"${current_price:,.2f}")
            col2.metric("Prediksi AI (Besok)", f"${future_price:,.2f}", delta=f"{change_pct:.2f}%")
            
            # Indikator RSI
            last_rsi = df['RSI'].iloc[-1]
            rsi_status = "NETRAL"
            if last_rsi > 70: rsi_status = "OVERBOUGHT (Rawan Turun)"
            elif last_rsi < 30: rsi_status = "OVERSOLD (Potensi Naik)"
            
            col3.metric("Indikator RSI", f"{last_rsi:.1f}", rsi_status)

            # --- KESIMPULAN/SINYAL ---
            st.write("### 📝 Rekomendasi Tindakan")
            
            # Logika Gabungan (AI + RSI)
            if change_pct > 1.5 and last_rsi < 70:
                st.success(f"**STRONG BUY (BELI KUAT)** 🚀\n\nAI memprediksi kenaikan signifikan (+{change_pct:.2f}%) dan RSI belum jenuh ({last_rsi:.1f}). Momen bagus untuk masuk.")
            elif change_pct > 0.5:
                st.info(f"**BUY / ACCUMULATE (BELI BERTAHAP)** 🟢\n\nTren positif terlihat, tapi kenaikan mungkin perlahan.")
            elif change_pct < -1.5:
                st.error(f"**STRONG SELL / AVOID (JUAL/HINDARI)** 🔻\n\nAI mendeteksi potensi penurunan tajam. RSI ada di {last_rsi:.1f}. Sebaiknya amankan aset.")
            else:
                st.warning(f"**WAIT AND SEE (TUNGGU)** ⚠️\n\nPasar sedang tidak jelas (Sideways). Risiko tinggi jika memaksa masuk.")

            # --- BUKTI AKURASI (BACKTEST) ---
            st.write("---")
            st.write("### 🧪 Bukti Pengujian (Backtest)")
            st.caption("Grafik di bawah ini membandingkan prediksi AI (Garis Merah) vs Harga Asli (Garis Biru) pada data masa lalu. Jika garis merah menempel ketat dengan biru, artinya AI ini akurat.")
            
            # Visualisasi Backtest
            fig = go.Figure()
            # Ambil tanggal yang sesuai dengan data test
            test_dates = df.index[train_size+lookback:]
            
            fig.add_trace(go.Scatter(x=test_dates, y=inverse_actual, name='Harga Asli', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=test_dates, y=inverse_pred, name='Prediksi AI', line=dict(color='red', width=2)))
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Hitung Error Rata-rata
            mae = np.mean(np.abs(inverse_pred - inverse_actual))
            st.write(f"**Rata-rata Meleset (Mean Absolute Error):** ${mae:.2f}")
            st.write("*Semakin kecil angka 'Meleset', semakin akurat model ini.*")

        except Exception as e:
            st.error(f"Terjadi error: {e}. Coba refresh atau ganti kode crypto.")

else:
    st.info("Masukkan kode crypto di kiri dan tekan tombol untuk memulai analisa tingkat tinggi.")
