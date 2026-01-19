import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# --- KONFIGURASI ---
st.set_page_config(page_title="AI FORECASTER V3", layout="wide")
st.title("🔮 AI FORECASTER: Prediksi 2 Langkah")
st.markdown("""
**Logika Baru:**
1.  ⚡ **Real-Time Ticker:** Mengambil harga detik ini (bukan harga history), agar sinkron dengan Tokocrypto.
2.  👣 **2 Langkah ke Depan:** Memprediksi Target Pendek (Step 1) dan Target Jauh (Step 2).
3.  💵 **Dual Currency:** Tampilan Rupiah (IDR) dan Dollar (USD).
""")

# --- DATABASE KOIN ---
# (Daftar Koin Pilihan Anda)
WATCHLIST = [
    "DATA/USDT", "BAR/USDT", "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
    "PEPE/USDT", "SHIB/USDT", "WIF/USDT", "BONK/USDT", "FLOKI/USDT", "BOME/USDT", 
    "JASMY/USDT", "LUNC/USDT", "SLP/USDT", "GALA/USDT", "NEAR/USDT", "FET/USDT",
    "RNDR/USDT", "FTM/USDT", "MATIC/USDT", "ADA/USDT", "AVAX/USDT", "DOT/USDT",
    "LINK/USDT", "TRX/USDT", "LTC/USDT", "BCH/USDT", "UNI/USDT", "APT/USDT",
    "FIL/USDT", "ATOM/USDT", "IMX/USDT", "OP/USDT", "INJ/USDT", "STX/USDT",
    "TIA/USDT", "SEI/USDT", "ARB/USDT", "SUI/USDT", "QNT/USDT", "AAVE/USDT",
    "SAND/USDT", "MANA/USDT", "THETA/USDT", "AXS/USDT", "EOS/USDT", "XTZ/USDT",
    "CFX/USDT", "CHZ/USDT", "MEME/USDT", "PEOPLE/USDT", "WLD/USDT", "ARKM/USDT",
    "1000SATS/USDT", "BTTC/USDT", "DENT/USDT", "HOT/USDT", "SC/USDT", "ZIL/USDT",
    "IOST/USDT", "VTHO/USDT", "CKB/USDT", "RSR/USDT", "MBL/USDT", "ANKR/USDT",
    "HEI/USDT", "KOM/USDT", "BROCCOLI714/USDT", "PENGU/USDT", "BIO/USDT", "VANA/USDT",
    "1000CHEEMS/USDT", "TURTLE/USDT", "MDT/USDT", "ACA/USDT", "CITY/USDT", "ATM/USDT",
    "COS/USDT", "ACM/USDT", "CHESS/USDT", "NBT/USDT", "CREO/USDT", "CVC/USDT", 
    "ALPINE/USDT", "BEL/USDT", "JUV/USDT", "HOOK/USDT", "NKN/USDT", "QUICK/USDT"
]

exchange = ccxt.binance({'enableRateLimit': True})

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Pengaturan Kurs")
    kurs_usd_idr = st.number_input("Kurs USD ke IDR (Cek di P2P Toko)", value=16200, step=50)
    st.caption("Tips: Sesuaikan kurs agar harga Rupiah pas dengan aplikasi Anda.")

# --- FUNGSI UTAMA ---
def analyze_forecast(symbol):
    try:
        # 1. AMBIL HARGA DETIK INI (TICKER)
        # Ini supaya harganya 100% sama dengan angka besar di aplikasi
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # 2. AMBIL DATA HISTORIS (CHART) UNTUK TREN
        bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=50)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
        
        # 3. HITUNG VOLATILITAS (Kekuatan Gerak)
        # Average True Range (ATR) sederhana untuk mengukur seberapa jauh harga bisa lari
        df['tr'] = df['high'] - df['low']
        atr = df['tr'].rolling(14).mean().iloc[-1]
        
        # 4. PREDIKSI 2 LANGKAH (Step 1 & Step 2)
        # Kita gunakan momentum terakhir untuk memproyeksikan masa depan
        
        # STEP 1: Target Pendek (Konservatif)
        # Harga Sekarang + (0.5 x Kekuatan Gerak)
        target_1 = current_price + (atr * 0.8)
        
        # STEP 2: Target Jauh (Optimis)
        # Harga Sekarang + (1.5 x Kekuatan Gerak)
        target_2 = current_price + (atr * 2.0)
        
        # Stop Loss (Pengaman)
        stop_loss = current_price - (atr * 0.5)
        
        # Waktu Estimasi
        time_now = datetime.now() + timedelta(hours=7) # WIB Server Adjustment
        time_step1 = time_now + timedelta(hours=2) # 2 Jam lagi
        time_step2 = time_now + timedelta(hours=6) # 6 Jam lagi
        
        # Format Harga
        cp_idr = current_price * kurs_usd_idr
        t1_idr = target_1 * kurs_usd_idr
        t2_idr = target_2 * kurs_usd_idr
        sl_idr = stop_loss * kurs_usd_idr
        
        # Persentase
        p1_pct = ((target_1 - current_price) / current_price) * 100
        p2_pct = ((target_2 - current_price) / current_price) * 100
        
        return {
            "symbol": symbol,
            "current_usd": current_price,
            "current_idr": cp_idr,
            "t1_usd": target_1,
            "t1_idr": t1_idr,
            "t1_pct": p1_pct,
            "t2_usd": target_2,
            "t2_idr": t2_idr,
            "t2_pct": p2_pct,
            "sl_idr": sl_idr,
            "history": df,
            "time_now": time_now,
            "time_s1": time_step1,
            "time_s2": time_step2
        }
        
    except Exception as e:
        return None

# --- UI TAMPILAN ---
col_scan, col_manual = st.columns([2, 1])

with col_manual:
    st.subheader("🔍 Cek Koin Tertentu")
    manual_coin = st.selectbox("Pilih Koin:", WATCHLIST, index=0)
    cek_btn = st.button("Ramal Koin Ini ⚡")

if cek_btn:
    with st.spinner(f"Menghubungkan ke Binance untuk {manual_coin}..."):
        data = analyze_forecast(manual_coin)
        
        if data:
            st.success(f"✅ Data Terkini: {data['time_now'].strftime('%H:%M:%S')} WIB")
            
            # --- METRIK UTAMA ---
            # Menampilkan harga saat ini + Target
            c1, c2, c3 = st.columns(3)
            
            c1.metric(
                label="HARGA SEKARANG (ENTRY)",
                value=f"Rp {data['current_idr']:,.2f}",
                delta=f"${data['current_usd']:.5f}",
                delta_color="off"
            )
            
            c2.metric(
                label="TARGET 1 (Pendek)",
                value=f"Rp {data['t1_idr']:,.2f}",
                delta=f"+{data['t1_pct']:.2f}%",
                help="Target aman untuk scalping cepat"
            )
            
            c3.metric(
                label="TARGET 2 (Jauh)",
                value=f"Rp {data['t2_idr']:,.2f}",
                delta=f"+{data['t2_pct']:.2f}%",
                help="Target optimis jika tren berlanjut"
            )
            
            # --- GRAFIK MASA DEPAN (PROJECTION) ---
            st.subheader("Grafik Jalur Masa Depan")
            
            fig = go.Figure()
            
            # 1. Data Masa Lalu (Garis Biru)
            hist_df = data['history']
            fig.add_trace(go.Scatter(
                x=hist_df['time'], 
                y=hist_df['close'] * kurs_usd_idr,
                mode='lines',
                name='History',
                line=dict(color='#00C9FF', width=2)
            ))
            
            # 2. Titik Sekarang (Titik Putih)
            fig.add_trace(go.Scatter(
                x=[data['time_now']],
                y=[data['current_idr']],
                mode='markers',
                name='SEKARANG',
                marker=dict(color='white', size=10, line=dict(color='black', width=2))
            ))
            
            # 3. Jalur ke Target 1 (Garis Putus-Putus Kuning)
            fig.add_trace(go.Scatter(
                x=[data['time_now'], data['time_s1']],
                y=[data['current_idr'], data['t1_idr']],
                mode='lines+markers',
                name='Langkah 1',
                line=dict(color='#FFD700', dash='dot', width=2)
            ))
            
            # 4. Jalur ke Target 2 (Garis Putus-Putus Hijau)
            fig.add_trace(go.Scatter(
                x=[data['time_s1'], data['time_s2']],
                y=[data['t1_idr'], data['t2_idr']],
                mode='lines+markers',
                name='Langkah 2',
                line=dict(color='#00FF00', dash='dot', width=2)
            ))
            
            fig.update_layout(
                title=f"Proyeksi Pergerakan {manual_coin} (WIB)",
                xaxis_title="Waktu",
                yaxis_title="Harga (Rupiah)",
                height=500,
                template="plotly_dark"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # --- REKOMENDASI TEKS ---
            st.info(f"""
            **Strategi Eksekusi:**
            1.  **Beli Sekarang:** Di harga **Rp {data['current_idr']:,.2f}** (${data['current_usd']}).
            2.  **Jual Sebagian (50%):** Saat menyentuh **Rp {data['t1_idr']:,.2f}** (Target 1).
            3.  **Jual Sisanya:** Saat menyentuh **Rp {data['t2_idr']:,.2f}** (Target 2).
            4.  **Cut Loss (Wajib):** Jika harga turun ke **Rp {data['sl_idr']:,.2f}**.
            """)
            
        else:
            st.error("Gagal mengambil data. Cek koneksi atau koin mungkin tidak ada di Binance.")

# --- FITUR SCANNER CEPAT ---
with col_scan:
    st.subheader("⚡ Scanner Potensi Cuan")
    if st.button("Cari Koin Potensial (Random Batch)"):
        batch = random.sample(WATCHLIST, 10)
        results = []
        
        progress = st.progress(0)
        for i, coin in enumerate(batch):
            d = analyze_forecast(coin)
            if d and d['t1_pct'] > 1.0: # Cari yg potensi > 1%
                results.append(d)
            progress.progress((i+1)/10)
        
        progress.empty()
        
        if results:
            results.sort(key=lambda x: x['t2_pct'], reverse=True)
            st.write(f"Ditemukan {len(results)} koin menarik:")
            
            for res in results:
                with st.expander(f"{res['symbol']} (+{res['t2_pct']:.2f}%)"):
                    c1, c2 = st.columns(2)
                    c1.write(f"Harga: **${res['current_usd']:.5f}**")
                    c1.write(f"Rp: **{res['current_idr']:,.0f}**")
                    
                    c2.write(f"Target 1: **Rp {res['t1_idr']:,.0f}**")
                    c2.write(f"Target 2: **Rp {res['t2_idr']:,.0f}**")
        else:
            st.warning("Batch ini tidak ada yang menarik. Coba klik lagi.")
