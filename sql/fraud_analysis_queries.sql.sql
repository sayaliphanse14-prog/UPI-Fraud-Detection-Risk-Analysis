USE upi_fraud_detection_db;

-- =====================================
-- UPI Fraud Detection Analysis Queries
-- Dataset: upi_fraud_detection_db
-- Description: Professional SQL queries for fraud detection analysis
-- Suitable for GitHub, resume, and Power BI dashboards
-- =====================================

-- README Section
/*
This SQL script contains advanced queries for analyzing UPI fraud detection dataset.
It includes:
1. Overall fraud metrics
2. High-risk transactions and users
3. Device type, city, and payment mode risk analysis
4. Time-based fraud patterns
5. Top fraud contributors
6. Dashboard-ready queries

Usage:
- Connect to MySQL and select the database.
- Run individual queries as needed.
- For Power BI, connect to MySQL and use these queries as source views.

Note:
- The `Fraudulent` column is handled for numeric (0/1), string ('Yes'/'No'), or boolean (TRUE/FALSE) formats.
- Table `transactions` uses backticks because `transaction` is a reserved keyword in MySQL.
*/

-- 1 >>>> Overall Fraud Metrics (Fraud Overview & Metrics)
SELECT
    COUNT(t.Transaction_ID) AS Total_Transactions,
    SUM(r.Fraudulent) AS Fraudulent_Transactions,
    ROUND(SUM(r.Fraudulent)/COUNT(t.Transaction_ID)*100, 2) AS Fraud_Percentage
FROM transactions t
JOIN risk_fraudulent r ON t.Transaction_ID = r.Transaction_ID;

-- 2 >>>> High-Risk Transactions
SELECT
    t.Transaction_ID,
    t.User_ID,
    t.Transaction_Amount_INR,
    r.Fraud_Score,
    r.IP_Risk_Score,
    r.Device_Risk_Score,
    r.Location_Risk_Score,
    r.Fraudulent
FROM transactions t
JOIN risk_fraudulent r ON t.Transaction_ID = r.Transaction_ID
ORDER BY r.Fraud_Score DESC
LIMIT 10;

-- 3 >>>> High-Risk Users
SELECT
    t.User_ID,
    COUNT(t.Transaction_ID) AS Total_Transactions,
    SUM(CASE 
            WHEN r.Fraudulent = 1 THEN 1
            WHEN r.Fraudulent = 'Yes' THEN 1
            WHEN r.Fraudulent = TRUE THEN 1
            ELSE 0
        END) AS Fraudulent_Transactions,
    ROUND(
        SUM(CASE 
                WHEN r.Fraudulent = 1 THEN 1
                WHEN r.Fraudulent = 'Yes' THEN 1
                WHEN r.Fraudulent = TRUE THEN 1
                ELSE 0
            END) / COUNT(t.Transaction_ID) * 100, 2
    ) AS Fraud_Percentage
FROM `transactions` t
JOIN `risk_fraudulent` r ON t.Transaction_ID = r.Transaction_ID
GROUP BY t.User_ID
HAVING Fraudulent_Transactions > 0
ORDER BY Fraud_Percentage DESC, Fraudulent_Transactions DESC
LIMIT 20;

-- 4 >>>> Device Type Risk Analysis
SELECT
    t.Device_Type,
    COUNT(t.Transaction_ID) AS Total_Transactions,
    SUM(r.Fraudulent) AS Fraudulent_Transactions,
    ROUND(SUM(r.Fraudulent)/COUNT(t.Transaction_ID)*100, 2) AS Fraud_Percentage,
    AVG(r.Device_Risk_Score) AS Avg_Device_Risk_Score
FROM transactions t
JOIN risk_fraudulent r ON t.Transaction_ID = r.Transaction_ID
GROUP BY t.Device_Type
ORDER BY Fraud_Percentage DESC;

-- 5 >>>> City-Wise Fraud Analysis
SELECT
    t.City,
    COUNT(t.Transaction_ID) AS Total_Transactions,
    SUM(r.Fraudulent) AS Fraudulent_Transactions,
    ROUND(SUM(r.Fraudulent)/COUNT(t.Transaction_ID)*100, 2) AS Fraud_Percentage,
    AVG(r.Location_Risk_Score) AS Avg_Location_Risk
FROM transactions t
JOIN risk_fraudulent r ON t.Transaction_ID = r.Transaction_ID
GROUP BY t.City
ORDER BY Fraud_Percentage DESC;

-- 6 >>>> Payment Mode Risk Analysis
SELECT
    t.Payment_Mode,
    COUNT(t.Transaction_ID) AS Total_Transactions,
    SUM(r.Fraudulent) AS Fraudulent_Transactions,
    ROUND(SUM(r.Fraudulent)/COUNT(t.Transaction_ID)*100, 2) AS Fraud_Percentage,
    AVG(r.Fraud_Score) AS Avg_Fraud_Score
FROM transactions t
JOIN risk_fraudulent r ON t.Transaction_ID = r.Transaction_ID
GROUP BY t.Payment_Mode
ORDER BY Fraud_Percentage DESC;

-- 7 >>>> Time-Based Fraud Patterns
SELECT
    HOUR(t.Transaction_Timestamp) AS Hour_of_Day,
    COUNT(t.Transaction_ID) AS Total_Transactions,
    SUM(r.Fraudulent) AS Fraudulent_Transactions,
    ROUND(SUM(r.Fraudulent)/COUNT(t.Transaction_ID)*100, 2) AS Fraud_Percentage
FROM transactions t
JOIN risk_fraudulent r ON t.Transaction_ID = r.Transaction_ID
GROUP BY HOUR(t.Transaction_Timestamp)
ORDER BY Hour_of_Day;

-- 8 >>>> Top Fraud Contributors
SELECT
    t.User_ID,
    SUM(r.Fraud_Score) AS Total_Fraud_Score,
    SUM(r.Fraudulent) AS Fraudulent_Transactions
FROM transactions t
JOIN risk_fraudulent r ON t.Transaction_ID = r.Transaction_ID
GROUP BY t.User_ID
ORDER BY Total_Fraud_Score DESC
LIMIT 5;

-- 9 >>>> Dashboard-Ready Query: Fraud Overview by Payment Mode & Device Type
SELECT
    t.Payment_Mode,
    t.Device_Type,
    COUNT(t.Transaction_ID) AS Total_Transactions,
    SUM(r.Fraudulent) AS Fraudulent_Transactions,
    ROUND(SUM(r.Fraudulent)/COUNT(t.Transaction_ID)*100, 2) AS Fraud_Percentage,
    AVG(r.Fraud_Score) AS Avg_Fraud_Score
FROM transactions t
JOIN risk_fraudulent r ON t.Transaction_ID = r.Transaction_ID
GROUP BY t.Payment_Mode, t.Device_Type
ORDER BY Fraud_Percentage DESC;
