import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
import random

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Oracle AI: Hype Hunter", layout="wide")

st.title("👁️ ORACLE AI: Hype & Micin Hunter (< Rp 10.000)")
st.markdown("""
**Fitur Baru (God Mode):**
1.  🔥 **Hype Detector:** Mendeteksi "keramaian internet" melalui ledakan volume tak wajar.
2.  💰 **Filter Harga:** Hanya memproses koin di bawah **Rp 10.000**.
3.  🎲 **Random Batch:** Mengambil sampel acak dari ratusan koin Tokocrypto agar server tidak crash.
""")

# --- DATABASE KOIN MASIF (DARI USER) ---
# Format asli user: XXX/USDT. Kita simpan raw dulu.
RAW_WATCHLIST = [
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
    "MEME/USDT", "HUMA/USDT", "MASK/USDT", "ALT/USDT", "POLY/USDT", "SKL/USDT", "ICX/USDT", 
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
    "CTSI/USDT", "TNSR/USDT"
]

# --- SIDEBAR PENGATURAN ---
st.sidebar.header("🎛️ Pengaturan Scanner")
modal_input = st.sidebar.number_input("Modal Trading (Rp)", min_value=100000, value=1000000, step=100000)
kurs_usd_idr = st.sidebar.number_input("Kurs USD/IDR", value=16000)
batas_harga = 10000 # Batas Rp 10.000

st.sidebar.info("Timeframe: 15 Menit (Fixed)")
yf_interval = "15m"

# --- FUNGSI FORMAT TICKER ---
def format_ticker(raw_ticker):
    # Mengubah HEI/USDT menjadi HEI-USD (Format Yahoo Finance)
    return raw_ticker.replace("/USDT", "-USD")

# --- FUNGSI CEK HYPE INTERNET (VOLUME SPIKE) ---
def cek_hype_score(df):
    """
    Menghitung skor hype berdasarkan lonjakan volume.
    Jika Volume sekarang > 3x Rata-rata Volume, berarti lagi HYPE (Viral).
    """
    try:
        current_vol = df['Volume'].iloc[-1]
        avg_vol = df['Volume'].mean()
        
        # Ratio Volume
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 0
        
        hype_label = "Sepi"
        hype_score = 0
        
        if vol_ratio > 5.0:
            hype_label = "🔥 VIRAL/FOMO (Internet Ramai)"
            hype_score = 100
        elif vol_ratio > 3.0:
            hype_label = "⚡ Ramai (High Hype)"
            hype_score = 80
        elif vol_ratio > 1.5:
            hype_label = "📈 Mulai Dilirik"
            hype_score = 50
        else:
            hype_label = "💤 Normal/Sepi"
            hype_score = 20
            
        return hype_label, vol_ratio
    except:
        return "Unknown", 0

# --- FUNGSI AI CORE ---
def ramal_koin(raw_ticker):
    ticker = format_ticker(raw_ticker)
    
    try:
        # Ambil data pendek (20 hari, 15 menit)
        data = yf.download(ticker, period='20d', interval=yf_interval, progress=False)
        
        if len(data) < 40: return None
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
            
        df = data[['Close', 'Volume']].dropna()
        
        # --- FILTER HARGA DI BAWAH 10 RIBU ---
        current_price_usd = df['Close'].iloc[-1]
        if isinstance(current_price_usd, pd.Series): current_price_usd = current_price_usd.item()
        
        current_price_idr = current_price_usd * kurs_usd_idr
        
        # Jika harga > 10.000, SKIP (Return None)
        if current_price_idr > batas_harga:
            return None 

        # FIX WAKTU WIB
        df.index = df.index + pd.Timedelta(hours=7)

        # --- INDIKATOR TEKNIS LENGKAP ---
        # 1. RSI
        df['RSI'] = RSIIndicator(close=df['Close'], window=14).rsi()
        # 2. EMA 20 (Tren)
        df['EMA'] = EMAIndicator(close=df['Close'], window=20).ema_indicator()
        # 3. MACD
        macd = MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        
        df.dropna(inplace=True)

        # --- CEK HYPE ---
        hype_status, vol_ratio = cek_hype_score(df)
        
        # --- AI PREDICTION ---
        scaler = MinMaxScaler(feature_range=(0, 1))
        # Fitur: Close, RSI, MACD
        features = df[['Close', 'RSI', 'MACD']].values
        scaled_data = scaler.fit_transform(features)
        
        lookback = 20
        x_train, y_train = [], []
        for i in range(lookback, len(scaled_data)):
            x_train.append(scaled_data[i-lookback:i, :])
            y_train.append(scaled_data[i, 0])
            
        x_train, y_train = np.array(x_train), np.array(y_train)
        
        # Model
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=(x_train.shape[1], 3)))
        model.add(Dropout(0.2))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(x_train, y_train, epochs=5, batch_size=16, verbose=0)
        
        # Prediksi Masa Depan
        last_seq = scaled_data[-lookback:].reshape(1, lookback, 3)
        future_prices = []
        
        for _ in range(5):
            pred = model.predict(last_seq, verbose=0)[0, 0]
            future_prices.append(pred)
            # Dummy update
            new_step = np.array([[[pred, last_seq[0,-1,1], last_seq[0,-1,2]]]])
            last_seq = np.append(last_seq[:, 1:, :], new_step, axis=1)
            
        # Inverse transform
        dummy = np.zeros((5, 3))
        dummy[:, 0] = future_prices
        real_future = scaler.inverse_transform(dummy)[:, 0]
        final_price = real_future[-1]
        
        change_pct = ((final_price - current_price_usd) / current_price_usd) * 100
        
        # LOGIKA FILTER DUMP (Cegah beli saat longsor)
        trend_label = "NETRAL"
        if df['Close'].iloc[-1] < df['EMA'].iloc[-1]:
            trend_label = "DOWNTREND (Risiko Tinggi)"
            if change_pct > 0: change_pct = change_pct * 0.2 # Kurangi optimisme AI
        else:
            trend_label = "UPTREND (Aman)"
            
        profit_idr = (change_pct / 100) * modal_input

        return {
            "ticker": raw_ticker,
            "price_idr": current_price_idr,
            "future_price": final_price,
            "change_pct": change_pct,
            "profit_idr": profit_idr,
            "hype": hype_status,
            "trend": trend_label,
            "df": df,
            "future_array": real_future
        }

    except:
        return None

# --- UI UTAMA ---
st.write("---")

tab1, tab2 = st.tabs(["🎲 SCANNER ACAK (Batch)", "🔍 CEK MANUAL"])

with tab1:
    st.header("Scanner Batch (Acak 20 Koin)")
    st.write(f"Database memuat **{len(RAW_WATCHLIST)} koin**. Klik tombol untuk mengambil 20 sampel acak & memfilter harga < Rp 10.000.")
    
    if st.button("Ambil 20 Sampel & Scan 🔥"):
        
        # AMBIL 20 SAMPLE ACAK DARI LIST BESAR
        batch_coins = random.sample(RAW_WATCHLIST, 20)
        
        results = []
        progress = st.progress(0)
        status = st.empty()
        
        valid_count = 0
        
        for i, coin in enumerate(batch_coins):
            status.text(f"Mengecek {coin}... (Filter < 10k)")
            res = ramal_koin(coin)
            
            # Jika lolos filter (tidak None)
            if res:
                results.append(res)
                valid_count += 1
            
            progress.progress((i + 1) / 20)
            
        status.text("Selesai!")
        
        if len(results) > 0:
            # Urutkan berdasarkan Potensi Cuan
            results.sort(key=lambda x: x['change_pct'], reverse=True)
            top = results[0]
            
            st.success(f"💎 **JUARA BATCH INI: {top['ticker']}**")
            st.caption(f"Status Internet: {top['hype']} | Tren: {top['trend']}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Harga (Rp)", f"Rp {top['price_idr']:,.2f}")
            c2.metric("Target AI", f"{top['change_pct']:.2f}%")
            c3.metric("Potensi Cuan", f"Rp {top['profit_idr']:,.0f}")
            
            # Grafik
            st.subheader(f"Grafik: {top['ticker']}")
            df = top['df']
            future_vals = top['future_array']
            last_date = df.index[-1]
            future_dates = pd.date_range(start=last_date + pd.Timedelta(minutes=15), periods=5, freq='15min')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index[-40:], y=df['Close'].iloc[-40:], mode='lines', name='Harga', line=dict(color='cyan')))
            
            col_line = 'lime' if top['change_pct'] > 0 else 'red'
            fig.add_trace(go.Scatter(x=future_dates, y=future_vals, mode='lines+markers', name='Prediksi', line=dict(color=col_line, width=3)))
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.write("---")
            st.write("**Hasil Scan Lainnya (Lolos Filter Harga):**")
            
            rows = []
            for r in results[1:]:
                rows.append([r['ticker'], f"Rp {r['price_idr']:,.2f}", r['hype'], f"{r['change_pct']:.2f}%", f"Rp {r['profit_idr']:,.0f}"])
            
            st.table(pd.DataFrame(rows, columns=["Koin", "Harga", "Kondisi Internet", "Potensi", "Cuan"]))
            
        else:
            st.warning("Dari 20 sampel acak ini, tidak ada yang lolos filter (Mungkin harganya > 10rb atau data error). Coba klik scan lagi!")

with tab2:
    st.header("Cek Manual Dari Database")
    # Dropdown berisi semua koin user
    pilihan_manual = st.selectbox("Pilih Koin", RAW_WATCHLIST)
    
    if st.button("Cek Koin Ini"):
        with st.spinner("Mengecek..."):
            res = ramal_koin(pilihan_manual)
            
            if res:
                st.metric("Harga", f"Rp {res['price_idr']:,.2f}")
                st.metric("Kondisi Internet", res['hype'])
                st.metric("Potensi", f"{res['change_pct']:.2f}%", f"Rp {res['profit_idr']:,.0f}")
                
                # Grafik
                df = res['df']
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index[-40:], y=df['Close'].iloc[-40:], mode='lines', name='Harga', line=dict(color='cyan')))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Koin ini harganya di atas Rp 10.000 atau data belum tersedia di Yahoo Finance.")
