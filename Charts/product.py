import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

def metric_calculations(filtered_df):
    product_quantities = (
        filtered_df.groupby("Product Name")["Quantity"].sum().reset_index()
    )
    top_product_by_quantity = product_quantities.sort_values(
        by="Quantity", ascending=False
    ).head(1)
    top_product_name = top_product_by_quantity.iloc[0]["Product Name"]
    top_product_quantity = top_product_by_quantity.iloc[0]["Quantity"]
    
    top_category = filtered_df["Category"].value_counts().idxmax()
    total_products_sold = filtered_df["Product Name"].value_counts()
    total_products_sold_len = len(total_products_sold)

    return total_products_sold_len, top_product_name, top_product_quantity, top_category

def product_category(filtered_df):
    list_of_category = filtered_df["Category"].unique()
    list_of_sub_category = filtered_df["Sub-Category"].unique()
    category_col, subcategory_col = st.columns(2)
    category_counts = filtered_df["Category"].value_counts()
    fig_category = px.bar(
        category_counts, x=category_counts.index, y=category_counts.values
    )
    fig_category.update_layout(yaxis_title="Number of Transactions")
    
    subcategory_counts = filtered_df["Sub-Category"].value_counts()
    fig_subcategory = px.bar(
        subcategory_counts, x=subcategory_counts.index, y=subcategory_counts.values
    )
    fig_subcategory.update_layout(yaxis_title="Number of Transactions")

    return fig_category, fig_subcategory

def segmentation(filtered_df):
    fig_categories_segment = px.pie(filtered_df, names="Segment", hole=0.3)
    fig_categories_region = px.pie(filtered_df, names="Category", hole=0.3)
    fig_subcategories_region = px.pie(filtered_df, names="Sub-Category", hole=0.3)

    return fig_categories_segment, fig_categories_region, fig_subcategories_region

def top_bottom_10_products(filtered_df):
    product = st.columns(1)
    product_quantities = (
        filtered_df.groupby("Product Name")["Quantity"].sum().reset_index()
    )
    top_10_products_by_quantity = (
        product_quantities.sort_values(by="Quantity", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    top_10_products_by_quantity.index += 1

    columns_to_display_product = ["Product Name", "Quantity"]

    product_quantities = (
            filtered_df.groupby("Product Name")["Quantity"].sum().reset_index()
        )

    bottom_10_products_by_quantity = (
        product_quantities.sort_values(by="Quantity", ascending=True)
        .head(10)
        .reset_index(drop=True)
    )
    bottom_10_products_by_quantity.index += 1

    return top_10_products_by_quantity, bottom_10_products_by_quantity, columns_to_display_product


def display_all_product (filtered_df):
    total_products_sold_len, top_product_name, top_product_quantity, top_category = metric_calculations(filtered_df)
    fig_category, fig_subcategory = product_category(filtered_df)
    fig_categories_segment, fig_categories_region, fig_subcategories_region = segmentation(filtered_df)
    top_10_products_by_quantity, bottom_10_products_by_quantity, columns_to_display_product = top_bottom_10_products(filtered_df)

    st.write("## Metric")
    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Total Product Item Sold", total_products_sold_len)
    metric2.metric(
        "Top Product Sold by Quantity", f"{top_product_name} ({top_product_quantity})"
    )
    metric3.metric("Top Category Sold", top_category)

    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")

    category_col, subcategory_col = st.columns(2)
    with category_col:
        st.subheader("Transactions by Category")
        st.plotly_chart(fig_category)

    with subcategory_col:
        st.subheader("Transactions by Sub-Category")
        st.plotly_chart(fig_subcategory)

    st.markdown("---")

    region1, region2, region3 = st.columns(3)

    with region1:
        st.subheader("Product Segment")
        st.plotly_chart(fig_categories_segment)
    with region2:
        st.subheader("Product Categories")
        st.plotly_chart(fig_categories_region)
    with region3:
        st.subheader("Product Sub-Categories")
        st.plotly_chart(fig_subcategories_region)

    st.write("## Top 10 Products by Quantity Sold")
    st.table(top_10_products_by_quantity[columns_to_display_product])
    st.write("## Bottom 10 Products by Quantity Sold")
    st.table(bottom_10_products_by_quantity[columns_to_display_product])