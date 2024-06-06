import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

file_path = "Superstore.csv"
df = pd.read_csv(file_path, encoding="ISO-8859-1")
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.sidebar.image("superstore_logo.png", width=300)

st.sidebar.markdown('<div style="margin-top: 50px;"></div>', unsafe_allow_html=True)

shipping, sales, product, customer = st.tabs(
    ["Shipping", "Sales", "Product", "Customer"]
)

df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")

df["Year"] = df["Order Date"].dt.year

year_filter = st.sidebar.selectbox(
    "Filter by Year", ["All"] + sorted(df["Year"].unique())
)

if year_filter == "All":
    filtered_year = df
else:
    filtered_year = df[df["Year"] == year_filter]

filtered_year["Month"] = filtered_year["Order Date"].dt.month

month_filter = st.sidebar.selectbox(
    "Filter by Month", ["All"] + sorted(filtered_year["Month"].unique())
)

if month_filter == "All":
    filtered_data = filtered_year
else:
    filtered_data = filtered_year[filtered_year["Month"] == month_filter]

min_date = filtered_data["Order Date"].min()
max_date = filtered_data["Order Date"].max()
latest_date = max_date

if year_filter == "All" and month_filter == "All":
    date_range = st.sidebar.date_input(
        "Filter by Date Range",
        [latest_date, latest_date],
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
    num_transactions = filtered_df.shape[0]
    shipping_mode_counts_filtered = filtered_df["Ship Mode"].value_counts()
    top_shipping_mode = shipping_mode_counts_filtered.idxmax()
    ship_state_counts_filtered = filtered_df["State"].value_counts()
    top_shipping_state = ship_state_counts_filtered.idxmax()

    shipping.write("## Metric")

    metric1, metric2, metric3 = shipping.columns(3)
    metric1.metric("Total Shippings", num_transactions)
    metric2.metric(
        "Top Shipping Mode",
        top_shipping_mode,
        int(shipping_mode_counts_filtered[top_shipping_mode]),
    )
    metric3.metric(
        "Top Shipping State",
        top_shipping_state,
        int(ship_state_counts_filtered[top_shipping_state]),
    )

    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")

    st.subheader("Transactions by Year")
    transactions_by_year = filtered_df["Year"].value_counts().sort_index()
    transactions_by_year.index = transactions_by_year.index.astype(int)

    fig = px.line(
        x=transactions_by_year.index,
        y=transactions_by_year.values,
        markers=True,
        labels={"x": "Year", "y": "Number of Transactions"},
    )

    fig.update_xaxes(tickmode="linear")

    st.plotly_chart(fig)

    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")

    delivery1, delivery2 = st.columns([0.3, 0.7])
    with delivery1:
        filtered_df["Order Date"] = pd.to_datetime(
            filtered_df["Order Date"], format="%m/%d/%Y"
        )
        filtered_df["Ship Date"] = pd.to_datetime(
            filtered_df["Ship Date"], format="%m/%d/%Y"
        )
        filtered_df["Shipping Duration"] = (
            filtered_df["Ship Date"] - filtered_df["Order Date"]
        ).dt.days
        average_shipping_delay = (
            filtered_df.groupby("Ship Mode")["Shipping Duration"].mean().reset_index()
        )
        average_shipping_delay.rename(
            columns={"Shipping Duration": "Average Shipping Duration (Days)"},
            inplace=True,
        )
        st.subheader("Average Shipping Estimation")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.table(round(average_shipping_delay, 2))

    with delivery2:
        average_estimated_duration = {
            "First Class": 2,
            "Same Day": 0,
            "Second Class": 3,
            "Standard Class": 5,
        }

        def is_late(row):
            return (
                row["Shipping Duration"] > average_estimated_duration[row["Ship Mode"]]
            )

        filtered_df["Late Shipment"] = filtered_df.apply(is_late, axis=1)
        shipment_counts = filtered_df.groupby("Ship Mode")["Late Shipment"].agg(
            ["sum", "count"]
        )
        shipment_counts["On Time Delivery"] = (
            shipment_counts["count"] - shipment_counts["sum"]
        )
        shipment_counts["Late Delivery"] = shipment_counts["sum"]
        shipment_counts = shipment_counts.reset_index()

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=shipment_counts["Ship Mode"],
                y=shipment_counts["Late Delivery"],
                name="Late Delivery",
                text=shipment_counts["Late Delivery"],
                textposition="inside",
                marker_color="indianred",
            )
        )

        fig.add_trace(
            go.Bar(
                x=shipment_counts["Ship Mode"],
                y=shipment_counts["On Time Delivery"],
                name="On Time Delivery",
                text=shipment_counts["On Time Delivery"],
                textposition="inside",
                marker_color="lightskyblue",
            )
        )
        fig.update_layout(
            xaxis_title="Shipping Mode",
            yaxis_title="Number of Deliveries",
            barmode="stack",
        )

        st.subheader(f"Delivery On Time vs Late")
        st.plotly_chart(fig)

    state_counts = filtered_df["State"].value_counts().reset_index()
    state_counts.columns = ["State", "Count"]

    state_abbrev = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
    }
    state_counts["State"] = state_counts["State"].apply(
        lambda x: state_abbrev.get(x, x)
    )

    state_counts["State"] = state_counts["State"].str.upper()

    state_coords = {
        "AL": (32.806671, -86.791130),
        "AK": (61.370716, -152.404419),
        "AZ": (33.729759, -111.431221),
        "AR": (34.969704, -92.373123),
        "CA": (36.116203, -119.681564),
        "CO": (39.059811, -105.311104),
        "CT": (41.597782, -72.755371),
        "DE": (39.318523, -75.507141),
        "FL": (27.766279, -81.686783),
        "GA": (33.040619, -83.643074),
        "HI": (21.094318, -157.498337),
        "ID": (44.240459, -114.478828),
        "IL": (40.349457, -88.986137),
        "IN": (39.849426, -86.258278),
        "IA": (42.011539, -93.210526),
        "KS": (38.526600, -96.726486),
        "KY": (37.668140, -84.670067),
        "LA": (31.169546, -91.867805),
        "ME": (44.693947, -69.381927),
        "MD": (39.063946, -76.802101),
        "MA": (42.230171, -71.530106),
        "MI": (43.326618, -84.536095),
        "MN": (45.694454, -93.900192),
        "MS": (32.741646, -89.678696),
        "MO": (38.456085, -92.288368),
        "MT": (46.921925, -110.454353),
        "NE": (41.125370, -98.268082),
        "NV": (38.313515, -117.055374),
        "NH": (43.452492, -71.563896),
        "NJ": (40.298904, -74.521011),
        "NM": (34.840515, -106.248482),
        "NY": (42.165726, -74.948051),
        "NC": (35.630066, -79.806419),
        "ND": (47.528912, -99.784012),
        "OH": (40.388783, -82.764915),
        "OK": (35.565342, -96.928917),
        "OR": (44.572021, -122.070938),
        "PA": (40.590752, -77.209755),
        "RI": (41.680893, -71.511780),
        "SC": (33.856892, -80.945007),
        "SD": (44.299782, -99.438828),
        "TN": (35.747845, -86.692345),
        "TX": (31.054487, -97.563461),
        "UT": (40.150032, -111.862434),
        "VT": (44.045876, -72.710686),
        "VA": (37.769337, -78.169968),
        "WA": (47.400902, -121.490494),
        "WV": (38.491226, -80.954456),
        "WI": (44.268543, -89.616508),
        "WY": (42.755966, -107.302490),
    }

    coords_df = pd.DataFrame.from_dict(
        state_coords, orient="index", columns=["Latitude", "Longitude"]
    ).reset_index()
    coords_df.columns = ["State", "Latitude", "Longitude"]

    state_counts = pd.merge(state_counts, coords_df, on="State", how="left")

    fig = px.choropleth(
        state_counts,
        locations="State",
        locationmode="USA-states",
        color="Count",
        scope="usa",
        color_continuous_scale="Blues",
    )
    for i, row in state_counts.iterrows():
        fig.add_trace(
            go.Scattergeo(
                locationmode="USA-states",
                lon=[row["Longitude"]],
                lat=[row["Latitude"]],
                text=row["State"],
                mode="text",
                showlegend=False,
            )
        )

    fig.update_layout(
        width=1800,
        height=800,
        geo=dict(
            lakecolor="rgb(255, 255, 255)",
            projection_type="albers usa",
        ),
    )

    st.subheader("Shipping State Destination")
    st.plotly_chart(fig, use_container_width=True)

with sales:
    total_sales = round(filtered_df["Sales"].sum())
    formated_total_sales = "{:,.0f}".format(total_sales)
    total_profit = round(filtered_df["Profit"].sum())
    formated_total_profit = "{:,.0f}".format(total_profit)

    filtered_df["Order Date"] = pd.to_datetime(
        filtered_df["Order Date"], format="%m/%d/%Y"
    )
    filtered_df["Month"] = filtered_df["Order Date"].dt.month
    filtered_df["Date"] = filtered_df["Order Date"].dt.day
    filtered_df["Year"] = filtered_df["Order Date"].dt.year

    yearly_sales = filtered_df.groupby("Year")["Sales"].sum().reset_index()
    yearly_profit = filtered_df.groupby("Year")["Profit"].sum().reset_index()
    ratio_profit = pd.DataFrame()
    ratio_profit["Year"] = yearly_profit["Year"]
    ratio_profit["Rasio"] = (yearly_profit["Profit"] / yearly_sales["Sales"]) * 100
    total_ratio_profit = round(ratio_profit["Rasio"].mean())

    sales.write("## Metric")

    metric1, metric2, metric3 = sales.columns(3)
    metric1.metric("Total Sales", f"${formated_total_sales}")
    metric2.metric("Total Profit", f"${formated_total_profit}")
    metric3.metric("Profit Ratio", f"{total_ratio_profit}%")

    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")

    sales_profit_by_year = (
        filtered_df.groupby("Year").agg({"Sales": "sum", "Profit": "sum"}).reset_index()
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

    st.subheader("Sales and Profit by Year")
    st.plotly_chart(fig, use_container_width=True)

    loss1, loss2 = st.columns(2)
    with loss1:
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

        st.subheader(f"Loss")
        loss = total_negative_profit * (-1)
        format_loss = "{:,.0f}".format(loss)
        st.write("Total Loss: -$", format_loss)
        st.plotly_chart(fig)
    with loss2:
        discounted_transactions = filtered_df[filtered_df["Discount"] > 0]
        discounted_transactions_by_year = (
            discounted_transactions.groupby("Year")
            .size()
            .reset_index(name="Total Discounted Transactions")
        )
        average_discount = discounted_transactions["Discount"].mean()
        fig = px.bar(
            discounted_transactions_by_year,
            x="Year",
            y="Total Discounted Transactions",
            labels={
                "Year": "Year",
                "Total Discounted Transactions": "Total Discounted Transactions",
            },
        )
        fig.update_layout(width=800)

        st.subheader(f"Total Discounted Transactions")
        format_average_percent = average_discount * 100
        format_average = "{:.1f}".format(format_average_percent)
        st.write("Average discount: ", format_average, "%")
        st.plotly_chart(fig)

    quantity_by_year = filtered_df.groupby("Year")["Quantity"].sum().reset_index()
    fig = px.bar(
        quantity_by_year,
        x="Year",
        y="Quantity",
        labels={"Year": "Year", "Quantity": "Total Quantity Sold"},
    )

    st.subheader("Total Quantity Sold by Year")
    st.plotly_chart(fig, use_container_width=True)

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

    st.subheader("Top 10 Products with Highest Loss:")
    st.table(top_loss_products)

    st.subheader("Top 10 Products with Highest Profit:")
    st.table(top_profitable_products)

    st.subheader("Top 10 Products with Highest Discount:")
    st.table(top_10_product_highest_discount)


with product:
    product_quantities = (
        filtered_df.groupby("Product Name")["Quantity"].sum().reset_index()
    )
    top_product_by_quantity = product_quantities.sort_values(
        by="Quantity", ascending=False
    ).head(1)
    top_product_name = top_product_by_quantity.iloc[0]["Product Name"]
    top_product_quantity = top_product_by_quantity.iloc[0]["Quantity"]

    product_counts = filtered_df["Product Name"].nunique()
    top_category = filtered_df["Category"].value_counts().idxmax()
    total_products_sold = filtered_df["Product Name"].value_counts()
    total_products_sold_len = len(total_products_sold)

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

    list_of_category = filtered_df["Category"].unique()
    list_of_sub_category = filtered_df["Sub-Category"].unique()
    category_col, subcategory_col = st.columns(2)

    with category_col:
        st.subheader("Transactions by Category")
        category_counts = filtered_df["Category"].value_counts()
        fig_category = px.bar(
            category_counts, x=category_counts.index, y=category_counts.values
        )
        fig_category.update_layout(yaxis_title="Number of Transactions")
        st.plotly_chart(fig_category)
    with subcategory_col:
        st.subheader("Transactions by Sub-Category")
        subcategory_counts = filtered_df["Sub-Category"].value_counts()
        fig_subcategory = px.bar(
            subcategory_counts, x=subcategory_counts.index, y=subcategory_counts.values
        )
        fig_subcategory.update_layout(yaxis_title="Number of Transactions")
        st.plotly_chart(fig_subcategory)

    st.markdown("---")

    region1, region2, region3 = st.columns(3)

    with region1:
        st.subheader("Product Segment")
        fig_categories_segment = px.pie(filtered_df, names="Segment", hole=0.3)
        st.plotly_chart(fig_categories_segment)

    with region2:
        st.subheader("Product Categories")
        fig_categories_region = px.pie(filtered_df, names="Category", hole=0.3)
        st.plotly_chart(fig_categories_region)

    with region3:
        st.subheader("Product Sub-Categories")
        fig_subcategories_region = px.pie(filtered_df, names="Sub-Category", hole=0.3)
        st.plotly_chart(fig_subcategories_region)

    product = st.columns(1)
    top_10_products_by_quantity = (
        product_quantities.sort_values(by="Quantity", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    top_10_products_by_quantity.index += 1
    top_10_product_highest_discount.index += 1

    columns_to_display_product = ["Product Name", "Quantity"]
    st.write("## Top 10 Products by Quantity Sold")
    st.table(top_10_products_by_quantity[columns_to_display_product])

    bottom_10_products_by_quantity = (
        product_quantities.sort_values(by="Quantity", ascending=True)
        .head(10)
        .reset_index(drop=True)
    )
    st.write("## Bottom 10 Products by Quantity Sold")
    st.table(bottom_10_products_by_quantity[columns_to_display_product])

with customer:
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

    customer_counts_by_year = (
        filtered_df.groupby("Year")["Customer Name"].nunique().reset_index()
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
    )
    st.subheader("Number of Customers Reached Each Year")
    st.plotly_chart(fig, use_container_width=True)

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
    st.subheader("Top 10 Customers with Highest Quantity Sold")
    st.table(top_customers_quantity)

    st.subheader("Top 10 Customers with Highest Profit")
    st.table(top_customers_profit)
