import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.title("📊 Advanced Stock Risk Analyzer")

# -----------------------------
# Utility Functions
# -----------------------------

def calculate_max_drawdown(prices):
    cumulative_max = np.maximum.accumulate(prices)
    drawdown = (prices - cumulative_max) / cumulative_max
    return drawdown.min()

def calculate_var(returns, confidence=0.95):
    return np.percentile(returns, (1 - confidence) * 100)

def calculate_es(returns, confidence=0.95):
    var = calculate_var(returns, confidence)
    return returns[returns < var].mean()

# -----------------------------
# News & Sentiment Engine
# -----------------------------

analyzer = SentimentIntensityAnalyzer()

def get_news_headlines(ticker, max_items=10):
    def get_news_headlines(ticker, max_items=10):
    api_key = Wr4D8qAmmOPADUCV5uSiSIy0SXSetIak
    url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={ticker}&limit={max_items}&apikey={api_key}"

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    headlines = []
    for item in data:
        headlines.append({
            "title": item.get("title", ""),
            "link": item.get("url", ""),
            "pub_date": item.get("publishedDate", "")
        })

    return headlines
  

RISK_KEYWORDS = [
    "lawsuit", "investigation", "fraud", "probe", "downgrade",
    "miss", "missed expectations", "layoffs", "bankruptcy",
    "regulator", "sec", "short seller", "hack", "breach"
]

def score_news_risk(headlines):
    if not headlines:
        return 0, 0, 0

    sentiments = []
    keyword_hits = 0

    for h in headlines:
        text = h["title"].lower()
        vs = analyzer.polarity_scores(text)
        sentiments.append(vs["compound"])

        for kw in RISK_KEYWORDS:
            if kw in text:
                keyword_hits += 1

    avg_sentiment = sum(sentiments) / len(sentiments)
    sentiment_risk = max(0, (0 - avg_sentiment) * 20)
    keyword_risk = min(60, keyword_hits * 5)

    news_risk = min(100, sentiment_risk + keyword_risk)
    return news_risk, avg_sentiment, keyword_hits

# -----------------------------
# UI
# -----------------------------

ticker = st.text_input("Enter stock ticker", "AAPL")

if st.button("Analyze"):

    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="1y")

        if hist.empty:
            st.error("Invalid ticker or no data available.")
        else:

            # Create tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "📈 Price Chart",
                "📊 Risk Metrics",
                "🧩 Fundamentals",
                "📰 News & Sentiment"
            ])

            # -----------------------------
            # Tab 1 — Price Chart
            # -----------------------------
            with tab1:
                st.subheader("📈 Price Chart (1 Year)")
                st.line_chart(hist["Close"])

            # -----------------------------
            # Tab 2 — Risk Metrics
            # -----------------------------
            returns = hist["Close"].pct_change().dropna()
            volatility = np.std(returns) * np.sqrt(252)
            beta = data.info.get("beta", None)
            max_drawdown = calculate_max_drawdown(hist["Close"].values)
            var_95 = calculate_var(returns)
            es_95 = calculate_es(returns)

            with tab2:
                st.subheader("📊 Risk Metrics")
                st.write(f"**Volatility:** {volatility:.4f}")
                st.write(f"**Beta:** {beta}")
                st.write(f"**Max Drawdown:** {max_drawdown:.4f}")
                st.write(f"**Value at Risk (95%):** {var_95:.4f}")
                st.write(f"**Expected Shortfall (95%):** {es_95:.4f}")

                score = 0
                score += min(volatility * 100, 40)
                score += min(abs(max_drawdown) * 100, 40)
                score += 20 if beta and beta > 1.2 else 5

                base_risk_score = score

                st.subheader("🔍 Final Risk Score")
                st.write(f"**Risk Score:** {round(score, 2)} / 100")

            # -----------------------------
            # Tab 3 — Fundamentals
            # -----------------------------
            with tab3:
                st.subheader("📚 Fundamentals")
                st.write(f"**Company:** {data.info.get('longName', 'N/A')}")
                st.write(f"**Sector:** {data.info.get('sector', 'N/A')}")
                st.write(f"**Market Cap:** {data.info.get('marketCap', 'N/A')}")
                st.write(f"**P/E Ratio:** {data.info.get('trailingPE', 'N/A')}")
                st.write(f"**52 Week High:** {data.info.get('fiftyTwoWeekHigh', 'N/A')}")
                st.write(f"**52 Week Low:** {data.info.get('fiftyTwoWeekLow', 'N/A')}")

            # -----------------------------
            # Tab 4 — News & Sentiment
            # -----------------------------
            with tab4:
                st.subheader("📰 News & Sentiment")

                headlines = get_news_headlines(ticker)
                news_risk, avg_sentiment, keyword_hits = score_news_risk(headlines)

                st.write(f"**Average news sentiment:** {avg_sentiment:.2f}")
                st.write(f"**Risk keywords detected:** {keyword_hits}")
                st.write(f"**News-based risk score:** {news_risk:.1f} / 100")

                st.markdown("---")
                st.write("### Latest Headlines")

                for h in headlines:
                    st.markdown(f"- [{h['title']}]({h['link']})  \n  *{h['pub_date']}*")

                total_risk_with_news = min(100, base_risk_score + news_risk * 0.4)

                st.markdown("---")
                st.subheader("🎯 Final Risk Score (with News)")
                st.write(f"**Base risk:** {base_risk_score:.1f}")
                st.write(f"**News adjustment:** {news_risk * 0.4:.1f}")
                st.write(f"**Final risk score:** {total_risk_with_news:.1f} / 100")

    except Exception as e:
        st.error(f"Error: {e}")


