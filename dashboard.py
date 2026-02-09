# =========================================
# STREAMLIT DASHBOARD: CHATBOT + ANALYTICS
# (BACKWARD-COMPATIBLE VERSION)
# =========================================

import os
import pickle
import numpy as np
import pandas as pd
import datetime
import spacy
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# -----------------------------------------
# PATH SAFETY
# -----------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

LOG_FILE = "chat_logs.csv"
CONFIDENCE_THRESHOLD = 0.4

# -----------------------------------------
# LOAD MODELS (CACHED)
# -----------------------------------------
@st.cache_resource
def load_resources():
    intent_model = load_model("intent_model.h5")
    sentiment_model = load_model("sentiment_model.h5")
    emotion_model = load_model("emotion_model.h5")

    tokenizer = pickle.load(open("tokenizer.pkl", "rb"))
    encoders = pickle.load(open("encoders.pkl", "rb"))

    nlp = spacy.load("en_core_web_sm")
    return intent_model, sentiment_model, emotion_model, tokenizer, encoders, nlp

intent_model, sentiment_model, emotion_model, tokenizer, encoders, nlp = load_resources()

# -----------------------------------------
# RESPONSE BANK
# -----------------------------------------
RESPONSES = {
    "greeting": ["Hello! How can I help you today?"],
    "goodbye": ["Goodbye! Have a great day 😊"],
    "support": ["Sure, please explain your issue."],
    "complaint": ["That sounds frustrating. I’ll try to assist."],
    "thanks": ["You're welcome! 😊"],
    "capabilities": ["I can help with support, complaints, order queries, and general assistance."],
    "query": ["I can help with order-related questions. Please share details."],
    "fallback": ["I’m not fully sure I understood that. Could you rephrase?"]
}

# -----------------------------------------
# KEYWORD INTENT OVERRIDE
# -----------------------------------------
def keyword_intent(text):
    text = text.lower()
    if any(w in text for w in ["hi", "hello", "hey", "good morning", "good evening"]):
        return "greeting"
    if any(w in text for w in ["bye", "goodbye", "exit"]):
        return "goodbye"
    if any(w in text for w in ["help", "support", "assist"]):
        return "support"
    if any(w in text for w in ["crash", "bad", "issue", "problem", "not working"]):
        return "complaint"
    if any(w in text for w in ["task", "capabilities", "features", "do you do"]):
        return "capabilities"
    if any(w in text for w in ["order", "track", "delivery", "status"]):
        return "query"
    if any(w in text for w in ["thank", "thanks"]):
        return "thanks"
    return None

# -----------------------------------------
# CHATBOT FUNCTION
# -----------------------------------------
def chatbot_response(user_input):
    seq = pad_sequences(
        tokenizer.texts_to_sequences([user_input]),
        maxlen=30
    )

    # Intent detection
    intent = keyword_intent(user_input)
    if intent is None:
        probs = intent_model.predict(seq, verbose=0)[0]
        confidence = float(np.max(probs))
        pred_intent = encoders["intent"].inverse_transform([np.argmax(probs)])[0]
        intent = pred_intent if confidence >= CONFIDENCE_THRESHOLD else "fallback"
    else:
        confidence = 1.0

    # Sentiment & emotion
    sentiment = encoders["sentiment"].inverse_transform(
        [np.argmax(sentiment_model.predict(seq, verbose=0))]
    )[0]

    emotion = encoders["emotion"].inverse_transform(
        [np.argmax(emotion_model.predict(seq, verbose=0))]
    )[0]

    response = np.random.choice(RESPONSES.get(intent, RESPONSES["fallback"]))

    if sentiment == "negative":
        response = "I’m sorry you’re feeling this way. " + response
    if emotion == "angry":
        response = "I understand your frustration. " + response

    # Log chat
    log = {
        "timestamp": datetime.datetime.now(),
        "text": user_input,
        "intent": intent,
        "sentiment": sentiment,
        "emotion": emotion,
        "confidence": confidence
    }

    pd.DataFrame([log]).to_csv(
        LOG_FILE,
        mode="a",
        header=not os.path.exists(LOG_FILE),
        index=False
    )

    return response

# -----------------------------------------
# STREAMLIT UI
# -----------------------------------------
st.set_page_config("Dynamic AI Chatbot Dashboard", layout="wide")
st.title("🤖 Dynamic AI Chatbot Dashboard")

page = st.sidebar.radio("Navigate", ["💬 Chatbot", "📊 Analytics Dashboard"])

# =========================================
# PAGE 1: CHATBOT
# =========================================
if page == "💬 Chatbot":
    st.subheader("Live AI Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        reply = chatbot_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)

# =========================================
# PAGE 2: ANALYTICS DASHBOARD
# =========================================
else:
    st.subheader("Smart Analytics Dashboard")

    if not os.path.exists(LOG_FILE):
        st.warning("No chat data available yet.")
        st.stop()

    df = pd.read_csv(LOG_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # -------- KPIs --------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Chats", len(df))
    c2.metric("Unique Intents", df["intent"].nunique())
    c3.metric("Negative %", round((df["sentiment"] == "negative").mean() * 100, 2))

    if "confidence" in df.columns:
        avg_conf = round(df["confidence"].mean(), 2)
    else:
        avg_conf = "N/A"
    c4.metric("Avg Confidence", avg_conf)

    # -------- VISUALS --------
    st.plotly_chart(px.bar(df, x="intent", title="Intent Distribution"),
                    use_container_width=True)

    st.plotly_chart(px.pie(df, names="sentiment", title="Sentiment Distribution"),
                    use_container_width=True)

    st.plotly_chart(px.pie(df, names="emotion", title="Emotion Distribution"),
                    use_container_width=True)

    if "confidence" in df.columns:
        st.plotly_chart(
            px.line(df, x="timestamp", y="confidence", title="Confidence Over Time"),
            use_container_width=True
        )

    heat = df.pivot_table(index="intent", columns="sentiment",
                          aggfunc="size", fill_value=0)

    st.plotly_chart(
        go.Figure(go.Heatmap(
            z=heat.values,
            x=heat.columns,
            y=heat.index
        )),
        use_container_width=True
    )

    st.plotly_chart(
        px.histogram(df, x="intent", color="sentiment",
                     title="Intent vs Sentiment"),
        use_container_width=True
    )

    st.subheader("Conversation Logs")
    st.dataframe(df, use_container_width=True)
