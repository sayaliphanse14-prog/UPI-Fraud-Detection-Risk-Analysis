import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =============================
# Page Config
# =============================
st.set_page_config(
    page_title="UPI Fraud Detection Dashboard",
    page_icon="🚨",
    layout="wide"
)

# =============================
# Load Data
# =============================
@st.cache_data
def load_data():
    # Project root = .../UPI-Fraud-Detection-Risk-Analysis-main
    base_dir = Path(__file__).resolve().parent.parent
    csv_file = base_dir / "data" / "upi_fraud_detection_dataset.csv"

    if not csv_file.exists():
        st.error(f"Dataset not found: {csv_file}")
        st.stop()

    df = pd.read_csv(csv_file)

    required_columns = [
        "User_ID", "Transaction_ID", "Transaction_Amount_INR",
        "Transaction_Type", "City", "Device_Type", "Payment_Mode",
        "Transaction_Timestamp", "IP_Risk_Score", "Device_Risk_Score",
        "Location_Risk_Score", "Fraud_Score", "Fraudulent"
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing columns in dataset: {', '.join(missing_columns)}")
        st.stop()

    df["Transaction_Timestamp"] = pd.to_datetime(
        df["Transaction_Timestamp"], errors="coerce"
    )
    df["Transaction_Amount_INR"] = pd.to_numeric(
        df["Transaction_Amount_INR"], errors="coerce"
    )
    df["Fraud_Score"] = pd.to_numeric(df["Fraud_Score"], errors="coerce")

    df["Date"] = df["Transaction_Timestamp"].dt.date
    df["Hour"] = df["Transaction_Timestamp"].dt.hour

    # Support both 0/1 and Yes/No fraud values.
    fraud_values = df["Fraudulent"].astype(str).str.strip().str.lower()
    df["Fraudulent"] = fraud_values.map({
        "1": "Yes",
        "0": "No",
        "1.0": "Yes",
        "0.0": "No",
        "true": "Yes",
        "false": "No",
        "yes": "Yes",
        "no": "No"
    }).fillna("No")

    for column in ["City", "Transaction_Type", "Device_Type", "Payment_Mode"]:
        df[column] = df[column].fillna("Unknown")

    df = df.dropna(subset=["Transaction_Amount_INR", "Fraud_Score"])

    return df


df = load_data()

# =============================
# Sidebar Filters
# =============================
st.sidebar.title("🔍 Fraud Filters")

min_amount = int(df["Transaction_Amount_INR"].min())
max_amount = int(df["Transaction_Amount_INR"].max())

amount_range = st.sidebar.slider(
    "Transaction Amount (INR)",
    min_amount,
    max_amount,
    (min_amount, max_amount)
)

cities = st.sidebar.multiselect(
    "Select City",
    sorted(df["City"].unique()),
    default=sorted(df["City"].unique())
)

fraud_filter = st.sidebar.multiselect(
    "Fraud Status",
    ["Yes", "No"],
    default=["Yes", "No"]
)

score_min = float(df["Fraud_Score"].min())
score_max = float(df["Fraud_Score"].max())
score_default = min(max(0.0, score_min), score_max)

risk_threshold = st.sidebar.slider(
    "Minimum Fraud Score",
    score_min,
    score_max,
    score_default
)

# =============================
# Apply Filters
# =============================
filtered_df = df[
    (df["Transaction_Amount_INR"] >= amount_range[0]) &
    (df["Transaction_Amount_INR"] <= amount_range[1]) &
    (df["City"].isin(cities)) &
    (df["Fraudulent"].isin(fraud_filter)) &
    (df["Fraud_Score"] >= risk_threshold)
].copy()

# =============================
# Dashboard Title
# =============================
st.title("🚨 UPI Fraud Detection & Risk Intelligence Dashboard")
st.caption("Interactive analysis of UPI transactions, fraud patterns and risk scores")

# =============================
# KPI Section
# =============================
col1, col2, col3, col4, col5 = st.columns(5)

total_txn = len(filtered_df)
fraud_txn = (filtered_df["Fraudulent"] == "Yes").sum()
fraud_rate = round((fraud_txn / total_txn) * 100, 2) if total_txn else 0
avg_risk = round(filtered_df["Fraud_Score"].mean(), 2) if total_txn else 0
high_risk = (filtered_df["Fraud_Score"] >= 70).sum()

col1.metric("💳 Total Transactions", total_txn)
col2.metric("🚨 Fraud Transactions", int(fraud_txn))
col3.metric("📊 Fraud Rate (%)", f"{fraud_rate}%")
col4.metric("⚠️ Avg Risk Score", avg_risk)
col5.metric("🔥 High Risk Cases", int(high_risk))

st.markdown("---")

if filtered_df.empty:
    st.warning("No transactions match the selected filters. Please adjust the sidebar filters.")
    st.stop()

# =============================
# Fraud by City
# =============================
st.subheader("🌍 Fraud Risk by City")

city_risk = (
    filtered_df.groupby("City")
    .agg(
        Transactions=("Transaction_ID", "count"),
        Avg_Risk=("Fraud_Score", "mean")
    )
    .reset_index()
    .sort_values("Avg_Risk", ascending=False)
)

fig_city = px.bar(
    city_risk.head(10),
    x="Avg_Risk",
    y="City",
    orientation="h",
    color="Transactions",
    title="Top Risk Cities"
)
fig_city.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig_city, use_container_width=True)

# =============================
# Fraud Score Trend
# =============================
st.subheader("📈 Fraud Score Trend Over Time")

daily_risk = (
    filtered_df.dropna(subset=["Date"])
    .groupby("Date")
    .agg(Avg_Risk=("Fraud_Score", "mean"))
    .reset_index()
)

fig_trend = px.line(
    daily_risk,
    x="Date",
    y="Avg_Risk",
    markers=True,
    title="Daily Average Fraud Risk Score"
)
st.plotly_chart(fig_trend, use_container_width=True)

# =============================
# Transaction Type Distribution
# =============================
st.subheader("💼 Fraud by Transaction Type")

type_dist = (
    filtered_df.groupby("Transaction_Type")
    .size()
    .reset_index(name="Count")
)

fig_type = px.pie(
    type_dist,
    names="Transaction_Type",
    values="Count",
    hole=0.5,
    title="Transaction Type Distribution"
)
st.plotly_chart(fig_type, use_container_width=True)

# =============================
# Payment Mode Risk
# =============================
st.subheader("📲 Payment Mode Risk Analysis")

view_mode = st.radio(
    "Visualization Mode",
    ["Bar View", "Bubble View", "Trend View"],
    horizontal=True
)

risk_cutoff = st.slider(
    "High Risk Threshold",
    0.0,
    100.0,
    70.0,
    help="Transactions at or above this score are treated as High Risk"
)

fraud_only = st.checkbox("Show Only Fraudulent Transactions", False)

viz_df = filtered_df.copy()
if fraud_only:
    viz_df = viz_df[viz_df["Fraudulent"] == "Yes"]

if viz_df.empty:
    st.info("No transactions match the Payment Mode filters.")
else:
    viz_df["Risk_Level"] = viz_df["Fraud_Score"].apply(
        lambda x: "High Risk" if x >= risk_cutoff else "Low / Medium Risk"
    )

    if view_mode == "Bar View":
        pay_risk = (
            viz_df.groupby("Payment_Mode")
            .agg(
                Transactions=("Transaction_ID", "count"),
                Avg_Risk=("Fraud_Score", "mean"),
                High_Risk_Cases=("Risk_Level", lambda x: (x == "High Risk").sum())
            )
            .reset_index()
            .sort_values("Avg_Risk", ascending=False)
        )

        fig = px.bar(
            pay_risk,
            x="Payment_Mode",
            y="Avg_Risk",
            color="High_Risk_Cases",
            text="Transactions",
            title="Payment Mode Risk Profile"
        )

    elif view_mode == "Bubble View":
        bubble_data = (
            viz_df.groupby("Payment_Mode")
            .agg(
                Transactions=("Transaction_ID", "count"),
                Avg_Risk=("Fraud_Score", "mean")
            )
            .reset_index()
        )

        fig = px.scatter(
            bubble_data,
            x="Transactions",
            y="Avg_Risk",
            size="Transactions",
            color="Payment_Mode",
            title="Risk vs Volume (Bubble Analysis)",
            labels={
                "Transactions": "Transaction Volume",
                "Avg_Risk": "Average Risk Score"
            }
        )

    else:
        trend_data = (
            viz_df.dropna(subset=["Date"])
            .groupby(["Date", "Payment_Mode"])
            .agg(Avg_Risk=("Fraud_Score", "mean"))
            .reset_index()
        )

        fig = px.line(
            trend_data,
            x="Date",
            y="Avg_Risk",
            color="Payment_Mode",
            markers=True,
            title="Payment Mode Risk Trend Over Time"
        )

    fig.update_layout(
        transition_duration=700,
        hovermode="closest",
        margin=dict(l=20, r=20, t=60, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================
# Fraud Heatmap
# =============================
st.subheader("🌌 Fraud Command Center (India Map)")

heatmap_mode = st.radio(
    "Heatmap Mode",
    ["Transaction Volume", "Average Risk", "Fraud Only"],
    horizontal=True
)

heatmap_cutoff = st.slider(
    "High Risk Threshold for Map",
    0.0,
    100.0,
    70.0,
    help="Used in Fraud Only mode to detect high-risk activity"
)

map_df = filtered_df.copy()

if heatmap_mode == "Fraud Only":
    map_df = map_df[
        (map_df["Fraudulent"] == "Yes") &
        (map_df["Fraud_Score"] >= heatmap_cutoff)
    ]

# City coordinates covering the cities commonly used in the dataset.
city_coords = {
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "Lucknow": {"lat": 26.8467, "lon": 80.9462},
    "Surat": {"lat": 21.1702, "lon": 72.8311},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882},
    "Bhopal": {"lat": 23.2599, "lon": 77.4126},
    "Patna": {"lat": 25.5941, "lon": 85.1376},
    "Chandigarh": {"lat": 30.7333, "lon": 76.7794},
}

map_df["lat"] = map_df["City"].map(
    lambda x: city_coords.get(x, {}).get("lat")
)
map_df["lon"] = map_df["City"].map(
    lambda x: city_coords.get(x, {}).get("lon")
)
map_df = map_df.dropna(subset=["lat", "lon"])

if map_df.empty:
    st.info("No mapped cities are available for the current filters.")
else:
    if heatmap_mode == "Average Risk":
        map_data = (
            map_df.groupby(["City", "lat", "lon"])
            .agg(Value=("Fraud_Score", "mean"))
            .reset_index()
        )
        color_scale = "Turbo"
    else:
        map_data = (
            map_df.groupby(["City", "lat", "lon"])
            .size()
            .reset_index(name="Value")
        )
        color_scale = "Inferno"

    peak_city = map_data.loc[map_data["Value"].idxmax(), "City"]
    st.info(f"📍 Peak Activity City: **{peak_city}**")

    # Use scatter_geo instead of scatter_map to avoid external map-tile
    # dependencies. This renders the India map directly in Plotly.
    fig_map = px.scatter_geo(
        map_data,
        lat="lat",
        lon="lon",
        size="Value",
        color="Value",
        color_continuous_scale=color_scale,
        size_max=35,
        hover_name="City",
        hover_data={"lat": False, "lon": False, "Value": True},
        title=f"🔥 Fraud Activity Heatmap in India ({heatmap_mode})"
    )

    fig_map.update_geos(
        projection_type="mercator",
        center={"lat": 22.0, "lon": 79.0},
        lataxis_range=[6, 38],
        lonaxis_range=[68, 90],
        showcountries=True,
        showcoastlines=True,
        showland=True,
        landcolor="lightgray",
        countrycolor="white"
    )

    fig_map.update_layout(
        margin={"l": 0, "r": 0, "t": 50, "b": 0},
        height=600
    )

    st.plotly_chart(fig_map, use_container_width=True)

# =============================
# Data Table
# =============================
with st.expander("📄 View Filtered Transactions"):
    st.dataframe(filtered_df, use_container_width=True)

# =============================
# Footer
# =============================
st.markdown("---")
st.markdown(
    "✅ **Advanced Portfolio Project | Fraud Analytics, Risk Intelligence & ML-Ready Dashboard**"
)
