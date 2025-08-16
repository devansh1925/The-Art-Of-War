import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Defense Revenue Insights", layout="wide")

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

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/updated_defense_companies_2005_2020.csv")
    except FileNotFoundError:
        st.error("Data file not found at data/updated_defense_companies_2005_2020.csv")
        st.stop()

    # ─── NORMALIZE COMPANY NAMES ────────────────────────────────────────────────
    # 1. trim whitespace
    df["Company"] = df["Company"].str.strip()

    # 2. drop trailing numbers
    df["Company"] = df["Company"].str.replace(r"\d+$", "", regex=True)

    # 3. replace punctuation (hyphens, slashes, periods, commas) with space
    df["Company"] = df["Company"].str.replace(r"[^\w\s]", " ", regex=True)

    # 4. collapse multiple spaces into one
    df["Company"] = df["Company"].str.replace(r"\s+", " ", regex=True)

    # 5. lowercase then title-case
    df["Company"] = df["Company"].str.lower().str.title()

    # ─── OPTIONAL: FUZZY-MAP NEAR-DUPLICATES ────────────────────────────────────
    # (requires Python stdlib difflib)
    from difflib import get_close_matches
    cleaned = {}
    for name in df["Company"].unique():
        # try to match against already-accepted names
        match = get_close_matches(name, cleaned.values(), n=1, cutoff=0.85)
        cleaned[name] = match[0] if match else name
    df["Company"] = df["Company"].map(cleaned)

    return df

# Load dataset
df = load_data()
all_companies = sorted(df["Company"].unique())
year_selected = df["Year"].max()

# App title
st.title("💼 Defense Companies Analysis (2005–2020)")

# Create horizontal tabs
tab1, tab2, tab3, tab4 = st.tabs(["Animations", "Trend", "Sunburst", "Bubble"])

with tab1:
    st.subheader("🎞️ Animated Top Companies by Defense Revenue (2005–2020)")
    top_n = st.slider("Top N Countries", min_value=5, max_value=30, value=10, key="top_n_anim")
    # Animated bar chart: top N by revenue each year
    top_countries_over_time = (
        df.groupby(["Year", "Country"])["Defense_Revenue_From_A_Year_Ago"]
        .sum()
        .reset_index()
        .sort_values(by=["Year", "Defense_Revenue_From_A_Year_Ago"], ascending=[True, False])
        .groupby("Year")
        .apply(lambda x: x.head(top_n))
        .reset_index(drop=True)
    )
    max_revenue = top_countries_over_time["Defense_Revenue_From_A_Year_Ago"].max()
    fig1 = px.bar(
        top_countries_over_time,
        x="Defense_Revenue_From_A_Year_Ago",
        y="Country",
        color="Country",
        animation_frame="Year",
        orientation="h",
        title=f"Top {top_n} Countries by Defense Revenue",
        labels={"Defense_Revenue_From_A_Year_Ago": "Defense Revenue"},
        height=500
    )
    fig1.update_layout(
        xaxis=dict(range=[0, max_revenue]),
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(t=40, l=0, r=0, b=0)
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("🎞️ Animated Total Number of Companies by Country (2005–2020)")
    # Animated bar chart: count of companies per country each year
    company_count = (
        df.groupby(["Year", "Country"])["Company"]
        .nunique()
        .reset_index(name="Count")
        .sort_values(by=["Year", "Count"], ascending=[True, False])
        .groupby("Year")
        .apply(lambda x: x.head(top_n))
        .reset_index(drop=True)
    )
    max_count = company_count["Count"].max()
    fig2 = px.bar(
        company_count,
        x="Count",
        y="Country",
        color="Country",
        animation_frame="Year",
        orientation="h",
        title="Total Number of Companies by Country",
        labels={"Count": "Number of Companies"},
        height=500
    )
    fig2.update_layout(
        xaxis=dict(range=[0, max_count]),
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(t=40, l=0, r=0, b=0)
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("📈 Defense Revenue Trend (2005–2020)")
    selected_companies = st.multiselect(
        "Select Companies for Trend", all_companies, key="trend_sel"
    )
    if selected_companies:
        trend_df = df[df["Company"].isin(selected_companies)]
    else:
        # Default to top companies from the latest year
        latest_top = (
            df[df["Year"] == year_selected]
            .nlargest(10, "Defense_Revenue_From_A_Year_Ago")["Company"].tolist()
        )
        trend_df = df[df["Company"].isin(latest_top)]
    fig_trend = px.line(
        trend_df,
        x="Year",
        y="Defense_Revenue_From_A_Year_Ago",
        color="Company",
        markers=True,
        title="Defense Revenue Trend Over Time",
        labels={"Defense_Revenue_From_A_Year_Ago": "Defense Revenue"},
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with tab3:
    st.subheader("🌞 Interactive Sunburst: Country → Company")
    col1, col2 = st.columns(2)
    with col1:
        num_countries = st.number_input(
            "Number of Top Countries",
            min_value=1,
            max_value=20,
            value=5,
            key="sb_countries"
        )
    with col2:
        num_companies = st.number_input(
            "Number of Top Companies per Country",
            min_value=1,
            max_value=20,
            value=3,
            key="sb_companies"
        )
    df_year = df[df["Year"] == year_selected]
    top_countries_list = (
        df_year.groupby("Country")["Defense_Revenue_From_A_Year_Ago"].sum()
        .nlargest(num_countries).index
    )
    sb_df = df_year[df_year["Country"].isin(top_countries_list)]
    sunburst_data = (
        sb_df.groupby(["Country", "Company"])["Defense_Revenue_From_A_Year_Ago"].sum()
        .reset_index()
    )
    top_entries = (
        sunburst_data.groupby("Country").apply(
            lambda x: x.nlargest(num_companies, "Defense_Revenue_From_A_Year_Ago")
        ).reset_index(drop=True)
    )
    top_entries["World"] = "World"
    fig_sun = px.sunburst(
        top_entries,
        path=["World", "Country", "Company"],
        values="Defense_Revenue_From_A_Year_Ago",
        color="Country",
        maxdepth=2
    )
    fig_sun.update_layout(
        margin=dict(t=40, l=0, r=0, b=0),
        sunburstcolorway=px.colors.qualitative.Pastel,
        extendsunburstcolors=True
    )
    st.plotly_chart(fig_sun, use_container_width=True)

    with st.expander("📄 View Raw Data"):
        st.dataframe(df_year)

with tab4:
    st.subheader("🎥 Animated Bubble Chart: Company Evolution (2005–2020)")
    top_n_bubble = st.slider(
        "Top N Companies per Year (for animation)",
        5, 30, 15,
        key="bubble_n"
    )
    anim_df = (
        df.groupby(["Year","Company","Country"], as_index=False)
        .agg({
            "Defense_Revenue_From_A_Year_Ago": "sum",
            "Total Revenue": "sum",
            "%of Revenue from Defence": "mean"
        })
    )
    anim_df["rank"] = anim_df.groupby("Year")["Defense_Revenue_From_A_Year_Ago"].rank("dense", ascending=False)
    anim_df = anim_df[anim_df["rank"] <= top_n_bubble]
    fig_bubble = px.scatter(
        anim_df,
        x="Total Revenue",
        y="Defense_Revenue_From_A_Year_Ago",
        animation_frame="Year",
        animation_group="Company",
        size="%of Revenue from Defence",
        color="Country",
        hover_name="Company",
        size_max=60,
        title="Company Evolution Over Time",
        labels={
            "Defense_Revenue_From_A_Year_Ago": "Defense Revenue",
            "Total Revenue": "Total Revenue",
            "%of Revenue from Defence": "% from Defense"
        },
    )
    fig_bubble.update_layout(margin=dict(t=40, l=0, r=0, b=0))
    st.plotly_chart(fig_bubble, use_container_width=True)

# Footer
st.markdown(
    """
    ---  
    🔍 Built with Streamlit & Plotly • Interactive Defense Revenue Insights
    """
)
