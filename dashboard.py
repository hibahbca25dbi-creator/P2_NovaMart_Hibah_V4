import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="NovaMart Dashboard",page_icon="📊",layout="wide")

st.title("📊 NovaMart Dashboard - Hibah P S")
st.markdown("### Customer Segment & Order Behaviour Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("data/novamart_clean.csv")
    return df

df = load_data()

st.sidebar.header("Filters")

segment = st.sidebar.multiselect(
    "Select Segment",
    options=df["segment"].unique(),
    default=df["segment"].unique()
)

region = st.sidebar.multiselect(
    "Select Region",
    options=df["region"].unique(),
    default=df["region"].unique()
)
filtered_df = df[
    (df["segment"].isin(segment)) &
    (df["region"].isin(region))
]

total_sales = filtered_df["sales"].sum()
customer_count = filtered_df["customer_id"].nunique()
average_order = filtered_df["sales"].mean()

col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Customer Count", customer_count)
col3.metric("Average Order Value", f"${average_order:,.2f}")

st.subheader("Sales by Segment")

sales_segment = filtered_df.groupby("segment")["sales"].sum().reset_index()

fig = px.bar(
    sales_segment,
    x="segment",
    y="sales",
    color="segment",
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Segment Share of Sales")

fig = px.pie(
    sales_segment,
    names="segment",
    values="sales",
    hole=0.5
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Monthly Orders per Segment")

monthly_orders = (
    filtered_df
    .groupby(["order_month", "segment"])
    .size()
    .reset_index(name="Orders")
)

month_order = [
    "January", "February", "March",
    "April", "May", "June",
    "July", "August", "September",
    "October", "November", "December"
]

monthly_orders["order_month"] = pd.Categorical(
    monthly_orders["order_month"],
    categories=month_order,
    ordered=True
)

monthly_orders = monthly_orders.sort_values("order_month")

fig = px.line(
    monthly_orders,
    x="order_month",
    y="Orders",
    color="segment",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Top 10 Customers by Sales")

top_customers = (
    filtered_df
    .groupby("customer_name")["sales"]
    .sum()
    .reset_index()
    .sort_values("sales", ascending=False)
    .head(10)
)

st.dataframe(top_customers, use_container_width=True)

customer_sales = (
    filtered_df
    .groupby("customer_name")["sales"]
    .sum()
)

threshold = np.percentile(customer_sales, 90)

top_spenders = customer_sales[customer_sales >= threshold]

st.success(
    f"⭐ Top 10% customer spending threshold: ${threshold:,.2f} | "
    f"Top Customers: {len(top_spenders)}"
)

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name="filtered_data.csv",
    mime="text/csv"
)