import streamlit as st
import numpy as np
import pandas as pd
import ccxt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
import random
from datetime import datetime, timedelta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Oracle AI: Ultimate List", layout="wide")

st.title("👁️ ORACLE AI: Ultimate Watchlist (USDT & IDR)")
st.markdown("""
**Fitur Terbaru:**
1.  📜 **Custom Watchlist:** Menggunakan daftar spesifik pilihan Anda (USDT & IDR).
2.  💱 **Smart IDR Conversion:** Analisa menggunakan data global (USDT) yang akurat, hasil ditampilkan dalam Rupiah.
3.  🛡️ **Filter < 10k:** Hanya menampilkan koin yang harganya masih murah.
""")

# --- DATABASE KOIN MASIF (DARI USER) ---
RAW_WATCHLIST = [
    # --- USDT PAIRS ---
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
    "MEME/USDT", "HUMA/USDT", "MASK/USDT", "ALT/USDT", "POLYX/USDT", "SKL/USDT", "ICX/USDT", 
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
    "CTSI/USDT", "TNSR/USDT",
    
    # --- IDR PAIRS (Akan dikonversi ke USDT untuk analisa) ---
    "BTC/IDR", "ETH/IDR", "USDT/IDR", "BNB/IDR", "XRP/IDR", "SOL/IDR", "USDC/IDR", 
    "DOGE/IDR", "ADA/IDR", "SUI/IDR", "AVAX/IDR", "HBAR/IDR", "TON/IDR", "TAO/IDR", 
    "ASTER/IDR", "POL/IDR", "WLD/IDR", "ARB/IDR", "ONDO/IDR", "RENDER/IDR", "VIRTUAL/IDR", 
    "SPX/IDR", "TIA/IDR", "FLOKI/IDR", "WIF/IDR", "SOON/IDR", "ALCH/IDR", "ZIL/IDR", 
    "VELO/IDR", "MEW/IDR", "POPCAT/IDR", "GRASS/IDR", "MOODENG/IDR", "JELLYJELLY/IDR", 
    "CARV/IDR", "NEIRO/IDR", "BOME/IDR", "MANTA/IDR", "GOAT/IDR", "DOGS/IDR", "SCR/IDR"
]

# --- SETUP EXCHANGE ---
exchange = ccxt.binance({'enableRateLimit': True})

# --- SIDEBAR ---
st.sidebar.header("🎛️ Pusat Kontrol")
modal_input = st.sidebar.number_input("Modal Trading (Rp)", min_value=100000, value=1000000, step=100000)
kurs_usd_idr = st.sidebar.number_input("Kurs USD/IDR (Untuk Konversi)", value=16000)
batas_harga = 10000 # Filter harga < 10k Rupiah

st.sidebar.info("Timeframe: **15 Menit** (Real-Time)")

# --- FUNGSI AMBIL DATA REAL-TIME ---
def get_data(symbol):
    try:
        # Trik IDR: Kalau symbol berakhiran IDR, kita ambil data USDT-nya dari Binance Global
        # Lalu nanti kita kali kurs. Ini karena Binance Global tidak punya pair IDR.
        is_idr_pair = False
        target_symbol = symbol
        
        if "/IDR" in symbol:
            is_idr_pair = True
            # Ubah XXX/IDR jadi XXX/USDT
            target_symbol = symbol.replace("/IDR", "/USDT")
            # Special case: USDT/IDR tidak bisa diubah jadi USDT/USDT (nilainya 1)
            if symbol == "USDT/IDR": return None 

        bars = exchange.fetch_ohlcv(target_symbol, timeframe='15m', limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df.index = df.index + timedelta(hours=7) # WIB
        
        return df, is_idr_pair
    except:
        return None, False

# --- CEK HYPE ---
def cek_hype_score(df):
    try:
        current_vol = df['volume'].iloc[-1]
        avg_vol = df['volume'].mean()
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 0
        if vol_ratio > 4.0: return "🔥 VIRAL", vol_ratio
        elif vol_ratio > 2.0: return "⚡ Rame", vol_ratio
        else: return "💤 Sepi", vol_ratio
    except: return "Unknown", 0

# --- AI CORE ---
def ramal_koin(symbol):
    try:
        df, is_idr_pair = get_data(symbol)
        if df is None: return None
        
        # HITUNG HARGA DALAM RUPIAH
        current_price_usd = df['close'].iloc[-1]
        current_price_idr = current_price_usd * kurs_usd_idr
        
        # FILTER HARGA: Jika harga > 10.000, SKIP.
        if current_price_idr > batas_harga: return None 

        # INDIKATOR TEKNIS
        df['RSI'] = RSIIndicator(close=df['close'], window=14).rsi()
        df['EMA'] = EMAIndicator(close=df['close'], window=20).ema_indicator()
        df.dropna(inplace=True)
        
        if len(df) < 30: return None

        hype_status, vol_ratio = cek_hype_score(df)
        
        # CEK TREN (EMA)
        last_price = df['close'].iloc[-1]
        is_downtrend = last_price < df['EMA'].iloc[-1]
        
        # AI PREDICTION
        scaler = MinMaxScaler(feature_range=(0, 1))
        features = df[['close', 'RSI', 'volume']].values
        scaled_data = scaler.fit_transform(features)
        
        lookback = 15
        x_train, y_train = [], []
        for i in range(lookback, len(scaled_data)):
            x_train.append(scaled_data[i-lookback:i, :])
            y_train.append(scaled_data[i, 0])
        
        x_train, y_train = np.array(x_train), np.array(y_train)
        
        model = Sequential()
        model.add(LSTM(30, return_sequences=False, input_shape=(x_train.shape[1], 3)))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(x_train, y_train, epochs=3, batch_size=16, verbose=0)
        
        # PREDIKSI MASA DEPAN
        last_seq = scaled_data[-lookback:].reshape(1, lookback, 3)
        future_prices_usd = []
        
        for _ in range(3):
            pred = model.predict(last_seq, verbose=0)[0, 0]
            future_prices_usd.append(pred)
            new_step = np.array([[[pred, last_seq[0,-1,1], last_seq[0,-1,2]]]])
            last_seq = np.append(last_seq[:, 1:, :], new_step, axis=1)
            
        dummy = np.zeros((3, 3))
        dummy[:, 0] = future_prices_usd
        real_future_usd = scaler.inverse_transform(dummy)[:, 0]
        final_price_usd = real_future_usd[-1]
        
        change_pct = ((final_price_usd - current_price_usd) / current_price_usd) * 100
        
        # LOGIKA TREN (Correction)
        trend_text = "UPTREND"
        if is_downtrend:
            trend_text = "DOWNTREND"
            if change_pct > 0: change_pct = change_pct * 0.1 # Kurangi optimisme
            
        profit_idr = (change_pct / 100) * modal_input

        # Convert Grafik ke Rupiah jika User minta IDR, atau tetap Rupiah untuk estimasi
        display_price_history = df['close'] * kurs_usd_idr
        display_future_history = real_future_usd * kurs_usd_idr

        return {
            "ticker": symbol,
            "price_idr": current_price_idr,
            "change_pct": change_pct,
            "profit_idr": profit_idr,
            "hype": hype_status,
            "trend": trend_text,
            "df_index": df.index,
            "hist_prices": display_price_history,
            "future_prices": display_future_history
        }
    except:
        return None

# --- UI UTAMA ---
st.write("---")

tab1, tab2 = st.tabs(["🎲 SCANNER BATCH (Acak 25)", "🔍 CEK MANUAL"])

with tab1:
    st.header("Scanner Batch (Acak 25 Koin)")
    st.write(f"Total Database: **{len(RAW_WATCHLIST)} Koin**. Klik tombol untuk mengambil sampel.")
    
    if st.button("AMBIL SAMPEL & SCAN 🔥"):
        # Ambil sampel acak agar server tidak overload
        batch_coins = random.sample(RAW_WATCHLIST, 25)
        
        results = []
        progress = st.progress(0)
        status = st.empty()
        
        valid_count = 0
        for i, coin in enumerate(batch_coins):
            status.text(f"Mengecek {coin}...")
            res = ramal_koin(coin)
            if res:
                results.append(res)
                valid_count += 1
            progress.progress((i + 1) / 25)
            
        status.text("Selesai!")
        
        if results:
            results.sort(key=lambda x: x['change_pct'], reverse=True)
            top = results[0]
            
            st.success(f"💎 **JUARA BATCH: {top['ticker']}**")
            st.caption(f"Hype: {top['hype']} | Tren: {top['trend']}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Harga (Rp)", f"Rp {top['price_idr']:,.2f}")
            c2.metric("Target AI", f"{top['change_pct']:.2f}%")
            c3.metric("Potensi Cuan", f"Rp {top['profit_idr']:,.0f}")
            
            # Grafik
            st.subheader(f"Grafik: {top['ticker']}")
            last_date = top['df_index'][-1]
            future_dates = pd.date_range(start=last_date + timedelta(minutes=15), periods=3, freq='15min')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=top['df_index'][-30:], y=top['hist_prices'].iloc[-30:], mode='lines+markers', name='Harga (IDR)', line=dict(color='cyan')))
            
            col_line = 'lime' if top['change_pct'] > 0 else 'red'
            fig.add_trace(go.Scatter(x=future_dates, y=top['future_prices'], mode='lines+markers', name='Prediksi', line=dict(color=col_line, width=3)))
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabel Sisa
            st.write("---")
            rows = []
            for r in results[1:]:
                rows.append([r['ticker'], f"Rp {r['price_idr']:,.2f}", r['hype'], f"{r['change_pct']:.2f}%", f"Rp {r['profit_idr']:,.0f}"])
            st.table(pd.DataFrame(rows, columns=["Koin", "Harga", "Hype", "Potensi", "Cuan"]))
        else:
            st.warning("Tidak ada koin yang lolos filter (< 10k) di batch ini. Coba lagi!")

with tab2:
    st.header("Cek Manual")
    pilihan = st.selectbox("Pilih Koin", RAW_WATCHLIST)
    
    if st.button("Analisa Koin Ini"):
        with st.spinner("Mengambil data..."):
            res = ramal_koin(pilihan)
            if res:
                st.metric("Harga", f"Rp {res['price_idr']:,.2f}")
                st.metric("Potensi", f"{res['change_pct']:.2f}%", f"Rp {res['profit_idr']:,.0f}")
                
                last_date = res['df_index'][-1]
                future_dates = pd.date_range(start=last_date + timedelta(minutes=15), periods=3, freq='15min')
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=res['df_index'][-30:], y=res['hist_prices'].iloc[-30:], mode='lines+markers', name='Harga', line=dict(color='cyan')))
                col_line = 'lime' if res['change_pct'] > 0 else 'red'
                fig.add_trace(go.Scatter(x=future_dates, y=res['future_prices'], mode='lines+markers', name='Prediksi', line=dict(color=col_line, width=3)))
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Gagal. Koin mungkin > Rp 10.000, atau data tidak tersedia di Binance Global.")
