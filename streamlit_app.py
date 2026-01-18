import streamlit as st
import numpy as np
import pandas as pd
import ccxt
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator, StochasticOscillator
from datetime import timedelta
import random

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="REAL-TIME SNIPER", layout="wide")
st.title("⚡ REAL-TIME SNIPER: Eksekusi Cepat")
st.markdown("""
**Mode Akurasi Tinggi:**
* 📡 **Data Source:** Langsung dari Binance (Induk Tokocrypto).
* ⏱️ **Zero Delay:** Tidak ada Yahoo Finance. Jika data tidak realtime, koin di-skip.
* 🎯 **Sinyal:** Fokus pada titik masuk (Entry) dan keluar (Exit).
""")

# --- DATABASE KOIN LENGKAP (DARI ANDA) ---
WATCHLIST = [
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

# --- KONEKSI EXCHANGE (CCXT) ---
exchange = ccxt.binance({
    'enableRateLimit': True, 
    'options': {'defaultType': 'spot'}
})

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Pengaturan Sniper")
    modal_awal = st.number_input("Modal Trading (Rp)", value=1000000)
    target_profit_pct = st.slider("Target Profit (%)", 1.0, 10.0, 2.5)
    stop_loss_pct = st.slider("Stop Loss (%)", 0.5, 5.0, 1.5)
    kurs_usd_idr = st.number_input("Kurs USD/IDR", value=16100)
    st.info("Hanya menampilkan koin yang datanya REAL-TIME di server Binance. Koin lokal/micin yang tidak ada di server global akan otomatis disembunyikan.")

# --- FUNGSI DATA REAL-TIME (STRICT) ---
def get_realtime_data(symbol):
    try:
        # LOGIKA KONVERSI IDR -> USDT (Untuk Data Fetching)
        # Server Global tidak punya IDR, jadi kita pinjam data USDT
        target_symbol = symbol
        is_idr = False
        
        if "/IDR" in symbol:
            target_symbol = symbol.replace("/IDR", "/USDT")
            is_idr = True
        
        # Mapping khusus untuk kasus beda nama
        # Misal ALCH di Toko = ACH di Binance
        if target_symbol == "ALCH/USDT": target_symbol = "ACH/USDT"
        if target_symbol == "JELLYJELLY/USDT": target_symbol = "JELLY/USDT" 
            
        # Ambil Data (Hanya 50 candle terakhir untuk kecepatan)
        bars = exchange.fetch_ohlcv(target_symbol, timeframe='15m', limit=50)
        
        if not bars: return None # Jika kosong, langsung skip
        
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7) # Convert ke WIB
        df.set_index('time', inplace=True)
        
        return df
        
    except Exception as e:
        return None # Jika error (koin ga ada di binance), return None

# --- ALGORITMA SNIPER ---
def analyze_coin(symbol):
    # 1. Ambil Data
    df = get_realtime_data(symbol)
    if df is None: return None # SKIP koin hantu
    
    # 2. Hitung Indikator
    close = df['close']
    
    # Bollinger Bands
    bb = BollingerBands(close=close, window=20, window_dev=2)
    df['bb_h'] = bb.bollinger_hband()
    df['bb_l'] = bb.bollinger_lband()
    
    # RSI
    df['rsi'] = RSIIndicator(close=close, window=14).rsi()
    
    # Stochastic
    stoch = StochasticOscillator(high=df['high'], low=df['low'], close=close)
    df['stoch'] = stoch.stoch()
    
    # 3. Tentukan Posisi Terakhir
    last_price = close.iloc[-1]
    last_rsi = df['rsi'].iloc[-1]
    bb_low = df['bb_l'].iloc[-1]
    bb_high = df['bb_h'].iloc[-1]
    
    # 4. Logic Sinyal
    signal = "WAIT"
    confidence = 0
    reason = "Sideways"
    
    # SYARAT BELI:
    # 1. Harga dekat BB Bawah (Diskon)
    # 2. RSI < 45 (Murah)
    if last_price <= (bb_low * 1.015) and last_rsi < 45:
        signal = "BUY NOW"
        confidence = 85
        reason = "Harga Diskon (Support BB) + RSI Rendah"
        if last_rsi < 30: 
            confidence = 98
            reason = "SUPER DISKON (Oversold)"
            
    # SYARAT JUAL:
    # 1. Harga dekat BB Atas (Mahal)
    # 2. RSI > 60 (Overbought dikit)
    elif last_price >= (bb_high * 0.985) and last_rsi > 60:
        signal = "SELL NOW"
        confidence = 85
        reason = "Harga Pucuk (Resistance BB) + RSI Mahal"
        
    # 5. Hitung Harga Rupiah (Estimasi)
    price_idr = last_price * kurs_usd_idr
    tp_price = price_idr * (1 + target_profit_pct/100)
    sl_price = price_idr * (1 - stop_loss_pct/100)
    est_profit = modal_awal * (target_profit_pct/100)
    
    return {
        "ticker": symbol,
        "price_idr": price_idr,
        "signal": signal,
        "confidence": confidence,
        "reason": reason,
        "tp": tp_price,
        "sl": sl_price,
        "profit": est_profit
    }

# --- TAMPILAN DASHBOARD ---
st.info("💡 **INFO:** Sistem sekarang hanya memproses koin yang datanya **REAL-TIME**. Jika koin favorit Anda tidak muncul, berarti datanya tidak tersedia di server Global (Binance).")

if st.button("🚀 SCANNER SNIPER (ACAK 30 KOIN)", type="primary"):
    
    # Ambil sampel acak
    batch = random.sample(WATCHLIST, 30)
    
    results_buy = []
    results_sell = []
    
    # Progress Bar
    progress = st.progress(0)
    status = st.empty()
    valid_count = 0
    
    for i, coin in enumerate(batch):
        status.caption(f"Mengecek {coin} di Server Realtime...")
        res = analyze_coin(coin)
        
        if res:
            valid_count += 1
            if "BUY" in res['signal']: results_buy.append(res)
            elif "SELL" in res['signal']: results_sell.append(res)
            
        progress.progress((i+1)/30)
        
    status.empty()
    
    st.write(f"✅ Selesai Scan. Dari 30 sampel, **{valid_count} koin valid** (ada datanya).")
    
    # --- HASIL SINYAL BELI ---
    st.subheader("🟢 KESEMPATAN BELI (BUY)")
    if results_buy:
        results_buy.sort(key=lambda x: x['confidence'], reverse=True)
        for item in results_buy:
            with st.container():
                st.markdown(f"### {item['ticker']} ({item['signal']})")
                c1, c2, c3 = st.columns(3)
                c1.metric("Harga Beli (Est)", f"Rp {item['price_idr']:,.0f}")
                c2.metric("Jual Di (TP)", f"Rp {item['tp']:,.0f}", f"+{target_profit_pct}%")
                c3.error(f"Stop Loss: Rp {item['sl']:,.0f}")
                st.caption(f"Alasan: {item['reason']}")
                st.divider()
    else:
        st.warning("Tidak ada sinyal BELI yang kuat di batch ini. Coba klik tombol Scan lagi untuk batch koin lain.")

    # --- HASIL SINYAL JUAL ---
    st.subheader("🔴 SAATNYA JUAL (SELL)")
    if results_sell:
        for item in results_sell:
            st.markdown(f"**{item['ticker']}** - Harga: Rp {item['price_idr']:,.0f} | **JUAL** ({item['reason']})")
    else:
        st.caption("Tidak ada sinyal jual urgent.")

# --- CEK MANUAL ---
st.sidebar.markdown("---")
st.sidebar.header("🔍 Cek Koin Tertentu")
manual_coin = st.sidebar.selectbox("Pilih Koin", WATCHLIST)

if st.sidebar.button("Cek Sinyal Koin Ini"):
    with st.spinner("Mengambil data Real-Time..."):
        res = analyze_coin(manual_coin)
        if res:
            if "BUY" in res['signal']:
                st.sidebar.success(f"REKOMENDASI: {res['signal']}")
            elif "SELL" in res['signal']:
                st.sidebar.error(f"REKOMENDASI: {res['signal']}")
            else:
                st.sidebar.warning(f"REKOMENDASI: {res['signal']}")
            
            st.sidebar.write(f"Harga: Rp {res['price_idr']:,.0f}")
            st.sidebar.write(f"TP: Rp {res['tp']:,.0f}")
            st.sidebar.caption(res['reason'])
        else:
            st.sidebar.error("Data koin ini tidak tersedia secara Real-Time.")
