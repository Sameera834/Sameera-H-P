import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from textblob import TextBlob

# ===================== LOAD DATA ===================== #
# Removed parse_dates here to avoid "Missing column provided to 'parse_dates'" error

forecast_df = pd.read_csv(
    "D:\\Amdox intenship\\Data analytics project\\bitcoin_analysis\\bitcoin_analysis\\model_forecast.csv"
)

base_df = pd.read_csv(
    "D:\\Amdox intenship\\Data analytics project\\bitcoin_analysis\\bitcoin_analysis\\bitcoin_preprocessed_daily.csv"
)

metrics_df = pd.read_csv(
    "D:\\Amdox intenship\\Data analytics project\\bitcoin_analysis\\bitcoin_analysis\\model_metrics.csv"
)

news_df = pd.read_csv(
    "D:\\Amdox intenship\\Data analytics project\\bitcoin_analysis\\bitcoin_analysis\\news .csv"
)

# ---- Date parsing done safely AFTER loading ----
# If your date column name is different (like 'Date'), map it to 'Timestamp' here.

# For forecast_df
if "Timestamp" in forecast_df.columns:
    forecast_df["Timestamp"] = pd.to_datetime(forecast_df["Timestamp"])
elif "Date" in forecast_df.columns:
    forecast_df["Timestamp"] = pd.to_datetime(forecast_df["Date"])
else:
    st.error("❌ No timestamp/date column found in model_forecast.csv")
    st.stop()

# For base_df
if "Timestamp" in base_df.columns:
    base_df["Timestamp"] = pd.to_datetime(base_df["Timestamp"])
elif "Date" in base_df.columns:
    base_df["Timestamp"] = pd.to_datetime(base_df["Date"])
else:
    st.error("❌ No timestamp/date column found in bitcoin_preprocessed_daily.csv")
    st.stop()

# For news_df
if "DATETIME" in news_df.columns:
    news_df["DATETIME"] = pd.to_datetime(news_df["DATETIME"])
elif "Date" in news_df.columns:
    news_df["DATETIME"] = pd.to_datetime(news_df["Date"])
else:
    st.error("❌ No DATETIME/date column found in news .csv")
    st.stop()

# Ensure sorted
forecast_df.sort_values("Timestamp", inplace=True)
base_df.sort_values("Timestamp", inplace=True)

# Feature engineering
if "Return" not in base_df.columns:
    base_df["Return"] = base_df["Close"].pct_change()

base_df["MA_30"] = base_df["Close"].rolling(window=30).mean()
base_df["Volatility_30"] = base_df["Return"].rolling(window=30).std()

# ===================== STREAMLIT CONFIG ===================== #
st.set_page_config(page_title="Crypto Forecast Dashboard", layout="wide")
st.title("📈 Cryptocurrency & Stock Forecasting Dashboard")

tabs = st.tabs([
    "📊 Forecast Dashboard",
    "📍 Live Market Analysis",
    "📰 Sentiment & News Influence",
    "📋 Model Metrics",
    "ℹ About"
])

# ===========================================================
# ===================== FORECAST TAB =========================
# ===========================================================
with tabs[0]:
    st.subheader("Forecast Analytics Dashboard")

    model_select = st.multiselect(
        "Select Forecast Models",
        ["Actual_Close", "ARIMA_Forecast", "SARIMA_Forecast", "Prophet_Forecast", "LSTM_Forecast"],
        default=["Actual_Close", "LSTM_Forecast"]
    )

    # Forecast vs Actual
    fig1 = go.Figure()
    for m in model_select:
        if m in forecast_df.columns:
            fig1.add_trace(go.Scatter(
                x=forecast_df["Timestamp"],
                y=forecast_df[m],
                mode="lines",
                name=m
            ))
        else:
            st.warning(f"⚠ Column '{m}' not found in model_forecast.csv")

    fig1.update_layout(template="plotly_dark", title="Forecast vs Actual")
    st.plotly_chart(fig1, use_container_width=True)

    # Candlestick + Volume
    fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
    fig2.add_trace(go.Candlestick(
        x=base_df["Timestamp"],
        open=base_df["Open"],
        high=base_df["High"],
        low=base_df["Low"],
        close=base_df["Close"]
    ), row=1, col=1)
    fig2.add_trace(go.Bar(x=base_df["Timestamp"], y=base_df["Volume"]), row=2, col=1)
    fig2.update_layout(template="plotly_dark", title="Candlestick Chart + Volume")
    st.plotly_chart(fig2, use_container_width=True)

    # Close vs 30-Day MA
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=base_df["Timestamp"], y=base_df["Close"], name="Close"))
    fig3.add_trace(go.Scatter(
        x=base_df["Timestamp"],
        y=base_df["MA_30"],
        name="MA_30",
        line=dict(dash="dot")
    ))
    fig3.update_layout(template="plotly_dark", title="Close vs 30-Day Moving Average")
    st.plotly_chart(fig3, use_container_width=True)

    # 30-Day Rolling Volatility
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=base_df["Timestamp"], y=base_df["Volatility_30"], name="Volatility"))
    fig4.update_layout(template="plotly_dark", title="30-Day Rolling Volatility")
    st.plotly_chart(fig4, use_container_width=True)

    # Return Distribution
    fig5 = go.Figure()
    fig5.add_trace(go.Histogram(x=base_df["Return"].dropna(), nbinsx=50))
    fig5.update_layout(template="plotly_dark", title="Return Distribution")
    st.plotly_chart(fig5, use_container_width=True)

    # Correlation Heatmap
    st.subheader("📉 Correlation Heatmap")
    corr = base_df.select_dtypes(include=[np.number]).corr().round(2)
    fig_heat = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        text=corr.values,
        texttemplate="%{text}",
        textfont={"size": 12}
    ))
    fig_heat.update_layout(template="plotly_dark", title="Correlation Heatmap")
    st.plotly_chart(fig_heat, use_container_width=True)

    # RMSE Model Distribution
    st.subheader("🥧 RMSE Model Distribution")
    if "RMSE" in metrics_df.columns and "Model" in metrics_df.columns:
        metrics_sorted = metrics_df.sort_values(by="RMSE")
        fig_rmse = go.Figure(go.Pie(
            labels=metrics_sorted["Model"],
            values=metrics_sorted["RMSE"],
            hole=0.35
        ))
        fig_rmse.update_layout(template="plotly_dark", title="Model RMSE Contribution")
        st.plotly_chart(fig_rmse, use_container_width=True)
    else:
        st.warning("⚠ 'RMSE' or 'Model' column not found in model_metrics.csv")

    # Positive vs Negative Days
    pos = (base_df["Return"] > 0).sum()
    neg = (base_df["Return"] < 0).sum()
    fig_ret = go.Figure(go.Pie(
        labels=["Positive", "Negative"],
        values=[pos, neg],
        hole=0.3
    ))
    fig_ret.update_layout(template="plotly_dark", title="Positive vs Negative Days")
    st.plotly_chart(fig_ret, use_container_width=True)

# ===========================================================
# ===================== LIVE MARKET TAB ======================
# ===========================================================
with tabs[1]:
    st.subheader("📍 Real-Time Live Market Price")

    ticker = st.selectbox("Select Asset", ["BTC-USD", "ETH-USD", "RELIANCE.NS", "TCS.NS", "AAPL", "NVDA", "TSLA"])

    live_data = yf.download(ticker, period="1d", interval="1m")

    if live_data.empty:
        st.error("⚠ No live market data available")
    else:
        current_price = float(live_data["Close"].iloc[-1])
        previous_price = float(live_data["Close"].iloc[-2])
        delta = float(current_price - previous_price)

        st.metric(label=f"{ticker} Current Price", value=f"{current_price:.2f}", delta=f"{delta:.2f}")

        fig_live = go.Figure(go.Scatter(x=live_data.index, y=live_data["Close"], mode="lines+markers"))
        fig_live.update_layout(template="plotly_dark", title=f"{ticker} Live Market Chart (1m)")
        st.plotly_chart(fig_live, use_container_width=True)

        st.write("⏱ Last Updated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# ===========================================================
# ================= SENTIMENT TAB ============================
# ===========================================================
with tabs[2]:
    st.subheader("📰 Sentiment & News Influence")

    if "HEADLINE" not in news_df.columns:
        st.error("❌ 'HEADLINE' column not found in news .csv")
    else:
        news_df["Sentiment"] = news_df["HEADLINE"].apply(lambda x: TextBlob(str(x)).sentiment.polarity)

        def sent_label(x):
            if x > 0.1:
                return "Positive"
            elif x < -0.1:
                return "Negative"
            return "Neutral"

        news_df["Sentiment_Type"] = news_df["Sentiment"].apply(sent_label)

        st.dataframe(news_df, use_container_width=True)

        # Sentiment distribution
        fig_piece = go.Figure(go.Pie(
            labels=news_df["Sentiment_Type"].value_counts().index,
            values=news_df["Sentiment_Type"].value_counts().values,
            hole=0.35
        ))
        fig_piece.update_layout(template="plotly_dark", title="Sentiment Distribution")
        st.plotly_chart(fig_piece, use_container_width=True)

        # Sentiment over time
        sent_time = news_df.groupby("DATETIME")["Sentiment"].mean().reset_index()
        fig_time = go.Figure(go.Scatter(
            x=sent_time["DATETIME"],
            y=sent_time["Sentiment"],
            mode="lines+markers"
        ))
        fig_time.update_layout(template="plotly_dark", title="Sentiment Trend Over Time")
        st.plotly_chart(fig_time, use_container_width=True)

        # Sentiment vs Price Influence
        merged = pd.merge(base_df, sent_time, left_on="Timestamp", right_on="DATETIME", how="left")
        fig_rel = make_subplots(specs=[[{"secondary_y": True}]])
        fig_rel.add_trace(
            go.Scatter(x=merged["Timestamp"], y=merged["Sentiment"], name="Sentiment"),
            secondary_y=False
        )
        fig_rel.add_trace(
            go.Scatter(x=merged["Timestamp"], y=merged["Close"], name="Close Price"),
            secondary_y=True
        )
        fig_rel.update_layout(template="plotly_dark", title="Sentiment vs Price Influence")
        st.plotly_chart(fig_rel, use_container_width=True)

        # Trending tags / topics
        if "TAGS" in news_df.columns:
            tag_counts = news_df["TAGS"].astype(str).str.split(",").explode().value_counts().head(15)
            fig_tags = go.Figure(go.Bar(x=tag_counts.values, y=tag_counts.index, orientation="h"))
            fig_tags.update_layout(template="plotly_dark", title="Trending Topics / Tags")
            st.plotly_chart(fig_tags, use_container_width=True)
        else:
            st.warning("⚠ 'TAGS' column not found in news .csv")

# ===========================================================
# ===================== METRICS TAB ==========================
# ===========================================================
with tabs[3]:
    st.subheader("📋 Model Evaluation Metrics Table")
    st.dataframe(metrics_df, use_container_width=True)

# ===========================================================
# ===================== ABOUT TAB ============================
# ===========================================================
with tabs[4]:
    st.header("👥 Project Team Members")
    st.write("""
- Sameera H P
- Vaishnavi Deshmukh
- Siddardha Raj
- Rushikesh
""")

    st.header("📌 Project Overview")
    st.write("""
This project focuses on **Cryptocurrency & Stock Market Forecasting and Sentiment-driven Analytics**.
The dashboard integrates real-time price monitoring, predictive forecasting models, technical indicators,
and sentiment analysis based on financial news.
""")

    st.header("🔍 Key Components")
    st.write("""
- Forecasting using ARIMA, SARIMA, Prophet and LSTM models
- Real-time price visualization and candlestick charts
- Volatility, returns analysis, and correlation heatmap
- RMSE model comparison and evaluation
- Sentiment vs price relationship visualization
- Trending tags/topic extraction
- Power BI dashboard for additional comparison and interpretation
""")

    st.header("🧠 Technologies & Tools Used")
    st.write("""
- **Python** (Pandas, NumPy, TensorFlow, Statsmodels, Scikit-learn, TextBlob)
- **Forecasting Models:** ARIMA, SARIMA, Prophet, LSTM
- **Visualization Tools:** Streamlit, Plotly
- **Business Intelligence:** Power BI interactive dashboards
- **Live Market API:** Yahoo Finance
""")

    st.header("🏁 Outcome")
    st.write("""
The dashboard enhances decision-making through:
- Real-time asset tracking and forecasting
- Understanding how news sentiment influences market direction
- Supporting financial analysts and traders with data insights

Additionally, a **Power BI interactive dashboard** was created for visual storytelling,
enhancing interpretation and presentation of forecasting vs sentiment analytics.
""")
