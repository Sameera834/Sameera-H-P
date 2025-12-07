import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.graphics.tsaplots import plot_acf
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, roc_curve, auc
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification

# === 1. Load the dataset ===
file_path = "D:\\Amdox intenship\\Data analytics project\\bitcoin_analysis\\bitcoin_analysis\\btcusd_1-min_data.csv"
df = pd.read_csv(file_path)

# === 2. Parse and clean ===
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s', errors='coerce')
df = df.set_index('Timestamp').sort_index()
df = df.ffill()

# === 3. Resample to daily data ===
cols = df.columns
agg_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}
if 'Volume_(BTC)' in cols:
    agg_dict['Volume_(BTC)'] = 'sum'
if 'Volume_(Currency)' in cols:
    agg_dict['Volume_(Currency)'] = 'sum'
if 'Volume_BTC' in cols:
    agg_dict['Volume_BTC'] = 'sum'
if 'Volume' in cols:
    agg_dict['Volume'] = 'sum'

daily = df.resample('D').agg(agg_dict)

# === 4. Feature Engineering ===
daily['Return'] = daily['Close'].pct_change()
daily['LogReturn'] = np.log(daily['Close'] / daily['Close'].shift(1))
daily['MA_30'] = daily['Close'].rolling(30).mean()
daily['Volatility_30'] = daily['Close'].rolling(30).std()

# === 5. Save cleaned data ===
daily.to_csv("bitcoin_preprocessed_daily.csv")
print("✅ Saved: bitcoin_preprocessed_daily.csv")

# === 6. Basic Info ===
print("\nBasic Info:")
print(daily.info())
print("\nMissing Values:\n", daily.isna().sum())
print("\nSummary Statistics:\n", daily.describe())

# === 7. Visual EDA ===

# 1️⃣ Close Price Trend
plt.figure(figsize=(12,6))
daily['Close'].plot()
plt.title("Bitcoin Daily Close Price")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.show()

# 2️⃣ Rolling Average
plt.figure(figsize=(12,6))
plt.plot(daily['Close'], label='Close')
plt.plot(daily['MA_30'], label='30-day MA', color='orange')
plt.title("Close Price with 30-Day Moving Average")
plt.legend()
plt.show()

# 3️⃣ Volatility
plt.figure(figsize=(12,6))
daily['Volatility_30'].plot(color='red')
plt.title("30-Day Rolling Volatility")
plt.xlabel("Date")
plt.ylabel("Volatility")
plt.show()

# 4️⃣ Log Return Distribution
plt.figure(figsize=(10,5))
sns.histplot(daily['LogReturn'].dropna(), bins=100, kde=True)
plt.title("Distribution of Log Returns")
plt.xlabel("Log Return")
plt.ylabel("Frequency")
plt.show()

#Generate the synthetic data'
X, y=make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)
X_train, X_test, y_train, y_test=train_test_split(X, y, test_size=0.3, random_state=42)

#Logistic regression model
model=LogisticRegression()
model.fit(X_train, y_train)
y_prob=model.predict_proba(X_test)[:, 1] # probabilities of the positive class

#ROC Curve
fpr, tpr, thresholds=roc_curve(y_test, y_prob)
roc_auc=auc(fpr, tpr)

#Plot the ROC Curve
plt.figure()
plt.plot(fpr, tpr, color='blue', label=f'ROC Curve (AUC={roc_auc:.2f})')
plt.plot([0,1],[0,1], color='gray', linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend(loc="lower right")
plt.show()

# 5️⃣ Correlation Heatmap
plt.figure(figsize=(8,6))
sns.heatmap(daily.select_dtypes(float).corr(), annot=True, cmap='coolwarm')
plt.title("Correlation Heatmap")
plt.show()

# 6️⃣ Autocorrelation
plot_acf(daily['LogReturn'].dropna(), lags=30)
plt.title("Autocorrelation of Log Returns")
plt.show()

# === 🧩 Additional Relationship Visuals ===

# 7️⃣ Risk vs Return (Volatility vs Return)
plt.figure(figsize=(8,6))
sns.scatterplot(x='Volatility_30', y='Return', data=daily)
plt.title("Risk vs Return (Volatility vs Return)")
plt.xlabel("30-Day Volatility")
plt.ylabel("Daily Return")
plt.show()

# 8️⃣ Rolling Correlation (Close vs Volume)
vol_col = [c for c in daily.columns if 'Volume' in c][0]  # auto-detect volume column
daily['RollingCorr_Close_Vol'] = daily['Close'].rolling(30).corr(daily[vol_col])
daily['RollingCorr_Close_Vol'].plot(figsize=(12,6))
plt.title("30-Day Rolling Correlation (Close vs Volume)")
plt.xlabel("Date")
plt.ylabel("Correlation")
plt.show()

# 9️⃣ Cumulative Return
daily['CumulativeReturn'] = (1 + daily['Return']).cumprod()
plt.figure(figsize=(12,6))
plt.plot(daily['CumulativeReturn'], color='green')
plt.title("Cumulative Return Over Time")
plt.xlabel("Date")
plt.ylabel("Cumulative Return (Growth)")
plt.show()

print("\n✅ EDA is completed!")
