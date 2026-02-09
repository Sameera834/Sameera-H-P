import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("Fraud Detection Dataset.csv")

# ---------------------------------
# Create numeric fraud column for EDA
# ---------------------------------
df['Fraud_Flag'] = df['isFraud'].apply(
    lambda x: 1 if str(x).lower() == 'fraud' else 0
)

# ---------------------------------
# 1. Fraud vs Non-Fraud Count
# ---------------------------------
plt.figure()
df['isFraud'].value_counts().plot(kind='bar')
plt.title("Fraud vs Non-Fraud Transactions")
plt.xlabel("Transaction Status")
plt.ylabel("Count")
plt.show()

# ---------------------------------
# 2. Transaction Amount Distribution
# ---------------------------------
plt.figure()
plt.hist(df['amount'], bins=30)
plt.title("Transaction Amount Distribution")
plt.xlabel("Amount")
plt.ylabel("Frequency")
plt.show()

# ---------------------------------
# 3. Fraud Rate by Transaction Type
# ---------------------------------
plt.figure()
df.groupby('type')['Fraud_Flag'].mean().plot(kind='bar')
plt.title("Fraud Rate by Transaction Type")
plt.xlabel("Transaction Type")
plt.ylabel("Fraud Rate")
plt.show()

# ---------------------------------
# 4. Fraud vs Unusual Login
# ---------------------------------
plt.figure()
df.groupby('unusuallogin')['Fraud_Flag'].mean().plot(kind='bar')
plt.title("Fraud Rate vs Unusual Login")
plt.xlabel("Unusual Login (0 = No, 1 = Yes)")
plt.ylabel("Fraud Rate")
plt.show()

# ---------------------------------
# 5. Fraud by Time of Day
# ---------------------------------
plt.figure()
df.groupby('Time of day')['Fraud_Flag'].mean().plot(kind='bar')
plt.title("Fraud Rate by Time of Day")
plt.xlabel("Time of Day")
plt.ylabel("Fraud Rate")
plt.show()
