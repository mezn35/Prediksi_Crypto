import streamlit as st
import numpy as np
import pandas as pd
import ccxt
import yfinance as yf
from ta.volatility import BollingerBands, AverageTrueRange
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from datetime import datetime, timedelta
import plotly.graph_objects as go
import random

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI FORTRESS MODE", layout="wide")
st.title("🛡️ AI FORTRESS: Strategi 'Anti-Boncos'")
st.markdown("""
**Sistem Keamanan Tingkat Tinggi:**
1.  👑 **EMA 200 Filter:** Hanya beli di fase **UPTREND** (Aman). Koin yang trennya turun otomatis DIBUANG.
2.  📉 **Buy The Dip:** Mencari momen koreksi (diskon) di tengah tren naik.
3.  🧮 **Rasio Emas:** Memastikan potensi untung jauh lebih besar daripada risiko rugi.
""")

# --- DATABASE KOIN LENGKAP ---
WATCHLIST = [
    # --- USDT PAIRS ---
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
    "ADA/USDT", "AVAX/USDT", "TRX/USDT", "LINK/USDT", "MATIC/USDT", "DOT/USDT", 
    "LTC/USDT", "BCH/USDT", "UNI/USDT", "NEAR/USDT", "APT/USDT", "XLM/USDT", 
    "SHIB/USDT", "ICP/USDT", "HBAR/USDT", "FIL/USDT", "ATOM/USDT", "VET/USDT", 
    "IMX/USDT", "OP/USDT", "INJ/USDT", "GRT/USDT", "RNDR/USDT", "STX/USDT", 
    "LDO/USDT", "FTM/USDT", "TIA/USDT", "SEI/USDT", "ARB/USDT", "ALGO/USDT", 
    "KAS/USDT", "SUI/USDT", "EGLD/USDT", "QNT/USDT", "AAVE/USDT", "MINA/USDT", 
    "FLOW/USDT", "AXS/USDT", "SAND/USDT", "THETA/USDT", "MANA/USDT", "EOS/USDT", 
    "XTZ/USDT", "NEO/USDT", "KCS/USDT", "CAKE/USDT", "CFX/USDT", "CHZ/USDT", 
    "GALA/USDT", "PEPE/USDT", "FLOKI/USDT", "BONK/USDT", "WIF/USDT", "BOME/USDT", 
    "JASMY/USDT", "LUNC/USDT", "SLP/USDT", "NOT/USDT", "TURBO/USDT", "MEME/USDT", 
    "PEOPLE/USDT", "WLD/USDT", "FET/USDT", "AGIX/USDT", "OCEAN/USDT", "ARKM/USDT",
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

exchange = ccxt.binance({'enableRateLimit': True})

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settingan Benteng")
    modal_awal = st.number_input("Modal Trading (Rp)", value=1000000)
    kurs_usd_idr = st.number_input("Kurs USD/IDR", value=16100)
    st.info("Logika 'Pasti Untung' = Hanya beli saat tren NAIK tapi harga DISKON (Koreksi). Jika pasar jelek, tidak akan ada sinyal.")

# --- FUNGSI HYBRID DATA ---
def get_data(symbol):
    df = None
    source = ""
    try:
        # Binance Realtime
        target = symbol.replace("/IDR", "/USDT")
        if "JELLY" in target: target = "JELLY/USDT" 
        # Ambil 300 candle untuk hitung EMA 200
        bars = exchange.fetch_ohlcv(target, timeframe='1h', limit=300)
        if bars:
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
            df['time'] = pd.to_datetime(df['time'], unit='ms') + timedelta(hours=7)
            df.set_index('time', inplace=True)
            source = "Realtime"
    except: pass
    
    if df is None:
        try:
            # Yahoo Backup
            yf_sym = symbol.replace("/", "-").replace("USDT", "USD").replace("IDR", "USD")
            data_yf = yf.download(yf_sym, period='1mo', interval='1h', progress=False)
            if len(data_yf) > 200:
                if isinstance(data_yf.columns, pd.MultiIndex): data_yf.columns = data_yf.columns.droplevel(1)
                df = data_yf[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
                df.columns = ['open', 'high', 'low', 'close', 'vol']
                df.index = df.index + timedelta(hours=7)
                source = "Backup"
        except: pass
    return df, source

# --- ANALISA BENTENG (FORTRESS LOGIC) ---
def analyze_fortress(symbol):
    df, source = get_data(symbol)
    if df is None or len(df) < 200: return None
    
    close = df['close']
    last_price = close.iloc[-1]
    
    # --- 1. FILTER TREN (EMA 200) ---
    # Ini filter paling penting. Kalau harga di bawah EMA 200 = DOWNTREND = JANGAN BELI.
    df['ema200'] = EMAIndicator(close=close, window=200).ema_indicator()
    ema200 = df['ema200'].iloc[-1]
    
    # --- 2. FILTER MOMENTUM (RSI) ---
    df['rsi'] = RSIIndicator(close=close, window=14).rsi()
    rsi = df['rsi'].iloc[-1]
    
    # --- 3. LOGIKA KEPUTUSAN ---
    status = "SKIP"
    reason = "Risiko Tinggi"
    score = 0
    
    # Aturan 1: Harga HARUS di atas EMA 200 (Tren Naik)
    # ATAU Harga baru saja memantul dari EMA 200
    is_uptrend = last_price > ema200
    
    # Aturan 2: RSI harus Murah (Diskon)
    is_cheap = rsi < 45
    is_super_cheap = rsi < 30
    
    # KONDISI EMAS (Perfect Buy)
    if is_uptrend and is_super_cheap:
        status = "BUY NOW"
        reason = "✨ GOLDEN MOMENT: Tren Naik + Harga Sangat Murah (Oversold)"
        score = 100
        
    # KONDISI PERAK (Good Buy)
    elif is_uptrend and is_cheap:
        status = "BUY"
        reason = "✅ Tren Naik + Harga Diskon (Koreksi Wajar)"
        score = 80
        
    # KONDISI "SEROK BAWAH" (Risiko Sedang, Potensi Tinggi)
    # Harga di bawah EMA 200, TAPI RSI sangat rendah (<25) = Potensi Rebound
    elif (not is_uptrend) and rsi < 25:
        status = "SPECULATIVE BUY"
        reason = "⚠️ Pantulan Keras (Rebound) dari Oversold Parah"
        score = 60
        
    else:
        # Jika tidak memenuhi syarat di atas, buang.
        if not is_uptrend: return {"ticker": symbol, "status": "DIBUANG (Downtrend/Bahaya)"}
        if not is_cheap: return {"ticker": symbol, "status": "DIBUANG (Kemahalan)"}

    # Hitung Target
    atr = AverageTrueRange(high=df['high'], low=df['low'], close=close, window=14).average_true_range().iloc[-1]
    
    # Target Profit minimal 10% atau 3x ATR (Mana yang lebih besar)
    target_pct = max(0.10, (atr * 3) / last_price)
    stop_loss_pct = target_pct / 3 # Risk Reward 1:3 (Rugi 1, Untung 3)
    
    price_idr = last_price * kurs_usd_idr
    tp_idr = price_idr * (1 + target_pct)
    sl_idr = price_idr * (1 - stop_loss_pct)
    profit_idr = modal_awal * target_pct
    
    # Estimasi Waktu (Time Traveler Lite)
    speed_per_hour = atr
    if speed_per_hour == 0: speed_per_hour = last_price * 0.001
    hours_to_tp = (tp_idr - price_idr) / (speed_per_hour * kurs_usd_idr)
    sell_time = df.index[-1] + timedelta(hours=hours_to_tp)
    
    return {
        "status": status,
        "ticker": symbol,
        "price_idr": price_idr,
        "tp_idr": tp_idr,
        "sl_idr": sl_idr,
        "profit_idr": profit_idr,
        "sell_time": sell_time,
        "reason": reason,
        "score": score,
        "rsi": rsi,
        "df": df,
        "source": source
    }

# --- UI UTAMA ---
st.info("💡 **LOGIKA BENTENG:** AI akan memfilter ratusan koin dan hanya menampilkan yang trennya NAIK (di atas EMA 200) tapi harganya sedang DISKON (RSI < 45). Jika pasar sedang hancur, hasil mungkin kosong demi keamanan Anda.")

if st.button("🛡️ AKTIFKAN PERISAI & SCAN (ACAK 50)", type="primary"):
    batch = random.sample(WATCHLIST, 50)
    st.session_state['fortress_results'] = []
    
    scan_log = []
    prog = st.progress(0)
    
    for i, c in enumerate(batch):
        res = analyze_fortress(c)
        if res:
            if "BUY" in res['status']:
                st.session_state['fortress_results'].append(res)
                scan_log.append(f"🟢 {c}: LOLOS ({res['status']})")
            else:
                scan_log.append(f"🔴 {c}: {res['status']}")
        else:
            scan_log.append(f"⚪ {c}: Tidak Ada Data")
        prog.progress((i+1)/50)
    prog.empty()
    
    with st.expander("Lihat Koin yang Ditolak (Demi Keamanan)"):
        st.write(scan_log)

if 'fortress_results' in st.session_state and st.session_state['fortress_results']:
    results = st.session_state['fortress_results']
    results.sort(key=lambda x: x['score'], reverse=True)
    
    top = results[0]
    
    # --- KARTU SINYAL UTAMA ---
    st.success(f"💎 **HASIL SARINGAN TERKETAT: {top['ticker']}**")
    st.caption(f"Alasan AI: {top['reason']} | RSI: {top['rsi']:.1f}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("BELI SEKARANG", f"Rp {top['price_idr']:,.0f}")
    c2.metric("TARGET JUAL", f"Rp {top['tp_idr']:,.0f}", help=f"Estimasi Waktu: {top['sell_time'].strftime('%d %b, %H:%M')}")
    c3.metric("BATAS RUGI (SL)", f"Rp {top['sl_idr']:,.0f}", "Wajib Pasang!")
    
    st.markdown(f"### 💰 Potensi Profit: Rp {top['profit_idr']:,.0f}")
    
    # --- GRAFIK ---
    df = top['df']
    fig = go.Figure()
    # Candlestick
    fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Harga'))
    # EMA 200 (Garis Tren)
    fig.add_trace(go.Scatter(x=df.index, y=df['ema200'], mode='lines', name='Garis Tren (EMA 200)', line=dict(color='orange', width=2)))
    # Target
    fig.add_hline(y=top['tp_idr']/kurs_usd_idr, line_color="green", annotation_text="Target Profit")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # --- TABEL ---
    st.write("---")
    st.write("### Opsi Aman Lainnya:")
    rows = []
    for r in results[1:]:
        rows.append([r['ticker'], r['status'], f"Rp {r['price_idr']:,.0f}", f"Rp {r['tp_idr']:,.0f}", r['reason']])
    st.table(pd.DataFrame(rows, columns=["Koin", "Status", "Harga Beli", "Target Jual", "Alasan"]))
    
else:
    if 'fortress_results' in st.session_state: # Sudah scan tapi kosong
        st.error("🛡️ **MODE BENTENG DIAKTIFKAN:** Dari 50 sampel, TIDAK ADA yang memenuhi syarat keamanan 100%.")
        st.write("Saran AI: Jangan memaksakan masuk pasar sekarang. Pasar mungkin sedang downtrend atau harga sedang di pucuk. 'Cash is King'. Coba scan lagi nanti.")
