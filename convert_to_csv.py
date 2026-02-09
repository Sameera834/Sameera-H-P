import pandas as pd
import os

# Get the Excel file path
excel_file = os.path.join(os.path.dirname(__file__), 'Fraud Detection Dataset.xlsx')

# Read the Excel file
print(f"Reading {excel_file}...")
df = pd.read_excel(excel_file)

# Create CSV file path
csv_file = excel_file.replace('.xlsx', '.csv')

# Save as CSV
df.to_csv(csv_file, index=False)
print(f"Successfully converted to {csv_file}")
print(f"File contains {len(df)} rows and {len(df.columns)} columns")
