import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from charts.sales import display_metrics_and_plots
from charts.ship import display_all_shippings
from charts.product import display_all_product
from charts.customer import display_customer

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
latest_date = df["Order Date"].max()
first_date_latest_month = pd.Timestamp(latest_year, latest_month, 1)
last_date_latest_month = first_date_latest_month + pd.offsets.MonthEnd(1)

month_names = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}
# Reverse dictionary to map month names back to numbers
month_numbers = {v: k for k, v in month_names.items()}


year_filter = st.sidebar.selectbox(
    "Filter by Year",
    ["All"] + sorted(df["Year"].unique()),
    index=sorted(df["Year"].unique()).index(latest_year) + 1 if latest_year else 0
)

if year_filter == "All":
    filtered_year = df
    available_months = sorted(filtered_year["Month"].unique())
    month_filter_options = ["All"] + [month_names[m] for m in available_months]
    if latest_month in available_months:
        month_filter_index = available_months.index(latest_month) + 1
    else:
        month_filter_index = 0
    month_filter = st.sidebar.selectbox(
        "Filter by Month",
        month_filter_options,
        index=month_filter_index
    )

else:
    filtered_year = df[df["Year"] == year_filter]
    available_months = sorted(filtered_year["Month"].unique())
    month_filter_options = ["All"] + [month_names[m] for m in available_months]
    if latest_month in available_months:
        month_filter_index = available_months.index(latest_month) + 1
    else:
        month_filter_index = 0
    
    month_filter = st.sidebar.selectbox(
        "Filter by Month",
        month_filter_options,
        index=month_filter_index
    )

if month_filter != "All":
    selected_month_number = month_numbers[month_filter]
else:
    selected_month_number = None

if selected_month_number is not None:
    filtered_data = filtered_year[filtered_year["Month"] == selected_month_number]
else:
    filtered_data = filtered_year

min_date = filtered_data["Order Date"].min()
max_date = filtered_data["Order Date"].max()
first_date_latest_month = pd.Timestamp(latest_year, latest_month, 1)
latest_date = max_date
default_date_range = [first_date_latest_month, last_date_latest_month]

if year_filter == latest_year and month_filter == latest_month:
    date_range = st.sidebar.date_input(
        "Filter by Date Range",
        default_date_range,
        min_value=first_date_latest_month,
        max_value=last_date_latest_month,
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
else:
    start_date = end_date = date_range[0]
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
    display_all_shippings(filtered_df,df, filtered_year)
with sales:
    display_metrics_and_plots(filtered_df,df, filtered_year)
with product:
    display_all_product(filtered_df)
with customer:
    display_customer(filtered_df,df, filtered_year)
