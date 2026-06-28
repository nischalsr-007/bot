import datetime
import json
import urllib.request
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# 1. PREMIUM CORES & LAYOUT THEME OVERRIDES
st.set_page_config(page_title="Nifty 50 Terminal", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0A0A0C !important;
        color: #E2E8F0 !important;
        font-family: 'Garamond', 'Georgia', serif !important;
    }
    h1, h2, h3, h4 {
        font-family: 'Garamond', 'Georgia', serif !important;
        color: #D4AF37 !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.5rem !important; }
    h3 { font-size: 1.2rem !important; }
    p, span, li { font-size: 1rem !important; line-height: 1.5 !important; }
    
    .metric-pass { color: #52B788 !important; font-weight: 600; }
    .metric-fail { color: #E63946 !important; font-weight: 600; }
    .metric-info { color: #4EA8DE !important; font-weight: 600; }
    
    .premium-card {
        background-color: #121216 !important;
        border: 1px solid #1E1E24;
        padding: 20px;
        border-radius: 6px;
        box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ NIFTY 50 RISK MANIPULATION SYSTEM")
st.markdown("<p style='font-size:1rem; font-style:italic; color:#8A92A6; margin-top:-10px;'>Condition-Driven Threat & Yield Assessment Matrix</p>", unsafe_allow_html=True)

# 2. SELECTION CONFIGURATIONS
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

st.sidebar.header("🕹️ CONTROL DASHBOARD")
selected_stock_name = st.sidebar.selectbox("Select Target Token Asset:", list(nifty50_tickers.keys()))
timeframe = st.sidebar.selectbox("Choose Strategic Window Profile:", [
    "15 Minutes Strategy (Intraday)", 
    "1 Hour Strategy (Intraday Scalp)", 
    "1 Day Strategy (Swing Momentum)", 
    "1 Week Strategy (Position Cycle)", 
    "1 Month Strategy (Macro Structural)"
])
ticker_token = nifty50_tickers[selected_stock_name]

# Adjust strategy parameters cleanly across intervals
if "15 Minutes" in timeframe:
    api_range, api_interval = "1d", "1m"
    projection_steps, profit_pct, loss_pct = 15, 0.005, 0.002
    holding_delta = datetime.timedelta(minutes=15)
elif "1 Hour" in timeframe:
    api_range, api_interval = "2d", "1m"
    projection_steps, profit_pct, loss_pct = 60, 0.015, 0.006
    holding_delta = datetime.timedelta(hours=1)
elif "1 Day" in timeframe:
    api_range, api_interval = "1mo", "15m"
    projection_steps, profit_pct, loss_pct = 32, 0.035, 0.012
    holding_delta = datetime.timedelta(days=1)
elif "1 Week" in timeframe:
    api_range, api_interval = "3mo", "1d"
    projection_steps, profit_pct, loss_pct = 5, 0.060, 0.020
    holding_delta = datetime.timedelta(weeks=1)
else: # 1 Month Strategy
    api_range, api_interval = "1y", "1d"
    projection_steps, profit_pct, loss_pct = 22, 0.120, 0.040
    holding_delta = datetime.timedelta(days=30)

# 3. SAFETY CLOSURE CALENDAR MANAGEMENT ENGINE
def get_operational_fuse_deadline(duration_delta):
    current_time = datetime.datetime.now()
    raw_target_time = current_time + duration_delta
    
    market_open_hour, market_open_minute = 9, 15
    market_close_hour, market_close_minute = 15, 30

    if raw_target_time.time() > datetime.time(market_close_hour, market_close_minute) or raw_target_time.time() < datetime.time(market_open_hour, market_open_minute):
        if raw_target_time.time() > datetime.time(market_close_hour, market_close_minute):
            raw_target_time += datetime.timedelta(days=1)
        raw_target_time = raw_target_time.replace(hour=9, minute=30, second=0, microsecond=0)

    # Filter exchange weekend closures
    if raw_target_time.weekday() == 5:
        raw_target_time += datetime.timedelta(days=2)
    elif raw_target_time.weekday() == 6:
        raw_target_time += datetime.timedelta(days=1)
        
    return raw_target_time.strftime('%Y-%m-%d %I:%M %p IST')

formatted_exit_time = get_operational_fuse_deadline(holding_delta)

# 4. REMOTE DATA INTEGRATION PROCESSING
try:
    stock_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_token}.NS?range={api_range}&interval={api_interval}"
    req_stock = urllib.request.Request(stock_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_stock) as resp:
        data = json.loads(resp.read().decode())
    prices = [p for p in data['chart']['result'][0]['indicators']['quote'][0]['close'] if p is not None]
    current_price = prices[-1]

    crude_url = "https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?range=5d&interval=1d"
    req_crude = urllib.request.Request(crude_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_crude) as resp_crude:
        crude_data = json.loads(resp_crude.read().decode())
    crude_prices = [c for c in crude_data['chart']['result'][0]['indicators']['quote'][0]['close'] if c is not None]
    latest_crude = crude_prices[-1] if crude_prices else 74.0
except Exception:
    current_price = 2200.0
    latest_crude = 74.0
    prices = [2180, 2190, 2200]

# Strategy Target Calculations
target_profit_value = current_price * (1 + profit_pct)
target_stop_value = current_price * (1 - loss_pct)

# Structural technical math blocks
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
avg_gain = sum(gains)/14 if gains else 0.5
avg_loss = sum(losses)/14 if losses else 0.5
rs = avg_gain / (avg_loss + 1e-10)
latest_rsi = 100 - (100 / (1 + rs))

# 5. CORE SCORING LOGIC PROCESSING
score = 0
reasons_positive = []
reasons_negative = []

if current_price > latest_ema_50:
    score += 40
    reasons_positive.append(f"Price trending safely north of the 50-period moving structural line.")
else:
    reasons_negative.append(f"Price registered lower than the short-term 50-period structural trendline.")

if current_price > latest_ema_100:
    score += 30
    reasons_positive.append("Long-term secondary support layers remain intact.")
else:
    reasons_negative.append("Asset tracking framework dropped below institutional 100-period support floors.")

if 30 <= latest_rsi <= 65:
    score += 30
    reasons_positive.append(f"RSI oscillator signals healthy parameters with clear operational runway ({latest_rsi:.1f}).")
else:
    reasons_negative.append(f"RSI reading records localized trend over-exhaustion risk profiles ({latest_rsi:.1f}).")

if latest_crude < 80.0:
    score += 10
    reasons_positive.append(f"Macro Tailwinds: Depressed crude oil processing curbs retail input pricing layers.")
else:
    reasons_negative.append(f"Macro Headwinds: High external commodity prices risk industrial margin squeezes.")

# 6. RENDER INTERFACE DISPLAY MATRIX
st.markdown("---")
col_v1, col_v2 = st.columns(2)

with col_v1:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    if score >= 75:
        st.markdown(f"<h2>System Analysis: <span class='metric-pass'>BUY OPINION</span></h2>", unsafe_allow_html=True)
        st.markdown(f"<h3>Strategy Matrix Score: <span class='metric-pass'>{score} / 110</span></h3>", unsafe_allow_html=True)
        st.markdown(f"<h3>Take-Profit Target: <span class='metric-pass'>₹{target_profit_value:.2f} (+{profit_pct*100:.1f}%)</span></h3>", unsafe_allow_html=True)
        st.markdown(f"<h3>Stop-Loss Guard: <span class='metric-fail'>₹{target_stop_value:.2f} (-{loss_pct*100:.1f}%)</span></h3>", unsafe_allow_html=True)
        st.markdown(f"<h3>Hard Time Fuse Deadline: <span class='metric-info'>{formatted_exit_time}</span></h3>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h2>System Analysis: <span class='metric-fail'>NO BUY (AVOID / HOLD)</span></h2>", unsafe_allow_html=True)
        st.markdown(f"<h3>Strategy Matrix Score: <span class='metric-fail'>{score} / 110</span></h3>", unsafe_allow_html=True)
        st.markdown(f"<h3>Hard Time Fuse Deadline: <span style='color:#718096;'>N/A (No entry triggered)</span></h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#A0AEC0;'><b>Last Frame Traded Price:</b> ₹{current_price:.2f}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_v2:
    st.markdown("<div class='premium-card' style='height:100%;'>", unsafe_allow_html=True)
    st.markdown("<h3>📋 SIGNAL FACTOR METRIC BREAKDOWN</h3>", unsafe_allow_html=True)
    for r in reasons_positive:
        st.markdown(f"<p>🏁 <span class='metric-pass'>Passed:</span> {r}</p>", unsafe_allow_html=True)
    for r in reasons_negative:
        st.markdown(f"<p>⚠️ <span class='metric-fail'>Caution:</span> {r}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 7. PERFORMANCE DATA GRAPH LAYERS
st.markdown("---")
st.subheader("📊 MODEL PERFORMANCE PROJECTION CANVA")

chart_df = pd.DataFrame({
    "Historical Close Trace": prices + [None] * projection_steps,
    "Model Future Path": [None] * (len(prices) - 1) + [current_price] + [
        current_price * (1 + (i * (profit_pct/projection_steps) if score >= 75 else i * -(loss_pct/projection_steps))) for i in range(1, projection_steps + 1)
    ]
})
st.line_chart(chart_df, color=["#4A4A5A", "#00BFFF"])

st.markdown("---")
st.subheader("🖥️ LIVE TRADINGVIEW HIGH-RESOLUTION TERMINAL")

tv_widget_html = f"""
<div class="tradingview-widget-container" style="height:650px;width:100%;">
  <div id="tradingview_operational_terminal" style="height:650px;"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "width": "100%",
    "height": 650,
    "symbol": "NSE:{ticker_token}",
    "interval": "D",
    "timezone": "Asia/Kolkata",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#0A0A0C",
    "enable_publishing": false,
    "hide_side_toolbar": false,
    "withlookahead": true,
    "allow_symbol_change": true,
    "container_id": "tradingview_operational_terminal",
    "studies": [
      "RSI@tv-basicstudies",
      "MASimple@tv-basicstudies"
    ]
  }});
  </script>
</div>
"""
components.html(tv_widget_html, height=660)
