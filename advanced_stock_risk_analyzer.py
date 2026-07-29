import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

st.title("Advanced Stock Risk Analyzer")

ticker = st.text_input("Enter a stock ticker (e.g., AAPL, TSLA):")

def calculate_max_drawdown(prices):
    cumulative_max = np.maximum.accumulate(prices)
    drawdown = (prices - cumulative_max) / cumulative_max
    return drawdown.min()

def calculate_var(returns, confidence=0.95):
    return np.percentile(returns, (1 - confidence) * 100)

def calculate_es(returns, confidence=0.95):
    var = calculate_var(returns, confidence)
    return returns[returns < var].mean()

if st.button("Analyze"):
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="1y")

        if hist.empty:
            st.error("Invalid ticker or no data available.")
        else:
            st.subheader("📈 Price Chart (1 Year)")
            st.line_chart(hist["Close"])

            returns = hist["Close"].pct_change().dropna()

            volatility = np.std(returns) * np.sqrt(252)
            beta = data.info.get("beta", None)
            max_drawdown = calculate_max_drawdown(hist["Close"].values)
            var_95 = calculate_var(returns)
            es_95 = calculate_es(returns)

            st.subheader("📊 Risk Metrics")
            st.write(f"**Volatility:** {volatility:.4f}")
            st.write(f"**Beta:** {beta}")
            st.write(f"**Max Drawdown:** {max_drawdown:.4f}")
            st.write(f"**Value at Risk (95%):** {var_95:.4f}")
            st.write(f"**Expected Shortfall (95%):** {es_95:.4f}")

            st.subheader("📚 Fundamentals")
            st.write(f"**Company:** {data.info.get('longName', 'N/A')}")
            st.write(f"**Sector:** {data.info.get('sector', 'N/A')}")
            st.write(f"**Market Cap:** {data.info.get('marketCap', 'N/A')}")
            st.write(f"**P/E Ratio:** {data.info.get('trailingPE', 'N/A')}")
            st.write(f"**52 Week High:** {data.info.get('fiftyTwoWeekHigh', 'N/A')}")
            st.write(f"**52 Week Low:** {data.info.get('fiftyTwoWeekLow', 'N/A')}")

            score = 0
            score += min(volatility * 100, 40)
            score += min(abs(max_drawdown) * 100, 40)
            score += 20 if beta and beta > 1.2 else 5

            st.subheader("🔍 Final Risk Score")
            st.write(f"**Risk Score:** {round(score, 2)} / 100")

    except Exception as e:
        st.error(f"Error: {e}")

