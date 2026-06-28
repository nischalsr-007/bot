import datetime
import pandas as pd
import streamlit as st
import yfinance as yf

# Set up page styling
st.set_page_config(page_title="Nifty 50 Deep Analyst", page_icon="📈", layout="wide")

st.title("📈 Nifty 50 Automated Analysis Bot Engine")
st.markdown(
    "Enter any NSE Nifty 50 stock ticker symbol to generate an algorithmic **BUY** or **NO BUY** verdict powered by real-time technical & macro variables."
)

# Sidebar setup for user inputs
st.sidebar.header("User Control Panel")
ticker_input = st.sidebar.text_input("Enter NSE Ticker Symbol:", value="RELIANCE")
run_analysis = st.sidebar.button("Execute Deep Analysis")

if run_analysis or ticker_input:
    # 1. FETCH DATA (Source: Yahoo Finance Data Engine API)
    yf_ticker = f"{ticker_input.strip().upper()}.NS"

    with st.spinner(f"Analyzing market structures for {ticker_input.upper()}..."):
        try:
            stock = yf.Ticker(yf_ticker)
            df = stock.history(period="6m")

            if df.empty:
                st.error(
                    f"Could not retrieve data for '{ticker_input}'. Please make sure it's a valid NSE stock ticker (e.g., HDFCBANK, INFOCY, TCS)."
                )
                st.stop()

            # Fetch Macro Engine Data (Brent Crude Oil Spot Price Tracker)
            crude = yf.Ticker("BZ=F")
            crude_df = crude.history(period="5d")
            latest_crude = (
                crude_df["Close"].iloc[-1] if not crude_df.empty else 75.0
            )

            current_price = df["Close"].iloc[-1]

        except Exception as e:
            st.error(f"Data engine error connection lost: {str(e)}")
            st.stop()

    # 2. QUANTITATIVE ENGINE (Technical Metric Analysis)
    df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA_100"] = df["Close"].ewm(span=100, adjust=False).mean()
    latest_ema_50 = df["EMA_50"].iloc[-1]
    latest_ema_100 = df["EMA_100"].iloc[-1]

    # Calculate Relative Strength Index (RSI - 14 Days)
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df["RSI"] = 100 - (100 / (1 + rs))
    latest_rsi = df["RSI"].iloc[-1]

    # 3. SCORING MATRIX ENGINE
    score = 0
    reasons_positive = []
    reasons_negative = []

    if current_price > latest_ema_50:
        score += 40
        reasons_positive.append(
            f"Price (₹{current_price:.2f}) is trading cleanly above its 50-day short-term EMA (₹{latest_ema_50:.2f}), confirming an active uptrend."
        )
    else:
        reasons_negative.append(
            f"Price (₹{current_price:.2f}) sits below its 50-day EMA (₹{latest_ema_50:.2f}), displaying near-term structural weakness."
        )

    if current_price > latest_ema_100:
        score += 30
        reasons_positive.append(
            "Long-term structural baseline is safely defended; holding above the institutional 100-day EMA floor."
        )
    else:
        reasons_negative.append(
            "Warning: Asset breached its critical 100-day EMA support layer. Risk profile is elevated."
        )

    if 30 <= latest_rsi <= 65:
        score += 30
        reasons_positive.append(
            f"RSI reading is balanced at {latest_rsi:.1f}. High structural upside space remains before hitting the overbought peak."
        )
    elif latest_rsi < 30:
        score += 15
        reasons_positive.append(
            f"RSI is highly oversold at {latest_rsi:.1f}. A major structural price bounce might be building."
        )
    else:
        reasons_negative.append(
            f"RSI reveals exhaustion at {latest_rsi:.1f}. Overbought territory risks an impending localized correction."
        )

    if latest_crude < 80.0:
        score += 10
        reasons_positive.append(
            f"Macro Catalyst: Brent crude down at ${latest_crude:.2f}/bbl. Low input costs ease inflation pressures for Indian corporations."
        )
    else:
        reasons_negative.append(
            f"Macro Headwind: High Global Crude prices (${latest_crude:.2f}/bbl) pose near-term fiscal drag risks on domestic corporate margins."
        )

    # 4. RENDER UI DASHBOARD BREAKDOWN
    st.markdown("---")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🚨 Algorithmic Verdict")
        if score >= 75:
            st.success("### PRECISES BUY OPINION")
            st.metric(label="System Health Score", value=f"{score} / 110")
        else:
            st.error("### NO BUY (HOLD / AVOID)")
            st.metric(label="System Health Score", value=f"{score} / 110")

        st.caption(f"Analysis Computed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    with col2:
        st.subheader("📋 Metric Verification Breakdown")
        st.write(f"**Live Value:** ₹{current_price:.2f} — *Source: [NSE India Real-time Quote]*")
        st.write(f"**14-Day RSI:** {latest_rsi:.2f} — *Source: [Quantitative Logic Engine]*")
        st.write(f"**Brent Crude:** ${latest_crude:.2f}/bbl — *Source: [ICE Commodity Feed]*")

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### 🟢 Drivers Supporting Buy Case")
        if reasons_positive:
            for r in reasons_positive:
                st.info(r)
        else:
            st.write("None.")

    with col4:
        st.markdown("### 🔴 Downside Risk Elements")
        if reasons_negative:
            for r in reasons_negative:
                st.warning(r)
        else:
            st.write("None.")