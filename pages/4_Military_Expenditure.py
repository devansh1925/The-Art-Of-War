import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- App config and title ---
st.set_page_config(page_title="Military Expenditure Dashboard", layout="wide")
st.title("🌍 Military Expenditure Visualization (1960–2018)")

# ─── GLOBAL CSS ───────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp {
      background: url('https://t4.ftcdn.net/jpg/03/49/86/71/240_F_349867133_a2Upqgg99LIDvsGbR4Of3a0bXCwqzrAQ.jpg')
                  no-repeat center center fixed;
      background-size: cover;
    }
    [data-testid="stSidebar"] {
      background-color: rgba(0, 0, 0, 0.6);
    }
    .css-1lcbmhc {
      text-align: center !important;
      padding: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Load & preprocess data ---
@st.cache_data
def load_data():
    df = pd.read_excel("data/Military_Expenditure_final_rounded.xlsx")
    df = df[df['Indicator Name'] == 'Military expenditure (current USD)']
    df = df[df["Type"] == "Country"]
    return df

df = load_data()
years_all     = [str(y) for y in range(1960, 2019)]
all_countries = sorted(df['Name'].unique())
default_countries = ['United States', 'China', 'Russian Federation']

# Prepare sum_df for Top/Bottom analyses (over full range—can be reindexed per slider)
sum_df_full = df.set_index('Name')[years_all].sum(axis=1)

# ─── TABS ─────────────────────────────────────────────────────────────
tabs = st.tabs([
    "1️⃣ Time Series",
    "2️⃣ Top/Bottom 5",
    "3️⃣ Global Map"
])

# ─── Tab 1: Expenditure Over Time & Single-Year Comparison ────────────
with tabs[0]:
    st.subheader("📈 Expenditure Over Time")
    countries = st.multiselect(
        "Select countries:",
        options=all_countries,
        default=[c for c in default_countries if c in all_countries]
    )
    year_range = st.slider(
        "Select year range:",
        min_value=1960, max_value=2018, value=(1990, 2018)
    )

    if countries:
        df_sel = (
            df[df['Name'].isin(countries)]
            [['Name'] + years_all]
            .set_index('Name')
            .T
            .astype(float)
        )
        df_sel.index = df_sel.index.astype(int)
        df_sel = df_sel.loc[year_range[0] : year_range[1]]

        fig = go.Figure()
        for c in df_sel.columns:
            fig.add_trace(go.Scatter(
                x=df_sel.index,
                y=df_sel[c] / 1e9,
                mode='lines',              # ← markers removed
                name=c,
                hovertemplate=(
                    f"Country: {c}<br>"   # ← hard-code country
                    "Year: %{x}<br>"
                    "Exp: %{y:.2f} B USD<extra></extra>"
                ),
                hoverlabel=dict(bgcolor='black', font_color='white')
            ))

        fig.update_layout(
            template='plotly_dark',
            xaxis=dict(
                title='Year',
                tickmode='array',
                tickvals=[y for y in df_sel.index if y % 5 == 0]
            ),
            yaxis=dict(title='Expenditure (Billion USD)')
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Single-Year Comparison")
        year = st.selectbox("Select a year:", options=df_sel.index[::-1])
        values = (df_sel.loc[year] / 1e9)

        fig2 = go.Figure(go.Bar(
            x=values.index,
            y=values.values,
            marker_color='skyblue',
            hovertemplate="Country: %{x}<br>Exp: %{y:.2f} B USD<extra></extra>",
            hoverlabel=dict(bgcolor='black', font_color='white')
        ))
        fig2.update_layout(
            template='plotly_dark',
            title=f'Year {year}',
            yaxis_title='Expenditure (Billion USD)'
        )
        st.plotly_chart(fig2, use_container_width=True)

# ─── Tab 2: Top/Bottom 5 Spenders ──────────────────────────────────────
with tabs[1]:
    st.subheader("💰 Top/Bottom 5 Spenders")
    range_tb = st.slider(
        "Select range for Top/Bottom analysis:",
        min_value=1960, max_value=2018, value=(1960, 2018)
    )
    cols_tb = [str(y) for y in range(range_tb[0], range_tb[1] + 1)]
    sum_df = df.set_index('Name')[cols_tb].sum(axis=1)

    top5 = sum_df.nlargest(5)
    bot5 = sum_df[sum_df > 0].nsmallest(5)

    # Top/Bottom side by side
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top 5**")
        fig_top = go.Figure(go.Bar(
            x=top5.index,
            y=top5.values / 1e9,
            marker_color='green',
            hovertemplate="Country: %{x}<br>Total: %{y:.2f} B USD<extra></extra>",
            hoverlabel=dict(bgcolor='black', font_color='white')
        ))
        fig_top.update_layout(template='plotly_dark', yaxis_title='Total (Billion USD)')
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.markdown("**Bottom 5**")
        fig_bot = go.Figure(go.Bar(
            x=bot5.index,
            y=bot5.values / 1e9,
            marker_color='red',
            hovertemplate="Country: %{x}<br>Total: %{y:.2f} B USD<extra></extra>",
            hoverlabel=dict(bgcolor='black', font_color='white')
        ))
        fig_bot.update_layout(template='plotly_dark', yaxis_title='Total (Billion USD)')
        st.plotly_chart(fig_bot, use_container_width=True)

    # Full-width Trends, with country-name injected
    st.subheader("📈 Trends of Top 5 Spenders Over Time")
    df_top_trend = (
        df[df['Name'].isin(top5.index)][['Name'] + cols_tb]
        .set_index('Name').T
    )
    df_top_trend.index = df_top_trend.index.astype(int)

    fig_top_trend = go.Figure()
    for country in df_top_trend.columns:
        fig_top_trend.add_trace(go.Scatter(
            x=df_top_trend.index,
            y=df_top_trend[country] / 1e9,
            mode='lines',
            name=country,
            hovertemplate=(
                f"Country: {country}<br>"
                "Year: %{x}<br>"
                "Exp: %{y:.2f} B USD<extra></extra>"
            ),
            hoverlabel=dict(bgcolor='black', font_color='white')
        ))
    fig_top_trend.update_layout(
        template='plotly_dark',
        xaxis_title='Year',
        yaxis_title='Expenditure (Billion USD)'
    )
    st.plotly_chart(fig_top_trend, use_container_width=True)

    st.subheader("📈 Trends of Bottom 5 Spenders Over Time")
    df_bot_trend = (
        df[df['Name'].isin(bot5.index)][['Name'] + cols_tb]
        .set_index('Name').T
    )
    df_bot_trend.index = df_bot_trend.index.astype(int)

    fig_bot_trend = go.Figure()
    for country in df_bot_trend.columns:
        fig_bot_trend.add_trace(go.Scatter(
            x=df_bot_trend.index,
            y=df_bot_trend[country] / 1e9,
            mode='lines',
            name=country,
            hovertemplate=(
                f"Country: {country}<br>"
                "Year: %{x}<br>"
                "Exp: %{y:.2f} B USD<extra></extra>"
            ),
            hoverlabel=dict(bgcolor='black', font_color='white')
        ))
    fig_bot_trend.update_layout(
        template='plotly_dark',
        xaxis_title='Year',
        yaxis_title='Expenditure (Billion USD)'
    )
    st.plotly_chart(fig_bot_trend, use_container_width=True)

# ─── Tab 3: Global Choropleth Map ─────────────────────────────────────
with tabs[2]:
    st.subheader("🗺 Global Map View")
    year_map = st.slider(
        "Select map year:",
        min_value=1960, max_value=2018, value=2018
    )
    map_df = (
        df[['Name', str(year_map)]]
        .rename(columns={str(year_map): 'Value'})
    )
    map_df = map_df[map_df['Value'] > 0]

    fig_map = px.choropleth(
        map_df,
        locations='Name',
        locationmode='country names',
        color='Value',
        color_continuous_scale='YlOrRd',
        projection='orthographic',
        hover_name='Name',
        hover_data={'Value': ':.2f'}
    )
    fig_map.update_traces(
        hovertemplate="Country: %{location}<br>Value: %{z:.2f} USD<extra></extra>",
        hoverlabel=dict(bgcolor='black', font_color='white')
    )
    fig_map.update_layout(
        template='plotly_dark',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_map, use_container_width=True)
