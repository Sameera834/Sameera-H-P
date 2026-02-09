import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Load data
df = pd.read_csv("Fraud Detection Dataset.csv")

# -------------------------------
# 1. Handle Missing Values
# -------------------------------
num_cols = df.select_dtypes(include=['float64', 'int64']).columns
cat_cols = df.select_dtypes(include=['object']).columns

for col in num_cols:
    df[col].fillna(df[col].median(), inplace=True)

for col in cat_cols:
    df[col].fillna(df[col].mode()[0], inplace=True)

# -------------------------------
# 2. Drop Irrelevant Columns
# -------------------------------
drop_cols = ['nameOrig', 'nameDest', 'Column1', 'isFraud - Copy']
df.drop(columns=drop_cols, inplace=True, errors='ignore')

# -------------------------------
# 3. Date Feature Extraction
# -------------------------------
df['Date of transaction'] = pd.to_datetime(df['Date of transaction'])

df['Transaction_Day'] = df['Date of transaction'].dt.day
df['Transaction_Month'] = df['Date of transaction'].dt.month
df['Transaction_Year'] = df['Date of transaction'].dt.year

df.drop(columns=['Date of transaction'], inplace=True)

# -------------------------------
# 4. Feature Engineering
# -------------------------------
df['balance_change_org'] = df['oldbalanceOrg'] - df['newbalanceOrig']
df['balance_change_dest'] = df['newbalanceDest'] - df['oldbalanceDest']

high_amount_threshold = df['amount'].quantile(0.90)
df['high_amount_flag'] = np.where(df['amount'] > high_amount_threshold, 1, 0)

# -------------------------------
# 5. Encode Categorical Features
# -------------------------------
le = LabelEncoder()
encode_cols = ['type', 'branch', 'Acct type', 'Time of day', 'DayOfWeek(new)']

for col in encode_cols:
    df[col] = le.fit_transform(df[col])

# -------------------------------
# 6. Feature Scaling
# -------------------------------
scaler = StandardScaler()
scale_cols = ['amount', 'oldbalanceOrg', 'newbalanceOrig',
              'oldbalanceDest', 'newbalanceDest']

df[scale_cols] = scaler.fit_transform(df[scale_cols])

# -------------------------------
# Final Dataset
# -------------------------------
print(df.head())
print("Shape:", df.shape)

# Save the preprocessed data
df.to_csv("Fraud_Detection_Preprocessed.csv", index=False)
print("\nPreprocessed data saved as 'Fraud_Detection_Preprocessed.csv'")
