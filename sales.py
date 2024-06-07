import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

def calculate_metrics(filtered_df):
    total_sales = round(filtered_df["Sales"].sum())
    formatted_total_sales = "{:,.0f}".format(total_sales)
    total_profit = round(filtered_df["Profit"].sum())
    formatted_total_profit = "{:,.0f}".format(total_profit)

    yearly_sales = filtered_df.groupby("Year")["Sales"].sum().reset_index()
    yearly_profit = filtered_df.groupby("Year")["Profit"].sum().reset_index()
    ratio_profit = pd.DataFrame()
    ratio_profit["Year"] = yearly_profit["Year"]
    ratio_profit["Rasio"] = (yearly_profit["Profit"] / yearly_sales["Sales"]) * 100
    total_ratio_profit = round(ratio_profit["Rasio"].mean())

    return {
        "total_sales": formatted_total_sales,
        "total_profit": formatted_total_profit,
        "total_ratio_profit": total_ratio_profit,
        "yearly_sales": yearly_sales,
        "yearly_profit": yearly_profit,
        "ratio_profit": ratio_profit,
    }

def plot_sales_profit(df):
    sales_profit_by_year = (
        df.groupby("Year")
        .agg({"Sales": "sum", "Profit": "sum"})
        .reset_index()
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sales_profit_by_year["Year"],
            y=sales_profit_by_year["Sales"],
            mode="lines+markers",
            name="Sales",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sales_profit_by_year["Year"],
            y=sales_profit_by_year["Profit"],
            mode="lines+markers",
            name="Profit",
        )
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Amount",
        width=1200,
        height=600,
        legend=dict(x=0, y=1, traceorder="normal"),
    )
    fig.update_xaxes(tickmode="linear")

    sales_profit_by_month = (
        df.groupby("Month")
        .agg({"Sales": "sum", "Profit": "sum"})
        .reset_index()
    )

    # Convert Year-Month to a string for Plotly
    sales_profit_by_month["Month"] = sales_profit_by_month["Month"].astype(str)
    fig_month = go.Figure()
    fig_month.add_trace(
        go.Scatter(
            x=sales_profit_by_month["Month"],
            y=sales_profit_by_month["Sales"],
            mode="lines+markers",
            name="Sales",
        )
    )
    fig_month.add_trace(
        go.Scatter(
            x=sales_profit_by_month["Month"],
            y=sales_profit_by_month["Profit"],
            mode="lines+markers",
            name="Profit",
        )
    )
    fig_month.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount",
        width=1200,
        height=600,
        legend=dict(x=0, y=1, traceorder="normal"),
    )
    fig_month.update_xaxes(tickmode="linear")

    return fig, fig_month

def plot_loss_discount(filtered_df):
    negative_profit_data = filtered_df[filtered_df["Profit"] < 0]
    negative_profit_by_year = (
        negative_profit_data.groupby("Year")["Profit"].sum().reset_index()
    )
    negative_profit_by_year["Profit"] = negative_profit_by_year["Profit"].astype(
        int
    )
    total_negative_profit = negative_profit_by_year["Profit"].sum()
    fig = px.bar(
        negative_profit_by_year,
        x="Year",
        y="Profit",
        labels={"Year": "Year", "Profit": "Total Negative Profit"},
    )
    fig.update_layout(width=800)
    fig.update_xaxes(tickmode="linear")

    st.subheader(f"Loss")
    loss = total_negative_profit * (-1)
    format_loss = "{:,.0f}".format(loss)

    discounted_transactions = filtered_df[filtered_df["Discount"] > 0]
    discounted_transactions_by_year = (
        discounted_transactions.groupby("Year")
        .size()
        .reset_index(name="Total Discounted Transactions")
    )
    average_discount = discounted_transactions["Discount"].mean()

    quantity_by_year = filtered_df.groupby("Year")["Quantity"].sum().reset_index()
    
    fig_discount = px.bar(
        discounted_transactions_by_year,
        x="Year",
        y="Total Discounted Transactions",
        labels={"Year": "Year", "Total Discounted Transactions": "Total Discounted Transactions"},
    )
    fig_discount.update_layout(width=800)

    fig_discount.update_xaxes(tickmode="linear")
    fig_quantity = px.bar(
        quantity_by_year,
        x="Year",
        y="Quantity",
        labels={"Year": "Year", "Quantity": "Total Quantity Sold"},
    )

    fig_height = 600
    fig.update_layout(height=fig_height)
    fig_discount.update_layout(height=fig_height)
    fig_quantity.update_layout(height=fig_height)
    fig_quantity.update_xaxes(tickmode="linear")
    

    return fig, format_loss, fig_discount, fig_quantity, average_discount

def display_top_10(filtered_df):
    loss_products = filtered_df[filtered_df["Profit"] < 0]
    top_loss_products = (
        loss_products.groupby("Product Name")
        .agg({"Sales": "sum", "Quantity": "sum", "Discount": "mean", "Profit": "sum"})
        .reset_index()
        .sort_values(by="Profit", ascending=True)
        .head(10)
        .reset_index(drop=True)
    )

    profitable_products = filtered_df[filtered_df["Profit"] > 0]
    top_profitable_products = (
        profitable_products.groupby("Product Name")
        .agg({"Sales": "sum", "Quantity": "sum", "Discount": "mean", "Profit": "sum"})
        .reset_index()
        .sort_values(by="Profit", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )

    top_10_product_highest_discount = (
        filtered_df.groupby("Product Name")
        .agg({"Sales": "sum", "Quantity": "sum", "Discount": "mean", "Profit": "sum"})
        .reset_index()
        .sort_values(by="Discount", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    top_loss_products.index += 1
    top_profitable_products.index += 1
    top_10_product_highest_discount.index += 1

    return top_loss_products, top_profitable_products, top_10_product_highest_discount

def display_metrics_and_plots(filtered_df,df):
    metrics = calculate_metrics(filtered_df)
    fig_sales_profit, fig_sales_profit_month = plot_sales_profit(df)
    fig, format_loss, fig_discount, fig_quantity, average_discount  = plot_loss_discount(filtered_df)
    top_loss_products, top_profitable_products, top_10_product_highest_discount = display_top_10(filtered_df)

    st.subheader("Metric")
    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Total Sales", f"${metrics['total_sales']}")
    metric2.metric("Total Profit", f"${metrics['total_profit']}")
    metric3.metric("Profit Ratio", f"{metrics['total_ratio_profit']}%")

    view = st.radio(
        "Select View", 
        ("Yearly", "Monthly"),
        key="sales_profit_view"
    )
    
    if view == "Yearly":
        st.subheader("Sales and Profit by Year")
        st.plotly_chart(fig_sales_profit, use_container_width=True)
    else:
        st.subheader("Sales and Profit by Month")
        st.plotly_chart(fig_sales_profit_month, use_container_width=True)

    loss1, loss2 = st.columns(2)
    with loss1:
        st.subheader(f"Loss")
        st.write("Total Loss: -$", format_loss)
        st.plotly_chart(fig)
    with loss2:
        st.subheader(f"Total Discounted Transactions")
        format_average_percent = average_discount * 100
        format_average = "{:.1f}".format(format_average_percent)
        st.write("Average discount: ", format_average, "%")
        st.plotly_chart(fig_discount)
    st.subheader("Total Quantity Sold by Year")
    st.plotly_chart(fig_quantity, use_container_width=True)

    st.subheader("Top 10 Products with Highest Loss:")
    st.table(top_loss_products)

    st.subheader("Top 10 Products with Highest Profit:")
    st.table(top_profitable_products)

    st.subheader("Top 10 Products with Highest Discount:")
    st.table(top_10_product_highest_discount)
