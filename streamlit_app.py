import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
import random
from datetime import datetime, timedelta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Oracle AI: Hybrid", layout="wide")

st.title("👁️ ORACLE AI: Hybrid Engine (Binance + Yahoo)")
st.markdown("""
**Perbaikan Sistem:**
1.  🛡️ **Hybrid Data:** Menggunakan Binance (Real-time) sebagai utama. Jika koin tidak ada, otomatis cari di Yahoo Finance.
2.  📊 **Laporan Scan:** Menampilkan detail berapa koin yang sukses discan, berapa yang data kosong, dan berapa yang kemahalan.
3.  💰 **Filter Cerdas:** Tetap menjaga batasan harga < Rp 10.000.
""")

# --- DATABASE KOIN MASIF ---
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
    
    # --- IDR PAIRS ---
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
kurs_usd_idr = st.sidebar.number_input("Kurs USD/IDR", value=16000)
batas_harga = 10000 # Filter harga

st.sidebar.info("Sistem akan mencoba Binance (Realtime) -> Jika gagal -> Yahoo (Backup)")

# --- FUNGSI HYBRID GET DATA ---
def get_data_hybrid(symbol):
    df = None
    source = "None"
    
    # 1. COBA BINANCE (CCXT)
    try:
        # Konversi symbol IDR ke USDT untuk request Binance
        target_symbol = symbol
        if "/IDR" in symbol:
            target_symbol = symbol.replace("/IDR", "/USDT")
        
        # Coba fetch
        bars = exchange.fetch_ohlcv(target_symbol, timeframe='15m', limit=100)
        if bars and len(bars) > 0:
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df.index = df.index + timedelta(hours=7) # WIB
            source = "Binance (Realtime)"
    except:
        pass # Lanjut ke backup
        
    # 2. JIKA GAGAL, COBA YAHOO FINANCE
    if df is None:
        try:
            # Format Yahoo: HEI-USD
            yf_symbol = symbol.replace("/", "-").replace("USDT", "USD").replace("IDR", "USD") # Asumsi IDR pair di Yahoo pakai USD ticker
            
            # Khusus beberapa koin aneh, format mungkin beda, tapi kita coba standar dulu
            data_yf = yf.download(yf_symbol, period='5d', interval='15m', progress=False)
            
            if len(data_yf) > 20:
                if isinstance(data_yf.columns, pd.MultiIndex):
                    data_yf.columns = data_yf.columns.droplevel(1)
                
                df = data_yf[['Open', 'High', 'Low', 'Close', 'Volume']]
                df.columns = ['open', 'high', 'low', 'close', 'volume'] # Samakan nama kolom
                df.index = df.index + timedelta(hours=7) # WIB
                source = "Yahoo (Backup)"
        except:
            pass

    return df, source

# --- AI CORE ---
def ramal_koin(symbol):
    try:
        df, source = get_data_hybrid(symbol)
        
        # LAPORAN STATUS (Untuk Debugging User)
        status_msg = "OK"
        if df is None:
            return {"status": "DATA_NOT_FOUND", "ticker": symbol}
        
        current_price_usd = df['close'].iloc[-1]
        current_price_idr = current_price_usd * kurs_usd_idr
        
        # FILTER HARGA
        if current_price_idr > batas_harga:
            return {"status": "TOO_EXPENSIVE", "ticker": symbol, "price": current_price_idr}

        # INDIKATOR
        df['RSI'] = RSIIndicator(close=df['close'], window=14).rsi()
        df['EMA'] = EMAIndicator(close=df['close'], window=20).ema_indicator()
        df.dropna(inplace=True)
        
        if len(df) < 30: return {"status": "DATA_TOO_SHORT", "ticker": symbol}

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
        
        # PREDIKSI
        last_seq = scaled_data[-lookback:].reshape(1, lookback, 3)
        future_prices = []
        for _ in range(3):
            pred = model.predict(last_seq, verbose=0)[0, 0]
            future_prices.append(pred)
            new_step = np.array([[[pred, last_seq[0,-1,1], last_seq[0,-1,2]]]])
            last_seq = np.append(last_seq[:, 1:, :], new_step, axis=1)
            
        dummy = np.zeros((3, 3))
        dummy[:, 0] = future_prices
        real_future_usd = scaler.inverse_transform(dummy)[:, 0]
        final_price_usd = real_future_usd[-1]
        
        change_pct = ((final_price_usd - current_price_usd) / current_price_usd) * 100
        profit_idr = (change_pct / 100) * modal_input
        
        # TREND CHECK
        trend = "UPTREND" if df['close'].iloc[-1] > df['EMA'].iloc[-1] else "DOWNTREND"
        if trend == "DOWNTREND" and change_pct > 0: change_pct *= 0.1 # Koreksi

        return {
            "status": "SUCCESS",
            "ticker": symbol,
            "source": source,
            "price_idr": current_price_idr,
            "change_pct": change_pct,
            "profit_idr": profit_idr,
            "trend": trend,
            "df_index": df.index,
            "hist_prices": df['close'] * kurs_usd_idr,
            "future_prices": real_future_usd * kurs_usd_idr
        }
    except:
        return {"status": "ERROR", "ticker": symbol}

# --- UI UTAMA ---
st.write("---")

tab1, tab2 = st.tabs(["🎲 SCANNER BATCH (Acak 40)", "🔍 CEK MANUAL"])

with tab1:
    st.header("Scanner Batch (Acak 40 Koin)")
    if st.button("AMBIL SAMPEL & SCAN 🔥"):
        
        # Batch diperbesar jadi 40 biar kemungkinan dapat koin valid lebih besar
        batch_coins = random.sample(RAW_WATCHLIST, 40)
        
        results = []
        stats = {"SUCCESS": 0, "DATA_NOT_FOUND": 0, "TOO_EXPENSIVE": 0, "ERROR": 0}
        
        progress = st.progress(0)
        status_box = st.empty()
        
        for i, coin in enumerate(batch_coins):
            status_box.text(f"Mengecek {coin}...")
            res = ramal_koin(coin)
            
            stats[res.get("status", "ERROR")] = stats.get(res.get("status", "ERROR"), 0) + 1
            
            if res["status"] == "SUCCESS":
                results.append(res)
            
            progress.progress((i + 1) / 40)
            
        status_box.empty()
        
        # TAMPILKAN STATISTIK SCANNING (Supaya user tidak bingung)
        st.info(f"📊 Laporan Scan: {stats['SUCCESS']} Berhasil | {stats['DATA_NOT_FOUND']} Data Kosong (Tidak ada di Exchange) | {stats['TOO_EXPENSIVE']} Kemahalan (>10k) | {stats['ERROR']} Error")
        
        if results:
            results.sort(key=lambda x: x['change_pct'], reverse=True)
            top = results[0]
            
            st.success(f"💎 **JUARA BATCH: {top['ticker']}**")
            st.caption(f"Sumber Data: {top['source']} | Tren: {top['trend']}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Harga (Rp)", f"Rp {top['price_idr']:,.2f}")
            c2.metric("Target AI", f"{top['change_pct']:.2f}%")
            c3.metric("Potensi Cuan", f"Rp {top['profit_idr']:,.0f}")
            
            # Grafik
            st.subheader(f"Grafik: {top['ticker']}")
            last_date = top['df_index'][-1]
            future_dates = pd.date_range(start=last_date + timedelta(minutes=15), periods=3, freq='15min')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=top['df_index'][-30:], y=top['hist_prices'].iloc[-30:], mode='lines+markers', name='Harga', line=dict(color='cyan')))
            col_line = 'lime' if top['change_pct'] > 0 else 'red'
            fig.add_trace(go.Scatter(x=future_dates, y=top['future_prices'], mode='lines+markers', name='Prediksi', line=dict(color=col_line, width=3)))
            st.plotly_chart(fig, use_container_width=True)
            
            st.write("---")
            st.write("### Daftar Koin Lolos Filter:")
            rows = []
            for r in results[1:]:
                rows.append([r['ticker'], f"Rp {r['price_idr']:,.2f}", r['source'], f"{r['change_pct']:.2f}%", f"Rp {r['profit_idr']:,.0f}"])
            st.table(pd.DataFrame(rows, columns=["Koin", "Harga", "Sumber Data", "Potensi", "Cuan"]))
        else:
            st.warning("Tidak ada koin yang lolos di batch ini. (Cek Laporan Scan di atas). Coba klik tombol lagi untuk ambil sampel baru.")

with tab2:
    st.header("Cek Manual")
    pilihan = st.selectbox("Pilih Koin", RAW_WATCHLIST)
    if st.button("Cek Koin Ini"):
        with st.spinner("Mencari data (Hybrid)..."):
            res = ramal_koin(pilihan)
            
            if res["status"] == "SUCCESS":
                st.success(f"Data Ditemukan via {res['source']}")
                st.metric("Harga", f"Rp {res['price_idr']:,.2f}")
                st.metric("Potensi", f"{res['change_pct']:.2f}%", f"Rp {res['profit_idr']:,.0f}")
                
                last_date = res['df_index'][-1]
                future_dates = pd.date_range(start=last_date + timedelta(minutes=15), periods=3, freq='15min')
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=res['df_index'][-30:], y=res['hist_prices'].iloc[-30:], mode='lines+markers', name='Harga', line=dict(color='cyan')))
                col_line = 'lime' if res['change_pct'] > 0 else 'red'
                fig.add_trace(go.Scatter(x=future_dates, y=res['future_prices'], mode='lines+markers', name='Prediksi', line=dict(color=col_line, width=3)))
                st.plotly_chart(fig, use_container_width=True)
            elif res["status"] == "DATA_NOT_FOUND":
                st.error("Data koin ini TIDAK DITEMUKAN di Binance maupun Yahoo Finance. Mungkin koin ini hanya ada di Tokocrypto lokal/DEX.")
            elif res["status"] == "TOO_EXPENSIVE":
                st.error(f"Koin ini harganya Rp {res['price']:,.2f} (Di atas batas Rp 10.000).")
