import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from datetime import datetime
import time

st.set_page_config(layout="wide", page_title="Fraud Detection Dashboard")

# =====================================================
# SESSION STATE FOR REALTIME
# =====================================================
if "realtime" not in st.session_state:
    st.session_state.realtime = False

# =====================================================
# LOAD DATA
# =====================================================
df = pd.read_csv("Fraud_Detection_Preprocessed.csv")

feature_cols = [
"step","type","branch","amount","oldbalanceOrg","newbalanceOrig",
"oldbalanceDest","newbalanceDest","unusuallogin","isFlaggedFraud",
"Acct type","Time of day","DayOfWeek","DayOfWeek(new)",
"Transaction_Day","Transaction_Month","Transaction_Year",
"balance_change_org","balance_change_dest","high_amount_flag"
]

target = "isFraud"

# =====================================================
# FIX TARGET LABELS
# =====================================================
def fix_target(v):
    v = str(v).lower()
    if v in ["fraud","1","true","yes"]:
        return 1
    return 0

df[target] = df[target].apply(fix_target)

X = df[feature_cols]
y = df[target].astype(int)

# =====================================================
# LOAD MODELS
# =====================================================
def load_model(path):
    try:
        return joblib.load(path)
    except:
        return None

models = {
    "LightGBM": load_model("lightgbm.pkl"),
    "XGBoost": load_model("xgboost.pkl"),
    "Random Forest": load_model("random_forest.pkl"),
    "Decision Tree": load_model("decision_tree.pkl"),
    "Logistic Regression": load_model("logistic_regression.pkl"),
    "Isolation Forest": load_model("isolation_forest.pkl"),
    "OneClass SVM": load_model("one_class_svm.pkl"),
}

models = {k:v for k,v in models.items() if v is not None}

# =====================================================
# NORMALIZE PREDICTIONS
# =====================================================
def normalize_preds(preds):
    preds = np.array(preds)
    preds = np.where(preds=="Fraud",1,preds)
    preds = np.where(preds=="Safe",0,preds)
    preds = np.where(preds==-1,1,preds)
    preds = preds.astype(int)
    preds = np.where(preds>1,1,preds)
    return preds

# =====================================================
# CALCULATE METRICS FOR ALL MODELS
# =====================================================
metrics = []
pred_store = {}

for name, model in models.items():
    raw = model.predict(X)
    preds = normalize_preds(raw)
    pred_store[name] = preds

    acc = accuracy_score(y, preds)
    prec = precision_score(y, preds, zero_division=0)
    rec = recall_score(y, preds, zero_division=0)
    f1 = f1_score(y, preds, zero_division=0)

    metrics.append([name, acc, prec, rec, f1])

metrics_df = pd.DataFrame(metrics, columns=["Model","Accuracy","Precision","Recall","F1"])
metrics_df = metrics_df.sort_values("Accuracy", ascending=False)

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("Model Control")

selected_model_name = st.sidebar.selectbox("Select Model", metrics_df["Model"])
model = models[selected_model_name]

if st.sidebar.button("▶ Start Real-Time"):
    st.session_state.realtime = True

if st.sidebar.button("⏹ Stop Real-Time"):
    st.session_state.realtime = False

df["Prediction"] = pred_store[selected_model_name]

# =====================================================
# TITLE
# =====================================================
st.title("🚨 Financial Fraud Detection Dashboard")

# =====================================================
# MODEL METRICS
# =====================================================
st.header("📊 Model Performance")
st.dataframe(metrics_df)

st.plotly_chart(px.bar(metrics_df, x="Model", y="Accuracy", color="Model"), use_container_width=True)

# =====================================================
# METRIC CARDS
# =====================================================
col1,col2,col3,col4 = st.columns(4)
col1.metric("Transactions", len(df))
col2.metric("Fraud %", f"{df['Prediction'].mean()*100:.2f}%")
col3.metric("Accuracy", f"{metrics_df[metrics_df.Model==selected_model_name]['Accuracy'].values[0]*100:.2f}%")
col4.metric("Fraud Count", int(df["Prediction"].sum()))

# =====================================================
# CONFUSION MATRIX
# =====================================================
st.header("Confusion Matrix")
cm = confusion_matrix(y, df["Prediction"])
st.plotly_chart(px.imshow(cm, text_auto=True), use_container_width=True)

# =====================================================
# ALL VISUALIZATIONS (40+)
# =====================================================
st.header("📊 All Visualizations")

st.plotly_chart(px.pie(df, names="Prediction"))
st.plotly_chart(px.histogram(df, x="amount", color="Prediction"))
st.plotly_chart(px.box(df, x="Prediction", y="amount"))
st.plotly_chart(px.violin(df, y="amount", color="Prediction"))

st.plotly_chart(px.scatter(df.sample(4000), x="oldbalanceOrg", y="amount", color="Prediction"))
st.plotly_chart(px.scatter(df.sample(4000), x="newbalanceOrig", y="amount", color="Prediction"))
st.plotly_chart(px.scatter(df.sample(4000), x="oldbalanceDest", y="amount", color="Prediction"))

st.plotly_chart(px.histogram(df, x="Time of day", color="Prediction"))
st.plotly_chart(px.histogram(df, x="DayOfWeek", color="Prediction"))
st.plotly_chart(px.histogram(df, x="branch", color="Prediction"))
st.plotly_chart(px.histogram(df, x="type", color="Prediction"))
st.plotly_chart(px.histogram(df, x="high_amount_flag", color="Prediction"))
st.plotly_chart(px.histogram(df, x="unusuallogin", color="Prediction"))
st.plotly_chart(px.histogram(df, x="isFlaggedFraud", color="Prediction"))

corr = df[feature_cols].corr()
st.plotly_chart(px.imshow(corr), use_container_width=True)

st.plotly_chart(px.scatter_3d(df.sample(3000),
                              x="amount", y="oldbalanceOrg", z="newbalanceOrig",
                              color="Prediction"))

st.plotly_chart(px.scatter_3d(df.sample(3000),
                              x="amount", y="oldbalanceDest", z="newbalanceDest",
                              color="Prediction"))

st.plotly_chart(px.treemap(df, path=["type","Prediction"], values="amount"))
st.plotly_chart(px.sunburst(df, path=["branch","Prediction"], values="amount"))

df_sorted = df.sort_values("step")
st.plotly_chart(px.line(df_sorted.head(5000), x="step", y="amount"))
st.plotly_chart(px.area(df_sorted.head(5000), x="step", y="amount", color="Prediction"))

st.plotly_chart(px.density_contour(df, x="amount", y="oldbalanceOrg"))
st.plotly_chart(px.ecdf(df, x="amount", color="Prediction"))

st.plotly_chart(px.parallel_coordinates(df.sample(2000),
                                        dimensions=feature_cols[:6],
                                        color="Prediction"))

st.plotly_chart(px.scatter_matrix(df.sample(2000),
                                  dimensions=feature_cols[:5],
                                  color="Prediction"))

# =====================================================
# REALTIME ALERT
# =====================================================
st.header("⚡ Real-Time Fraud Alerts")

alert_placeholder = st.empty()
table_placeholder = st.empty()

if st.session_state.realtime:

    sample = df.sample(1)
    raw = model.predict(sample[feature_cols])[0]
    pred = normalize_preds([raw])[0]

    if pred == 1:
        alert_placeholder.error(f"🚨 FRAUD DETECTED at {datetime.now()}")
    else:
        alert_placeholder.success("Safe Transaction")

    table_placeholder.dataframe(sample[feature_cols])

    time.sleep(1)
    st.rerun()
