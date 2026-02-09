# =========================================
# DYNAMIC AI CHATBOT - FINAL STABLE ENGINE
# =========================================

import os
import pickle
import numpy as np
import pandas as pd
import datetime
import spacy
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# -------- PATH SAFETY --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# -------- LOAD MODELS --------
intent_model = load_model("intent_model.h5")
sentiment_model = load_model("sentiment_model.h5")
emotion_model = load_model("emotion_model.h5")

tokenizer = pickle.load(open("tokenizer.pkl","rb"))
encoders = pickle.load(open("encoders.pkl","rb"))

nlp = spacy.load("en_core_web_sm")

CONFIDENCE_THRESHOLD = 0.4   # LOWERED (IMPORTANT)

# -------- RESPONSE BANK --------
RESPONSES = {
    "greeting": [
        "Hello! How can I help you today?",
        "Hi there! What can I do for you?"
    ],
    "goodbye": [
        "Goodbye! Have a great day 😊"
    ],
    "support": [
        "Sure, please explain your issue.",
        "I’m here to help. Tell me more."
    ],
    "complaint": [
        "I’m sorry for the inconvenience. Let me help you.",
        "That sounds frustrating. I’ll try to assist."
    ],
    "thanks": [
        "You're welcome! 😊"
    ],
    "capabilities": [
        "I can help with support issues, complaints, greetings, order queries, and general assistance."
    ],
    "query": [
        "I can help with order-related questions. Please share more details."
    ],
    "fallback": [
        "I’m not fully sure I understood that. Could you please rephrase?"
    ]
}

# -------- KEYWORD OVERRIDES (CRITICAL) --------
def keyword_intent(text):
    text = text.lower()

    if any(w in text for w in ["hi", "hello", "hey", "good morning", "good evening"]):
        return "greeting"
    if any(w in text for w in ["bye", "goodbye", "exit", "quit"]):
        return "goodbye"
    if any(w in text for w in ["help", "support", "assist"]):
        return "support"
    if any(w in text for w in ["bad", "crash", "not working", "problem", "issue"]):
        return "complaint"
    if any(w in text for w in ["task", "do you do", "capabilities", "features"]):
        return "capabilities"
    if any(w in text for w in ["order", "track", "delivery", "status"]):
        return "query"
    if any(w in text for w in ["thanks", "thank you"]):
        return "thanks"

    return None

# -------- CHATBOT FUNCTION --------
def chatbot_response(user_input):
    seq = pad_sequences(
        tokenizer.texts_to_sequences([user_input]),
        maxlen=30
    )

    # ----- KEYWORD FIRST -----
    intent = keyword_intent(user_input)

    # ----- ML SECOND -----
    if intent is None:
        probs = intent_model.predict(seq, verbose=0)[0]
        confidence = np.max(probs)
        predicted_intent = encoders["intent"].inverse_transform(
            [np.argmax(probs)]
        )[0]

        if confidence >= CONFIDENCE_THRESHOLD:
            intent = predicted_intent
        else:
            intent = "fallback"

    # ----- SENTIMENT & EMOTION -----
    sentiment = encoders["sentiment"].inverse_transform(
        [np.argmax(sentiment_model.predict(seq, verbose=0))]
    )[0]

    emotion = encoders["emotion"].inverse_transform(
        [np.argmax(emotion_model.predict(seq, verbose=0))]
    )[0]

    # ----- RESPONSE -----
    response = np.random.choice(RESPONSES.get(intent, RESPONSES["fallback"]))

    if sentiment == "negative":
        response = "I’m sorry you’re feeling this way. " + response

    if emotion == "angry":
        response = "I understand your frustration. " + response

    # ----- LOGGING -----
    log = {
        "timestamp": datetime.datetime.now(),
        "text": user_input,
        "intent": intent,
        "sentiment": sentiment,
        "emotion": emotion
    }

    pd.DataFrame([log]).to_csv(
        "chat_logs.csv",
        mode="a",
        header=not os.path.exists("chat_logs.csv"),
        index=False
    )

    return response

# -------- TERMINAL CHAT --------
if __name__ == "__main__":
    print("\n🤖 AI Chatbot is running (type 'exit' to stop)\n")

    while True:
        text = input("You: ")
        if text.lower() in ["exit", "quit"]:
            print("Bot: Goodbye! 👋")
            break

        print("Bot:", chatbot_response(text))
