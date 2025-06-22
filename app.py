import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from email_parser import fetch_transactions 

st.set_page_config(page_title="DBS Transaction Dashboard", layout="wide")
st.title("DBS iBanking Transaction Dashboard")

cutoff_input = st.sidebar.date_input(
    "Cutoff Date (show transactions from this date onward)",
    value=datetime(2025, 1, 1),
    min_value=datetime(2022, 1, 1),
    max_value=datetime.today()
)

cutoff_date = datetime.combine(cutoff_input, datetime.min.time()).replace(tzinfo=timezone.utc)

with st.spinner("Fetching transactions..."):
    df = fetch_transactions(cutoff_date=cutoff_date)

if df.empty:
    st.warning("No transactions found after the selected cutoff date.")
    st.stop()

st.subheader("Transaction Data")
st.dataframe(df.sort_values(by="datetime", ascending=False), use_container_width=True)

total_spent = df["amount"].sum()
num_txns = len(df)
avg_txn = df["amount"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Spent", f"SGD {total_spent:,.2f}")
col2.metric("Transactions", num_txns)
col3.metric("Average per Transaction", f"SGD {avg_txn:,.2f}")

df["date"] = df["datetime"].dt.date
daily_df = df.groupby("date")["amount"].sum().reset_index()

st.subheader("Daily Spending")
st.bar_chart(data=daily_df, x="date", y="amount", use_container_width=True)



# Top recipients
st.subheader("Top Recipients")
top_recipients = df["recipient"].value_counts().head(10)
st.bar_chart(top_recipients)

st.subheader("Download Data")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download as CSV", csv, "dbs_transactions.csv", "text/csv")
