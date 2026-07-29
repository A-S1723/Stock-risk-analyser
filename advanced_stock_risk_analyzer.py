
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

import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def get_news_headlines(ticker, max_items=10):
    # Yahoo Finance RSS uses the stock symbol in the URL
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&lang=en-US"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "xml")
    items = soup.find_all("item")[:max_items]

    headlines = []
    for item in items:
        title = item.title.text if item.title else ""
        link = item.link.text if item.link else ""
        pub_date = item.pubDate.text if item.pubDate else ""
        headlines.append({
            "title": title,
            "link": link,
            "pub_date": pub_date
        })
    return headlines
RISK_KEYWORDS = [
    "lawsuit", "investigation", "fraud", "probe", "downgrade",
    "miss", "missed expectations", "layoffs", "bankruptcy",
    "regulator", "sec", "short seller", "hack", "breach"
]

def score_news_risk(headlines):
    if not headlines:
        return 0, 0, 0  # news_risk, avg_sentiment, keyword_hits

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

    # Base news risk from sentiment (negative → higher risk)
    # sentiment ~ [-1, 1] → risk ~ [0, 40]
    sentiment_risk = max(0, (0 - avg_sentiment) * 20)

    # Extra risk from keywords
    keyword_risk = min(60, keyword_hits * 5)

    news_risk = min(100, sentiment_risk + keyword_risk)
    return news_risk, avg_sentiment, keyword_hits
ticker = st.text_input("Enter stock ticker", "AAPL")

if ticker:
    # your existing risk calculations...
    base_risk_score = score  # whatever you already compute

    st.subheader("News & Sentiment")

    headlines = get_news_headlines(ticker)
    news_risk, avg_sentiment, keyword_hits = score_news_risk(headlines)

    st.write(f"**Average news sentiment:** {avg_sentiment:.2f}")
    st.write(f"**Risk keywords detected:** {keyword_hits}")
    st.write(f"**News-based risk score:** {news_risk:.1f} / 100")

    # Show headlines
    for h in headlines:
        st.markdown(f"- [{h['title']}]({h['link']})  \n  *{h['pub_date']}*")

    # Combine with your existing risk score
    total_risk_with_news = min(100, base_risk_score + news_risk * 0.4)

    st.subheader("Final Risk Score (with News)")
    st.write(f"**Base risk:** {base_risk_score:.1f}")
    st.write(f"**News adjustment:** {news_risk * 0.4:.1f}")
    st.write(f"**Final risk score:** {total_risk_with_news:.1f} / 100")

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

import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def get_news_headlines(ticker, max_items=10):
    # Yahoo Finance RSS uses the stock symbol in the URL
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&lang=en-US"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "xml")
    items = soup.find_all("item")[:max_items]

    headlines = []
    for item in items:
        title = item.title.text if item.title else ""
        link = item.link.text if item.link else ""
        pub_date = item.pubDate.text if item.pubDate else ""
        headlines.append({
            "title": title,
            "link": link,
            "pub_date": pub_date
        })
    return headlines
RISK_KEYWORDS = [
    "lawsuit", "investigation", "fraud", "probe", "downgrade",
    "miss", "missed expectations", "layoffs", "bankruptcy",
    "regulator", "sec", "short seller", "hack", "breach"
]

def score_news_risk(headlines):
    if not headlines:
        return 0, 0, 0  # news_risk, avg_sentiment, keyword_hits

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

    # Base news risk from sentiment (negative → higher risk)
    # sentiment ~ [-1, 1] → risk ~ [0, 40]
    sentiment_risk = max(0, (0 - avg_sentiment) * 20)

    # Extra risk from keywords
    keyword_risk = min(60, keyword_hits * 5)

    news_risk = min(100, sentiment_risk + keyword_risk)
    return news_risk, avg_sentiment, keyword_hits
ticker = st.text_input("Enter stock ticker", "AAPL")

if ticker:
    # your existing risk calculations...
    base_risk_score = total_risk_score  # whatever you already compute

    st.subheader("News & Sentiment")

    headlines = get_news_headlines(ticker)
    news_risk, avg_sentiment, keyword_hits = score_news_risk(headlines)

    st.write(f"**Average news sentiment:** {avg_sentiment:.2f}")
    st.write(f"**Risk keywords detected:** {keyword_hits}")
    st.write(f"**News-based risk score:** {news_risk:.1f} / 100")

    # Show headlines
    for h in headlines:
        st.markdown(f"- [{h['title']}]({h['link']})  \n  *{h['pub_date']}*")

    # Combine with your existing risk score
    total_risk_with_news = min(100, base_risk_score + news_risk * 0.4)

    st.subheader("Final Risk Score (with News)")
    st.write(f"**Base risk:** {base_risk_score:.1f}")
    st.write(f"**News adjustment:** {news_risk * 0.4:.1f}")
    st.write(f"**Final risk score:** {total_risk_with_news:.1f} / 100")

