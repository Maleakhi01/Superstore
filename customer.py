import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

def metric_calculations(filtered_df):
    customer_quantity = (
        filtered_df.groupby("Customer Name")["Quantity"].sum().reset_index()
    )
    top_customer_by_quantity = customer_quantity.sort_values(
        by="Quantity", ascending=False
    ).head(1)
    top_customer_name = top_customer_by_quantity.iloc[0]["Customer Name"]
    top_customer_quantity = top_customer_by_quantity.iloc[0]["Quantity"]

    total_customer_sold = filtered_df["Customer Name"].value_counts()
    total_customer_sold_len = len(total_customer_sold)

    customer_profit = filtered_df.groupby("Customer Name")["Profit"].sum().reset_index()
    top_customer_by_profit = customer_profit.sort_values(
        by="Profit", ascending=False
    ).head(1)
    top_customer_name_profit = top_customer_by_profit.iloc[0]["Customer Name"]
    top_customer_profit = top_customer_by_profit.iloc[0]["Profit"]
    top_customer_profit_format = "{:,.0f}".format(top_customer_profit)

    total_customer_sold = filtered_df["Customer Name"].value_counts()
    total_customer_sold_len = len(total_customer_sold)
    return total_customer_sold_len, top_customer_name, top_customer_quantity, top_customer_name_profit, top_customer_profit_format

def customer_reach(filtered_df):
    customer_counts_by_year = (
        filtered_df.groupby("Year")["Customer Name"].nunique().reset_index()
    )
    customer_counts_by_month = (
        filtered_df.groupby("Month")["Customer Name"].nunique().reset_index()
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=customer_counts_by_year["Year"],
            y=customer_counts_by_year["Customer Name"],
            mode="lines+markers",
            name="Unique Customers",
        )
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Customers",
        width=1200,
        height=600,
        legend=dict(x=0, y=1, traceorder="normal"),
        xaxis=dict(tickmode="linear")
    )

    fig_month = go.Figure()

    fig_month.add_trace(
        go.Scatter(
            x=customer_counts_by_month["Month"],
            y=customer_counts_by_month["Customer Name"],
            mode="lines+markers",
            name="Unique Customers",
        )
    )
    fig_month.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Customers",
        width=1200,
        height=600,
        legend=dict(x=0, y=1, traceorder="normal"),
        xaxis=dict(tickmode="linear")
    )
    return fig, fig_month

def top_10_customer(filtered_df):
    top_customers_quantity = (
        filtered_df.groupby(["Customer Name"])
        .agg({"Quantity": "sum", "Product Name": lambda x: ", ".join(x)})
        .nlargest(10, "Quantity")
        .reset_index()
    )

    top_customers_profit = (
        filtered_df.groupby(["Customer Name"])
        .agg({"Profit": "sum", "Product Name": lambda x: ", ".join(x)})
        .nlargest(10, "Profit")
        .reset_index()
    )

    top_customers_quantity.index += 1
    top_customers_profit.index += 1

    top_customers_quantity = top_customers_quantity[
        ["Customer Name", "Product Name", "Quantity"]
    ]
    top_customers_profit = top_customers_profit[
        ["Customer Name", "Product Name", "Profit"]
    ]

    return top_customers_profit, top_customers_quantity
def display_customer(filtered_df,df):
    total_customer_sold_len, top_customer_name, top_customer_quantity, top_customer_name_profit, top_customer_profit_format = metric_calculations(filtered_df)
    fig, fig_month = customer_reach(df)
    top_customers_profit, top_customers_quantity = top_10_customer(filtered_df)
    
    st.write("## Metric")
    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Total Customer Reach", total_customer_sold_len)
    metric2.metric(
        "Top Customer by Quantity", f"{top_customer_name} ({top_customer_quantity})"
    )
    metric3.metric(
        "Top Customer by Profit",
        f"{top_customer_name_profit} $({top_customer_profit_format})",
    )

    view = st.radio(
        "Select View", 
        ("Yearly", "Monthly"),
        key="customer_view"
    )
    if view == "Yearly":
        st.subheader("Number of Customers Reached Each Year")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.subheader("Sales and Profit by Month")
        st.plotly_chart(fig_month, use_container_width=True)

    st.subheader("Top 10 Customers with Highest Quantity Sold")
    st.table(top_customers_quantity)

    st.subheader("Top 10 Customers with Highest Profit")
    st.table(top_customers_profit)

