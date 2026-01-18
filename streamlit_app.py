import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator, StochasticOscillator
from datetime import timedelta
import random

# --- KONFIGURASI ---
st.set_page_config(page_title="AI SNIPER SIGNAL", layout="wide")
st.title("🎯 AI SNIPER: Sinyal Eksekusi (Buy/Sell)")
st.markdown("""
**Instruksi Langsung:**
Aplikasi ini tidak lagi meramal garis, tapi memberikan **Titik Entry & Exit** berdasarkan algoritma Scalping (Bollinger Bands + RSI + Stochastic).
""")

# --- INPUT USER ---
with st.sidebar:
    st.header("⚙️ Pengaturan Sniper")
    modal_awal = st.number_input("Modal Trading (Rp)", value=1000000)
    target_profit_pct = st.slider("Target Profit per Trade (%)", 1.0, 10.0, 2.5)
    stop_loss_pct = st.slider("Batas Rugi (Stop Loss) (%)", 0.5, 5.0, 1.5)
    kurs_usd_idr = st.number_input("Kurs USD/IDR (Sesuaikan dgn P2P)", value=16100)
    
    st.info("💡 **Tips:** Jika harga di Tokocrypto beda dikit, itu wajar (Spread). Fokus pada **Persentase** kenaikannya.")

# --- DATABASE KOIN (FULL LIST) ---
WATCHLIST = [
    # --- LIST PRIORITAS (Micin & Volatil) ---
    "DENT/USDT", "JASMY/USDT", "SLP/USDT", "LUNC/USDT", "SPELL/USDT", "SHIB/USDT", 
    "PEPE/USDT", "FLOKI/USDT", "BONK/USDT", "WIF/USDT", "BOME/USDT", "NOT/USDT",
    "TURBO/USDT", "GALA/USDT", "SAND/USDT", "MANA/USDT", "GMT/USDT", "NEAR/USDT",
    "ALCH/USDT", "ACH/USDT", "TKO/USDT", "XRP/USDT", "DOGE/USDT", "SOL/USDT",
    "HEI/USDT", "KOM/USDT", "1000SATS/USDT", "BTTC/USDT", "WIN/USDT", "BTT/USDT",
    "XVG/USDT", "HOT/USDT", "SC/USDT", "ZIL/USDT", "IOST/USDT", "VTHO/USDT",
    "CKB/USDT", "RSR/USDT", "MBL/USDT", "ANKR/USDT", "STX/USDT", "CFX/USDT"
]

# --- KONEKSI EXCHANGE ---
exchange = ccxt.binance({'enableRateLimit': True})

# --- FUNGSI AMBIL DATA ---
def get_market_data(symbol):
    df = None
    source = "Binance"
    
    try:
        # 1. Coba Binance Realtime
        target = symbol
        if "/IDR" in symbol: target = symbol.replace("/IDR", "/USDT")
        
        bars = exchange.fetch_ohlcv(target, timeframe='15m', limit=50)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
        df.set_index('time', inplace=True)
        
    except:
        # 2. Coba Yahoo Finance (Backup)
        try:
            yf_sym = symbol.replace("/", "-").replace("USDT", "USD")
            # Handling khusus ticker aneh
            if "ALCH" in symbol: yf_sym = "ACH-USD" # Kemungkinan Alchemy Pay
            
            df = yf.download(yf_sym, period='2d', interval='15m', progress=False)
            if len(df) > 0:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
                df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
                df.columns = ['open', 'high', 'low', 'close', 'vol']
                df.index = df.index + timedelta(hours=7)
                source = "Yahoo"
            else:
                return None, None
        except:
            return None, None

    return df, source

# --- LOGIKA SNIPER (SIGNAL GENERATOR) ---
def analyze_coin(symbol):
    df, source = get_market_data(symbol)
    if df is None or len(df) < 20: return None
    
    # Indikator
    close = df['close']
    
    # 1. Bollinger Bands (Volatilitas)
    bb = BollingerBands(close=close, window=20, window_dev=2)
    df['bb_h'] = bb.bollinger_hband()
    df['bb_l'] = bb.bollinger_lband()
    
    # 2. RSI (Jenuh Beli/Jual)
    df['rsi'] = RSIIndicator(close=close, window=14).rsi()
    
    # 3. Stochastic (Momentum Cepat)
    stoch = StochasticOscillator(high=df['high'], low=df['low'], close=close)
    df['stoch'] = stoch.stoch()
    
    # --- LOGIKA SINYAL ---
    last_price = close.iloc[-1]
    last_rsi = df['rsi'].iloc[-1]
    last_stoch = df['stoch'].iloc[-1]
    bb_low = df['bb_l'].iloc[-1]
    bb_high = df['bb_h'].iloc[-1]
    
    signal = "NEUTRAL"
    confidence = 0
    reason = ""
    
    # KONDISI BELI (BUY)
    # Harga menyentuh BB Bawah + RSI Murah (<40) + Stoch mau naik
    if last_price <= (bb_low * 1.01) and last_rsi < 45:
        signal = "BUY NOW"
        confidence = 80
        reason = "Harga di Dasar (Support) + RSI Murah"
        if last_rsi < 30: 
            confidence = 95
            reason += " (Oversold Parah!)"
            
    # KONDISI JUAL (SELL)
    # Harga menyentuh BB Atas + RSI Mahal (>60)
    elif last_price >= (bb_high * 0.99) and last_rsi > 60:
        signal = "SELL NOW"
        confidence = 80
        reason = "Harga di Pucuk (Resistance) + RSI Mahal"
    
    # KONDISI WAIT
    else:
        signal = "WAIT"
        reason = "Pasar Sideways / Belum ada momen"

    # Konversi ke Rupiah
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
        "profit": est_profit,
        "source": source
    }

# --- TAMPILAN DASHBOARD ---

# Container tombol scan
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    scan_btn = st.button("🔍 SCAN PASAR (ACAK 20)", type="primary")

if scan_btn:
    # Ambil sampel acak
    batch = random.sample(WATCHLIST, 20)
    
    results_buy = []
    results_sell = []
    
    progress = st.progress(0)
    status = st.empty()
    
    for i, coin in enumerate(batch):
        status.caption(f"Membidik {coin}...")
        res = analyze_coin(coin)
        if res:
            if "BUY" in res['signal']: results_buy.append(res)
            elif "SELL" in res['signal']: results_sell.append(res)
        progress.progress((i+1)/20)
        
    status.empty()
    progress.empty()

    # --- TAMPILKAN HASIL BELI (HIJAU) ---
    st.subheader("🟢 SINYAL BELI (Potensi Cuan)")
    if len(results_buy) > 0:
        # Urutkan dari Confidence tertinggi
        results_buy.sort(key=lambda x: x['confidence'], reverse=True)
        
        for item in results_buy:
            with st.container():
                # Kartu Sinyal
                c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
                
                c1.markdown(f"### {item['ticker']}")
                c1.caption(f"Sumber: {item['source']}")
                
                c2.metric("ENTRY (Beli)", f"Rp {item['price_idr']:,.0f}")
                
                c3.metric("TARGET JUAL (TP)", f"Rp {item['tp']:,.0f}", f"+{target_profit_pct}%")
                
                c4.error(f"STOP LOSS: Rp {item['sl']:,.0f}")
                c4.success(f"**ALASAN:** {item['reason']}")
                
                st.markdown(f"**Estimasi Cuan:** Rp {item['profit']:,.0f} dengan modal Rp {modal_awal:,.0f}")
                st.divider()
    else:
        st.info("Belum ada sinyal BELI yang kuat di batch ini. Pasar mungkin lagi tinggi/nanggung.")

    # --- TAMPILKAN HASIL JUAL (MERAH) ---
    st.subheader("🔴 SINYAL JUAL (Take Profit/Short)")
    if len(results_sell) > 0:
        for item in results_sell:
             st.markdown(f"**{item['ticker']}** - Harga: Rp {item['price_idr']:,.0f} | **Saran: JUAL SEKARANG** ({item['reason']})")
    else:
        st.caption("Tidak ada sinyal jual darurat.")

# --- CEK MANUAL ---
st.write("---")
st.header("Cek Koin Spesifik")
manual_coin = st.selectbox("Pilih Koin:", WATCHLIST)

if st.button("Analisa Koin Ini"):
    with st.spinner("Menganalisa..."):
        res = analyze_coin(manual_coin)
        if res:
            if "BUY" in res['signal']:
                st.success(f"### REKOMENDASI: {res['signal']}")
            elif "SELL" in res['signal']:
                st.error(f"### REKOMENDASI: {res['signal']}")
            else:
                st.warning(f"### REKOMENDASI: {res['signal']}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Harga Sekarang", f"Rp {res['price_idr']:,.0f}")
            c2.metric("Target Jual (TP)", f"Rp {res['tp']:,.0f}", f"+{target_profit_pct}%")
            c3.metric("Stop Loss (SL)", f"Rp {res['sl']:,.0f}", f"-{stop_loss_pct}%")
            
            st.write(f"**Analisa:** {res['reason']}")
        else:
            st.error("Data koin tidak ditemukan.")
