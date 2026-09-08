import pandas as pd
from sqlalchemy import create_engine

# -------------------------------
# Step 1: Load your CSV
# -------------------------------
csv_file =  r"C:\Users\saksh\OneDrive\Documents\UPI-Fraud-Detection-Risk-Analysis-main\data\upi_fraud_detection_dataset.csv"
df = pd.read_csv(csv_file)



print(df.columns.tolist())

# -------------------------------
# Step 2: Prepare the tables
# -------------------------------

# Users table (unique users)
users_df = df[['User_ID']].drop_duplicates()

# Transactions table
transactions_df = df[['Transaction_ID', 'User_ID', 'Transaction_Amount_INR', 'Transaction_Type',
                      'City', 'Device_Type', 'Payment_Mode', 'Transaction_Timestamp']]

# Risk/Fraud table
risk_df = df[['Transaction_ID', 'IP_Risk_Score', 'Device_Risk_Score',
              'Location_Risk_Score', 'Fraud_Score', 'Fraudulent']]

# -------------------------------
# Step 3: Connect to MySQL Database
# -------------------------------
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://upi_user:UpiProject%40123@localhost:3306/upi_fraud_detection_db"
)


# -------------------------------
# Step 4: Insert tables into MySQL
# -------------------------------
users_df.to_sql('users', con=engine, if_exists='replace', index=False)
transactions_df.to_sql('transactions', con=engine, if_exists='replace', index=False)
risk_df.to_sql('risk_fraudulent', con=engine, if_exists='replace', index=False)



print("✅ CSV has been successfully split and uploaded into MySQL tables!")
