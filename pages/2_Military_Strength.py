import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="🌍 Military Dashboard", layout="wide")

# ─── INJECT GLOBAL CSS ─────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Full-screen war-scene background */
    .stApp {
      background: url('https://t4.ftcdn.net/jpg/03/49/86/71/240_F_349867133_a2Upqgg99LIDvsGbR4Of3a0bXCwqzrAQ.jpg')
                  no-repeat center center fixed;
      background-size: cover;
    }
    /* Translucent sidebar */
    [data-testid="stSidebar"] {
      background-color: rgba(0, 0, 0, 0.6);
    }
    /* Centered hero text */
    .css-1lcbmhc {
      text-align: center !important;
      padding: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# ─── DATA LOAD ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/military_data.csv")
    return df

df = load_data()
numeric_cols = df.select_dtypes(include='number').columns.tolist()
country_list = df['country'].unique().tolist()

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align: center; color: #2E8B57;'>🌏 Global Military Power Visualization</h1>",
    unsafe_allow_html=True
)

# ─── NAVIGATION TABS ────────────────────────────────────────────────────────────
tabs = st.tabs([
    "🔍 Country Profile Explorer",
    "📺 Choropleth Map",
    "📊 Compare Countries",
    "🏆 Top-N Ranking Tool",
    "🧠 Correlation Explorer"
])

# ─── MODULE 1: Country Profile Explorer ─────────────────────────────────────────
with tabs[0]:
    st.header("🔍 Country Profile Explorer")

    country = st.selectbox(
        "Select a country:",
        sorted(df['country'].unique()),
        index=sorted(df['country'].unique()).index('India')
    )
    row = df[df['country'] == country].iloc[0]

    st.markdown("### 📌 General Information")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='color:#4CAF50;'>🪖 Military Personnel</h3>", unsafe_allow_html=True)
        st.markdown(
            f"Active Personnel: <span style='color:#009688;'>{int(row['Active Personnel']):,}</span><br>"
            f"<i style='color:#888;'>Number of active military members.</i>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"Reserve Personnel: <span style='color:#009688;'>{int(row['Reserve Personnel']):,}</span><br>"
            "<i style='color:#888;'>Number of personnel on reserve duty.</i>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"Paramilitary: <span style='color:#009688;'>{int(row['Paramilitary']):,}</span><br>"
            "<i style='color:#888;'>Forces performing military duties but not part of the regular army.</i>",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown("<h3 style='color:#2196F3;'>✈ Military Assets</h3>", unsafe_allow_html=True)
        st.markdown(
            f"Total Aircraft Strength: <span style='color:#009688;'>{int(row['Total Aircraft Strength']):,}</span><br>"
            "<i style='color:#888;'>Number of aircraft in the military's inventory.</i>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"Tanks: <span style='color:#009688;'>{int(row['Tanks']):,}</span><br>"
            "<i style='color:#888;'>Number of tanks in military service.</i>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"Oil Production (Barrels/day): <span style='color:#009688;'>{int(row['Oil Production']):,}</span><br>"
            "<i style='color:#888;'>Daily oil production (in barrels) of the country.</i>",
            unsafe_allow_html=True
        )

    st.markdown("### 💰 Economic Overview")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<h3 style='color:#FFC107;'>💵 Economic Overview</h3>", unsafe_allow_html=True)
        st.markdown(
            f"Defense Budget (USD): <span style='color:#009688;'>${int(row['Defense Budget']):,}</span><br>"
            "<i style='color:#888;'>Amount allocated for national defense spending.</i>",
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"External Debt (USD): <span style='color:#009688;'>${int(row['External Debt']):,}</span><br>"
            "<i style='color:#888;'>Total debt the country owes to foreign entities.</i>",
            unsafe_allow_html=True
        )

# ─── MODULE 2: Choropleth Map ───────────────────────────────────────────────────
with tabs[1]:
    st.subheader("📺 Global Metric Choropleth Map")
    metric = st.selectbox("Select Metric", numeric_cols, key="choropleth_metric")
    fig = px.choropleth(
        df,
        locations="country_code",
        color=metric,
        hover_name="country",
        color_continuous_scale="Agsunset",
        projection="natural earth",
        template="plotly_dark",
        title=f"Global Distribution of {metric}"
    )
    st.plotly_chart(fig, use_container_width=True)

# ─── MODULE 3: Compare Countries ────────────────────────────────────────────────
with tabs[2]:
    st.subheader("📊 Compare Countries")
    countries = st.multiselect("Select Countries", country_list, default=country_list[:5])
    metric = st.selectbox("Select Attribute to Compare", numeric_cols, key="compare_metric")
    subset = df[df['country'].isin(countries)]
    fig = px.bar(
        subset,
        x="country",
        y=metric,
        color="country",
        title=f"Comparison on {metric}",
        text_auto=".2s",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig, use_container_width=True)

# ─── MODULE 4: Top-N Ranking Tool ───────────────────────────────────────────────
with tabs[3]:
    st.subheader("🏆 Top-N Countries by Metric")
    metric = st.selectbox("Select Metric", numeric_cols, key="ranking_metric")
    n = st.slider("Select Top N", 5, 30, 10, key="topn_slider")
    top_df = df.nlargest(n, metric)[['country', metric]]
    st.markdown(f"#### Top {n} Countries by {metric}")
    fig = px.bar(
        top_df,
        x=metric,
        y="country",
        orientation="h",
        text_auto=".2s",
        template="plotly_dark",
        color_discrete_sequence=['goldenrod']
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_df.reset_index(drop=True), use_container_width=True)

# ─── MODULE 5: Correlation Explorer ─────────────────────────────────────────────
with tabs[4]:
    st.markdown("## 🧠 Correlation Heatmap of Military Metrics (Interactive)")
    initial_attributes = [
        "Active Personnel", "Defense Budget", "Oil Production", "Tanks",
        "Total Aircraft Strength", "Submarines", "Reserve Personnel"
    ]
    selected_attrs = st.multiselect("Select Attributes", initial_attributes, default=initial_attributes)
    if len(selected_attrs) >= 2:
        corr = df[selected_attrs].corr().round(2)
        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="Viridis",
            aspect="auto",
            labels=dict(color="Correlation"),
        )
        fig.update_layout(
            title="Correlation Matrix of Selected Metrics",
            title_font_size=26,
            title_font_color="white",
            paper_bgcolor="#1E1E1E",
            plot_bgcolor="#2B2B2B",
            font_color="white",
            font=dict(family="Arial, sans-serif", size=14),
            margin=dict(l=40, r=40, t=60, b=40),
        )
        fig.update_xaxes(side="bottom", tickangle=45, showgrid=True,
                         tickfont=dict(size=12, color="white"))
        fig.update_yaxes(tickfont=dict(size=12, color="white"), showgrid=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least two attributes to compute the correlation matrix.")
