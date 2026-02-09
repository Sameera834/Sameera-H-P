# ============================================================
# Financial Fraud Detection – FINAL VERSION (Sklearn Safe)
# ============================================================

import os
import numpy as np
import pandas as pd
import joblib
import sklearn
from packaging import version

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import OneClassSVM

import xgboost as xgb
import lightgbm as lgb

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

# ============================================================
# CONFIG
# ============================================================
DATA_PATH = "Fraud_Detection_Preprocessed.csv"
TARGET_COL = "isFraud"
RANDOM_STATE = 42

# ============================================================
# HELPER: SKLEARN VERSION SAFE ENCODER
# ============================================================
def get_onehot_encoder():
    if version.parse(sklearn.__version__) >= version.parse("1.2"):
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    else:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)

# ============================================================
# MAIN
# ============================================================
def main():
    print("🚀 Script started")

    # ----------------------------
    # Load data
    # ----------------------------
    df = pd.read_csv(DATA_PATH)
    print(f"📊 Dataset loaded with shape {df.shape}")
    print("📌 Columns:", list(df.columns))

    # ----------------------------
    # Split features / target
    # ----------------------------
    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    # ----------------------------
    # Encode target labels
    # ----------------------------
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)
    joblib.dump(label_encoder, "target_encoder.pkl")
    print("🎯 Target encoded:", dict(enumerate(label_encoder.classes_)))

    # ----------------------------
    # Feature preprocessing
    # ----------------------------
    num_cols = X.select_dtypes(include=["int64", "float64"]).columns
    cat_cols = X.select_dtypes(include=["object"]).columns

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", get_onehot_encoder())
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_pipeline, num_cols),
        ("cat", categorical_pipeline, cat_cols)
    ])

    # ----------------------------
    # Train / test split
    # ----------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y
    )

    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.transform(X_test)

    joblib.dump(preprocessor, "feature_preprocessor.pkl")

    # ----------------------------
    # Safety checks
    # ----------------------------
    assert not np.isnan(X_train).any(), "❌ NaN found in X_train"
    assert not np.isnan(X_test).any(), "❌ NaN found in X_test"
    print("✅ No NaN values after preprocessing")

    # ========================================================
    # SUPERVISED MODELS
    # ========================================================
    print("🤖 Training Logistic Regression")
    lr = LogisticRegression(max_iter=2000, n_jobs=-1)
    lr.fit(X_train, y_train)
    joblib.dump(lr, "logistic_regression.pkl")

    print("🌲 Training Decision Tree")
    dt = DecisionTreeClassifier(random_state=RANDOM_STATE)
    dt.fit(X_train, y_train)
    joblib.dump(dt, "decision_tree.pkl")

    print("🌳 Training Random Forest")
    rf = RandomForestClassifier(
        n_estimators=200,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    joblib.dump(rf, "random_forest.pkl")

    print("⚡ Training XGBoost")
    xgb_model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=len(label_encoder.classes_),
        eval_metric="mlogloss",
        n_estimators=200,
        random_state=RANDOM_STATE
    )
    xgb_model.fit(X_train, y_train)
    joblib.dump(xgb_model, "xgboost.pkl")

    print("💡 Training LightGBM")
    lgb_model = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=len(label_encoder.classes_),
        n_estimators=200,
        random_state=RANDOM_STATE
    )
    lgb_model.fit(X_train, y_train)
    joblib.dump(lgb_model, "lightgbm.pkl")

    # ========================================================
    # UNSUPERVISED MODELS
    # ========================================================
    print("🕵️ Training Isolation Forest")
    iso = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=RANDOM_STATE
    )
    iso.fit(X_train)
    joblib.dump(iso, "isolation_forest.pkl")

    print("🕵️ Training One-Class SVM")
    ocsvm = OneClassSVM(kernel="rbf", nu=0.05)
    ocsvm.fit(X_train)
    joblib.dump(ocsvm, "one_class_svm.pkl")

    # ========================================================
    # AUTOENCODER (H5)
    # ========================================================
    print("🧠 Training Autoencoder")

    input_dim = X_train.shape[1]
    inp = Input(shape=(input_dim,))
    enc = Dense(64, activation="relu")(inp)
    enc = Dense(32, activation="relu")(enc)
    dec = Dense(64, activation="relu")(enc)
    out = Dense(input_dim, activation="linear")(dec)

    autoencoder = Model(inp, out)
    autoencoder.compile(optimizer="adam", loss="mse")

    autoencoder.fit(
        X_train,
        X_train,
        epochs=20,
        batch_size=32,
        validation_split=0.1,
        verbose=1
    )

    autoencoder.save("autoencoder_anomaly_model.h5")
    print("✅ Autoencoder saved")

    print("\n🎉 ALL MODELS TRAINED SUCCESSFULLY")

# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    main()
