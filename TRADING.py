import datetime
import json
import urllib.request
import pandas as pd
import streamlit as st

# Set up page styling for maximum canvas layout
st.set_page_config(page_title="Nifty 50 Predictor", page_icon="📈", layout="wide")

st.title("📈 Nifty 50 Algorithmic Trading Terminal")
st.markdown("Select an asset below to view the automated buy matrix and forecasting chart profiles.")

# 1. FOOLPROOF DROPDOWN FOR ALL NIFTY 50 STOCKS
nifty50_tickers = {
    "Reliance Industries": "RELIANCE", "HDFC Bank": "HDFCBANK", "ICICI Bank": "ICICIBANK",
    "Bharti Airtel": "BHARTIARTL", "State Bank of India": "SBIN", "Infosys": "INFY",
    "Tata Consultancy Services": "TCS", "Larsen & Toubro": "LT", "Axis Bank": "AXISBANK",
    "ITC Limited": "ITC", "Hindustan Unilever": "HINDUNILVR", "Mahindra & Mahindra": "M&M",
    "Maruti Suzuki": "MARUTI", "Sun Pharma": "SUNPHARMA", "Tata Motors": "TATAMOTORS",
    "HCL Technologies": "HCLTECH", "Bajaj Finance": "BAJFINANCE", "Adani Ports": "ADANIPORTS",
    "Kotak Mahindra Bank": "KOTAKBANK", "Titan Company": "TITAN", "UltraTech Cement": "ULTRACEMCO",
    "NTPC Limited": "NTPC", "Power Grid": "POWERGRID", "Coal India": "COALINDIA",
    "Tata Steel": "TATASTEEL", "Jio Financial Services": "JIOFIN", "Trent Limited": "TRENT",
    "Hindalco Industries": "HINDALCO", "Bharat Electronics": "BEL", "Tech Mahindra": "TECHM",
    "Grasim Industries": "GRASIM", "Adani Enterprises": "ADANIENT", "IndiGo (InterGlobe)": "INDIGO",
    "Wipro": "WIPRO", "Apollo Hospitals": "APOLLOHOSP", "Cipla": "CIPLA", "Dr. Reddy's": "DRREDDY",
    "Eicher Motors": "EICHERMOT", "Bajaj Auto": "BAJAJ-AUTO", "Bajaj Finserv": "BAJAJFINSV",
    "Nestle India": "NESTLEIND", "Shriram Finance": "SHRIRAMFIN", "HDFC Life": "HDFCLIFE",
    "SBI Life": "SBILIFE", "Asian Paints": "ASIANPAINT", "JSW Steel": "JSWSTEEL",
    "Max Healthcare": "MAXHEALTH", "Tata Consumer Products": "TATACONSUM", "ONGC": "ONGC"
}

# Sidebar control panel
st.sidebar.header("Navigation Panel")
selected_stock_name = st.sidebar.selectbox("Select Nifty 50 Asset:", list(nifty50_tickers.keys()))
timeframe = st.sidebar.selectbox("Choose Chart Horizon Data Profile:", ["1 Hour Horizon (1m intervals)", "1 Day Horizon (15m intervals)"])
ticker_token = nifty50_tickers[selected_stock_name]

# 2. RUN LIVE DATA PROCESSING & REST PAYLOADS
# Toggling data intervals cleanly based on timeframe selector
if "1 Hour" in timeframe:
    api_range, api_interval = "2d", "1m"
    projection_steps = 60 # 60 minutes future projection
    label_step = "Minute"
else:
    api_range, api_interval = "1mo", "15m"
    projection_steps = 32 # 1 day future projection (approx 32 fifteen-minute market slots)
    label_step = "Period"

with st.spinner("Compiling structural data feeds..."):
    try:
        stock_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_token}.NS?range={api_range}&interval={api_interval}"
        req_stock = urllib.request.Request(stock_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_stock) as resp:
            data = json.loads(resp.read().decode())
            
        timestamps = data['chart']['result'][0]['timestamp']
        raw_prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
        
        # Clean data mappings
        clean_timestamps = []
        prices = []
        for t, p in zip(timestamps, raw_prices):
            if p is not None:
                clean_timestamps.append(datetime.datetime.fromtimestamp(t))
                prices.append(p)
                
        current_price = prices[-1]

        # Fetch Macro variables (Brent Crude Oil Tracker)
        crude_url = "https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?range=5d&interval=1d"
        req_crude = urllib.request.Request(crude_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_crude) as resp_crude:
            crude_data = json.loads(resp_crude.read().decode())
        crude_prices = [c for c in crude_data['chart']['result'][0]['indicators']['quote'][0]['close'] if c is not None]
        latest_crude = crude_prices[-1] if crude_prices else 73.5
        
    except Exception as e:
        st.error(f"Network processing delay. Defaulting template: {str(e)}")
        current_price = 1500.0
        latest_crude = 73.5
        clean_timestamps = [datetime.datetime.now() - datetime.timedelta(minutes=i) for i in range(100, 0, -1)]
        prices = [1480 + (i * 0.2) for i in range(100)]

# Math engines
def run_ema(lst, p):
    if len(lst) < p: p = len(lst)
    k = 2 / (p + 1)
    e = lst[0]
    for x in lst[1:]: e = (x * k) + (e * (1 - k))
    return e

latest_ema_50 = run_ema(prices, 50)
latest_ema_100 = run_ema(prices, 100)

gains = [prices[i] - prices[i-1] for i in range(1, len(prices[-15:])) if prices[i] > prices[i-1]]
losses = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices[-15:])) if prices[i] < prices[i-1]]
avg_gain = sum(gains)/14 if gains else 0.1
avg_loss = sum(losses)/14 if losses else 0.1
rs = avg_gain / (avg_loss + 1e-10)
latest_rsi = 100 - (100 / (1 + rs))

# 3. CORE BUY / NO BUY DECISION MATRIX DISPLAY
st.markdown("---")
score = 0
reasons_positive = []
reasons_negative = []

if current_price > latest_ema_50:
    score += 40
    reasons_positive.append(f"Price (₹{current_price:.2f}) is trading above its 50-period EMA (₹{latest_ema_50:.2f}), confirming near-term upward momentum.")
else:
    reasons_negative.append(f"Price (₹{current_price:.2f}) sits below its 50-period EMA (₹{latest_ema_50:.2f}), showing local structural weakness.")

if current_price > latest_ema_100:
    score += 30
    reasons_positive.append("The asset is successfully maintaining its baseline above the key institutional 100-period EMA line.")
else:
    reasons_negative.append("Warning: Price has slipped below its 100-period EMA floor support framework.")

if 30 <= latest_rsi <= 65:
    score += 30
    reasons_positive.append(f"RSI indicator is balanced at {latest_rsi:.1f}, leaving ample technical runway before hitting overbought thresholds.")
else:
    reasons_negative.append(f"RSI reading is showing localized exhaustion signals at {latest_rsi:.1f}.")

if latest_crude < 80.0:
    score += 10
    reasons_positive.append(f"Macro Tailwinds: Brent crude down at ${latest_crude:.2f}/bbl. Lower operational raw input values support corporate margins.")
else:
    reasons_negative.append(f"Macro Headwinds: High crude asset price levels are squeezing corporate margins.")

col_v1, col_v2 = st.columns([1, 2])
with col_v1:
    st.subheader("🚨 Algorithmic Verdict Dashboard")
    if score >= 75:
        st.success(f"### 🎯 PRECISES BUY OPINION")
        st.metric(label="System Health Score", value=f"{score} / 110", delta="PASSED STRATEGY")
    else:
        st.error(f"### 🚫 NO BUY (HOLD / AVOID)")
        st.metric(label="System Health Score", value=f"{score} / 110", delta="- FAILED STRATEGY", delta_color="inverse")
    st.write(f"**Current Price:** ₹{current_price:.2f}")
    st.write(f"**RSI Value:** {latest_rsi:.2f}")

with col_v2:
    st.subheader("📊 Dynamic Market Drivers Analysis")
    st.markdown("**Positive Catalysts:**")
    for r in reasons_positive: st.markdown(f"* 🟢 {r}")
    if reasons_negative:
        st.markdown("**Downside Operational Risks:**")
        for r in reasons_negative: st.markdown(f"* 🔴 {r}")

# 4. UNIFIED HISTORICAL & REAL-TIME BLUE FUTURE PROJECTION CHART
st.markdown("---")
st.subheader(f"📈 Integrated Forecasting & Performance Chart: {selected_stock_name}")
st.caption("Historical path data transforms smoothly into a bright blue predictive forecast visualization.")

# Create the projection modeling arrays
chart_df = pd.DataFrame({
    "Historical Price": prices + [None] * projection_steps,
    "Blue Future Projection": [None] * (len(prices) - 1) + [current_price] + [
        current_price * (1 + (i * 0.0003 if score >= 75 else i * -0.0002)) for i in range(1, projection_steps + 1)
    ]
})

# Plotting the unified chart with custom line styling definitions
st.line_chart(chart_df, color=["#757575", "#0d47a1"])

# Informational Footer Breakdown
st.info(f"💡 **Chart Info:** The grey line shows your selected asset's real-time history. The bright **BLUE line** projects the mathematical model path forward into the next window based on your data horizon parameters.")
