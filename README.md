UPI Fraud Detection & Risk Intelligence Dashboard
📌 Overview

This project is an end-to-end data analytics and fraud detection system designed to identify high-risk UPI transactions using Python, SQL, Streamlit, and Power BI. It simulates a real-world banking fraud monitoring solution by integrating ETL pipelines, advanced SQL queries, and interactive dashboards for operational and executive-level analysis.

🏗️ Architecture
CSV Dataset  
   ↓  
Python ETL (Pandas + SQLAlchemy)  
   ↓  
MySQL Database (Normalized Tables)  
   ↓  
Advanced SQL Queries  
   ↓  
Streamlit Dashboard (Live Risk Monitoring)  
   ↓  
Power BI Dashboard (Strategic Analytics & DAX)

⚙️ Tech Stack

Python (Pandas, Streamlit, Plotly, SQLAlchemy)

MySQL

SQL (Advanced Analytics)

Power BI (DAX, Visual Analytics)

GitHub

📂 Project Structure
upi-fraud-detection/
│
├── data/
│   └── upi_fraud_detection_dataset.csv
│
├── sql/
│   └── fraud_analysis_queries.sql
│
├── python/
│   ├── etl_to_mysql.py
│   └── streamlit_dashboard.py
│
├── powerbi/
│   └── upi_fraud_dashboard.pbix
│
├── screenshots/
│   ├── streamlit_dashboard.png
│   └── powerbi_dashboard.png
│
└── README.md

🔍 Key Features

Fraud Risk Scoring Engine

City-Based Fraud Heatmap (India Map)

Payment Mode Risk Profiling

Real-Time KPI Monitoring

Advanced DAX Measures

High-Risk Transaction Flagging

📊 Dashboards
🖥️ Streamlit (Operational View)

Live Filters: City, Risk Score, Amount, Fraud Status

KPIs: Fraud Rate, Avg Risk, High-Risk Cases

Risk Heatmap

Trend & Bubble Charts

📈 Power BI (Executive View)

Fraud % (DAX)

Risk Index

City Risk Rankings

Time-Based Fraud Trends

Risk Segmentation

🛠️ Setup Instructions
1️⃣ Install Dependencies
pip install pandas streamlit plotly sqlalchemy pymysql

2️⃣ Run ETL Pipeline
python etl_to_mysql.py

3️⃣ Launch Dashboard
streamlit run streamlit_dashboard.py

4️⃣ Open Power BI

Open upi_fraud_dashboard.pbix

Refresh MySQL data source

📌 Business Use Case

Designed for:

Banks

FinTech Companies

Fraud & Risk Teams

Data Analysts

Compliance Teams

🚀 Future Scope

ML Fraud Prediction Model

Cloud Deployment

Live Payment API Integration

Automated Alerts

👩‍💻 Author

Hemalatha G
Entry-Level Data Analyst
Skilled in Python | SQL | Power BI | Data Analytics | Fraud Intelligence