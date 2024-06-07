import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from sales import display_metrics_and_plots
from ship import display_all_shippings
from product import display_all_product
from customer import display_customer

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path, encoding="ISO-8859-1")

file_path = "Superstore.csv"
df = load_data(file_path)

def apply_custom_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

apply_custom_css()

st.sidebar.image("superstore_logo.png", width=300)

st.sidebar.markdown('<div style="margin-top: 50px;"></div>', unsafe_allow_html=True)

shipping, sales, product, customer = st.tabs(
    ["Shipping", "Sales", "Product", "Customer"]
)


df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")

df["Year"] = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.month

latest_year = df["Year"].max()
latest_month = df[df["Year"] == latest_year]["Month"].max()
latest_date = df["Order Date"].max().date()

default_year = latest_year if latest_year else None
default_month = latest_month if latest_month else None
default_date_range = [latest_date - pd.Timedelta(days=30), latest_date]

year_filter = st.sidebar.selectbox(
    "Filter by Year",
    ["All"] + sorted(df["Year"].unique()),
    index=sorted(df["Year"].unique()).index(default_year) + 1 if default_year else 0
)

if year_filter == "All":
    filtered_year = df
    month_filter_options = ["All"] + sorted(filtered_year["Month"].unique())
    month_filter = st.sidebar.selectbox(
        "Filter by Month",
        month_filter_options,
    )
else:
    filtered_year = df[df["Year"] == year_filter]
    filtered_year["Month"] = filtered_year["Order Date"].dt.month

    month_filter = st.sidebar.selectbox(
        "Filter by Month",
        ["All"] + sorted(df[df["Year"] == year_filter]["Month"].unique()),
        index=sorted(df[df["Year"] == year_filter]["Month"].unique()).index(default_month) + 1 if default_month is not None else 0
    )


if month_filter == "All":
    filtered_data = filtered_year
else:
    filtered_data = filtered_year[filtered_year["Month"] == month_filter]


min_date = filtered_data["Order Date"].min()
max_date = filtered_data["Order Date"].max()
latest_date = max_date

if year_filter == default_year and month_filter == default_month:
    date_range = st.sidebar.date_input(
        "Filter by Date Range",
        [latest_date, latest_date],
        min_value=min_date,
        max_value=max_date,
    )
    
elif year_filter == "All" and month_filter == "All":
    date_range = st.sidebar.date_input(
        "Filter by Date Range",
        [min_date, latest_date],
        min_value=min_date,
        max_value=max_date,
    )
else:
    date_range = st.sidebar.date_input(
        "Filter by Date Range",
        [min_date, latest_date],
        min_value=min_date,
        max_value=max_date,
    )

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_data = filtered_data[
        (filtered_data["Order Date"] >= pd.to_datetime(start_date))
        & (filtered_data["Order Date"] <= pd.to_datetime(end_date))
    ]

list_of_regions = ["All"] + list(filtered_data["Region"].unique())

selected_region = st.sidebar.selectbox("Select Region", list_of_regions)
if selected_region == "All":
    filtered_region = filtered_data
else:
    filtered_region = filtered_data[filtered_data["Region"] == selected_region]

list_of_states = ["All"] + list(filtered_region["State"].unique())
selected_state = st.sidebar.selectbox("Select State", list_of_states)

if selected_state == "All":
    filtered_state = filtered_region
else:
    filtered_state = filtered_region[filtered_region["State"] == selected_state]

list_of_cities = ["All"] + list(filtered_state["City"].unique())
selected_city = st.sidebar.selectbox("Select City", list_of_cities)

if selected_city == "All":
    filtered_df = filtered_state
else:
    filtered_df = filtered_state[filtered_state["City"] == selected_city]

st.sidebar.markdown('<div style="margin-top: 200px;"></div>', unsafe_allow_html=True)
st.sidebar.markdown(
    "<h3 style='text-align: center;'>Maleakhi Ezekiel</h3>", unsafe_allow_html=True
)

with shipping:
    display_all_shippings(filtered_df,df)
with sales:
    display_metrics_and_plots(filtered_df,df)
with product:
    display_all_product(filtered_df)
with customer:
    display_customer(filtered_df,df)
