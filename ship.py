import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def generate_metrics(filtered_df):
    num_transactions = filtered_df.shape[0]
    shipping_mode_counts_filtered = filtered_df["Ship Mode"].value_counts()
    top_shipping_mode = shipping_mode_counts_filtered.idxmax()
    ship_state_counts_filtered = filtered_df["State"].value_counts()
    top_shipping_state = ship_state_counts_filtered.idxmax()

    metrics = {
        "num_transactions": num_transactions,
        "top_shipping_mode": top_shipping_mode,
        "top_shipping_mode_count": int(shipping_mode_counts_filtered[top_shipping_mode]),
        "top_shipping_state": top_shipping_state,
        "top_shipping_state_count": int(ship_state_counts_filtered[top_shipping_state]),
    }
    return metrics

def generate_transactions_plot(df):
    transactions_by_year = df["Year"].value_counts().sort_index()
    transactions_by_year.index = transactions_by_year.index.astype(int)
    fig = px.line(
        x=transactions_by_year.index,
        y=transactions_by_year.values,
        markers=True,
        labels={"x": "Year", "y": "Number of Transactions"}
    )
    transactions_by_month = df["Month"].value_counts().sort_index()
    transactions_by_month.index = transactions_by_month.index.astype(str)
    fig_month = px.line(
        x=transactions_by_month.index,
        y=transactions_by_month.values,
        markers=True,
        labels={"x": "Month", "y": "Number of Transactions"}
    )
        
    fig.update_xaxes(tickmode="linear")
    fig_month.update_xaxes(tickmode="linear")
    return fig, fig_month

def generate_delivery_analysis(filtered_df):
    filtered_df["Order Date"] = pd.to_datetime(filtered_df["Order Date"], format="%m/%d/%Y")
    filtered_df["Ship Date"] = pd.to_datetime(filtered_df["Ship Date"], format="%m/%d/%Y")
    filtered_df["Shipping Duration"] = (filtered_df["Ship Date"] - filtered_df["Order Date"]).dt.days

    average_shipping_delay = filtered_df.groupby("Ship Mode")["Shipping Duration"].mean().reset_index()
    average_shipping_delay.rename(columns={"Shipping Duration": "Average Shipping Duration (Days)"}, inplace=True)

    average_estimated_duration = {
        "First Class": 2,
        "Same Day": 0,
        "Second Class": 3,
        "Standard Class": 5,
    }

    def is_late(row):
        return row["Shipping Duration"] > average_estimated_duration.get(row["Ship Mode"], 0)

    filtered_df["Late Shipment"] = filtered_df.apply(is_late, axis=1)
    shipment_counts = filtered_df.groupby("Ship Mode")["Late Shipment"].agg(["sum", "count"])
    shipment_counts["On Time Delivery"] = shipment_counts["count"] - shipment_counts["sum"]
    shipment_counts["Late Delivery"] = shipment_counts["sum"]
    shipment_counts = shipment_counts.reset_index()

    return average_shipping_delay, shipment_counts

def generate_shipping_state_map(filtered_df):
    state_counts = filtered_df["State"].value_counts().reset_index()
    state_counts.columns = ["State", "Count"]

    state_abbrev = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", 
        "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
        "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", 
        "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
        "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
        "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", 
        "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    }

    state_counts["State"] = state_counts["State"].apply(lambda x: state_abbrev.get(x, x)).str.upper()

    state_coords = {
        "AL": (32.806671, -86.791130), "AK": (61.370716, -152.404419), "AZ": (33.729759, -111.431221),
        "AR": (34.969704, -92.373123), "CA": (36.116203, -119.681564), "CO": (39.059811, -105.311104),
        "CT": (41.597782, -72.755371), "DE": (39.318523, -75.507141), "FL": (27.766279, -81.686783),
        "GA": (33.040619, -83.643074), "HI": (21.094318, -157.498337), "ID": (44.240459, -114.478828),
        "IL": (40.349457, -88.986137), "IN": (39.849426, -86.258278), "IA": (42.011539, -93.210526),
        "KS": (38.526600, -96.726486), "KY": (37.668140, -84.670067), "LA": (31.169546, -91.867805),
        "ME": (44.693947, -69.381927), "MD": (39.063946, -76.802101), "MA": (42.230171, -71.530106),
        "MI": (43.326618, -84.536095), "MN": (45.694454, -93.900192), "MS": (32.741646, -89.678696),
        "MO": (38.456085, -92.288368), "MT": (46.921925, -110.454353), "NE": (41.125370, -98.268082),
        "NV": (38.313515, -117.055374), "NH": (43.452492, -71.563896), "NJ": (40.298904, -74.521011),
        "NM": (34.840515, -106.248482), "NY": (42.165726, -74.948051), "NC": (35.630066, -79.806419),
        "ND": (47.528912, -99.784012), "OH": (40.388783, -82.764915), "OK": (35.565342, -96.928917),
        "OR": (44.572021, -122.070938), "PA": (40.590752, -77.209755), "RI": (41.680893, -71.511780),
        "SC": (33.856892, -80.945007), "SD": (44.299782, -99.438828), "TN": (35.747845, -86.692345),
        "TX": (31.054487, -97.563461), "UT": (40.150032, -111.862434), "VT": (44.045876, -72.710686),
        "VA": (37.769337, -78.169968), "WA": (47.400902, -121.490494), "WV": (38.491226, -80.954456),
        "WI": (44.268543, -89.616508), "WY": (42.755966, -107.302490),
    }

    coords_df = pd.DataFrame.from_dict(state_coords, orient="index", columns=["Latitude", "Longitude"]).reset_index()
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

    return fig

def display_all_shippings(filtered_df,df):
    metrics = generate_metrics(filtered_df)
    transactions_fig, transactions_fig_month = generate_transactions_plot(df)
    average_shipping_delay, shipment_counts = generate_delivery_analysis(filtered_df)
    shipping_map_fig = generate_shipping_state_map(filtered_df)
    st.write("## Metric")
    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Total Shippings", metrics["num_transactions"])
    metric2.metric("Top Shipping Mode", metrics["top_shipping_mode"], metrics["top_shipping_mode_count"])
    metric3.metric("Top Shipping State", metrics["top_shipping_state"], metrics["top_shipping_state_count"])

    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    view_option = st.radio("Select View", ("Yearly", "Monthly"))
    
    if view_option == "Yearly":
        st.subheader("Transactions by Year")
        st.plotly_chart(transactions_fig)
    else:
        st.subheader("Transactions by Month")
        st.plotly_chart(transactions_fig_month)

    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    
    delivery1, delivery2 = st.columns([0.3, 0.7])

    with delivery1:
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

    st.subheader("Shipping State Destination")
    st.plotly_chart(shipping_map_fig, use_container_width=True)

