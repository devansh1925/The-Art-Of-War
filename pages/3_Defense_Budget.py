import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from io import BytesIO

st.set_page_config(page_title="Defense Budget", layout="wide")
st.title("🌍 Global Defense Budget Insights")
st.markdown("Explore patterns and trends in military spending across the globe via the tabs below.")
st.divider()

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
    """Load and validate defence-budget CSV."""
    df = pd.read_csv("data/Cleaned_Defence_Budget.csv")
    years = [str(y) for y in range(1960, 2021)]
    # Essential columns
    if "Country Code" not in df.columns or "Country Name" not in df.columns:
        st.error("Dataset must include 'Country Code' and 'Country Name'.")
        st.stop()
    # Check for missing year columns
    missing = [y for y in years if y not in df.columns]
    if missing:
        st.warning(f"Missing year columns: {', '.join(missing)}")
    # Coerce numeric
    for y in years:
        if y in df.columns:
            df[y] = pd.to_numeric(df[y], errors="coerce")
    return df, years

df, year_columns = load_data()

# Create the three horizontal tabs
tab1, tab2, tab3 = st.tabs([
    "🌐 Global Spending (% of GDP)",
    "📊 Top Spenders vs India",
    "🕰️ Decade Breakdown"
])

# --- Tab 1: Global Military Spending Choropleth Globe ---
with tab1:
    st.header("🌐 Global Military Spending (% of GDP)")
    years_int = sorted([int(y) for y in year_columns if y.isdigit()])
    year = st.slider("Select Year", min_value=years_int[0], max_value=years_int[-1], value=years_int[-1])
    ystr = str(year)
    df_year = df[["Country Name", "Country Code", ystr]].dropna(subset=[ystr])

    if df_year.empty:
        st.warning("No data for that year.")
    else:
        fig = px.choropleth(
            df_year,
            locations="Country Code",
            color=ystr,
            hover_name="Country Name",
            hover_data={ystr: ':.2f%'},  # Format value nicely
            projection="orthographic",
            color_continuous_scale=px.colors.sequential.Blues,
            range_color=(0, df_year[ystr].quantile(0.95)),
            title=f"Defence Spending as % of GDP in {year}",
            labels={ystr: "%GDP"}  # <-- 🛠️ This line fixes your label!
        )

        # Update layout
        fig.update_layout(
            margin=dict(l=10, r=10, t=50, b=10),
            geo=dict(bgcolor='rgba(0,0,0,0)', showland=True, landcolor="rgb(217,217,217)"),
            coloraxis_colorbar=dict(
                title="% of GDP",
                title_side="top",
                ticks="outside",
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"🔝 Top 5 Spenders in {year}")
            top5 = df_year.nlargest(5, ystr).set_index("Country Name")[[ystr]]
            top5.columns = ["Spending (% GDP)"]
            st.dataframe(top5, use_container_width=True)
        with col2:
            st.subheader(f"🔻 Bottom 5 Spenders in {year}")
            bot5 = df_year.nsmallest(5, ystr).set_index("Country Name")[[ystr]]
            bot5.columns = ["Spending (% GDP)"]
            st.dataframe(bot5, use_container_width=True)

# --- Tab 2: Top Spenders vs India ---
with tab2:
    st.header("📊 Top Defence Spenders vs India")
    year = st.slider("Select Year", min_value=years_int[0], max_value=years_int[-1], value=(years_int[0]+years_int[-1])//2, key="tab2_year")
    col = str(year)
    data = df[["Country Name", col]].dropna()
    ranked = data.sort_values(col, ascending=False)
    top10 = ranked.head(10)
    india = data[data["Country Name"]=="India"]
    if not india.empty and "India" not in top10["Country Name"].values:
        top10 = pd.concat([top10, india])

    fig = px.bar(
        top10,
        x=col, y="Country Name",
        orientation="h",
        color=col,
        color_continuous_scale="Plasma",
        title=f"Top 10 Spenders vs India in {year}",
        labels={col: "% of GDP"}  # 🛠️ Added label to fix x-axis and colorbar!
    )
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        margin=dict(l=10, t=50),
        coloraxis_colorbar=dict(
            title="% of GDP",  # 🛠️ Title for the colorbar
            title_side="top",
            ticks="outside",
        ),
        xaxis_title="% of GDP"  # 🛠️ x-axis title changed
    )

    st.plotly_chart(fig, use_container_width=True)

    if not india.empty:
        rank = (ranked[col] > india[col].iloc[0]).sum() + 1
        st.markdown(f"**India’s rank in {year}:** #{rank}")

    st.markdown("---")
    st.subheader(f"Summary Metrics for {year}")
    vals = df[col].dropna()
    avg, med, mn, mx = vals.mean(), vals.median(), vals.min(), vals.max()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Average", f"{avg:.2f}%")
    c2.metric("Median", f"{med:.2f}%")
    c3.metric("Minimum", f"{mn:.2f}%")
    c4.metric("Maximum", f"{mx:.2f}%")

    # India’s trend over time
    st.markdown("---")
    india_trend = (
        df[df["Country Name"]=="India"]
        .melt(id_vars="Country Name", value_vars=year_columns, var_name="Year", value_name="% GDP")
        .dropna()
    )
    if not india_trend.empty:
        fig2 = px.line(india_trend, x="Year", y="% GDP",
                       title="India's Spending (% GDP) Over Time")
        st.plotly_chart(fig2, use_container_width=True)

# --- Tab 3: Decade‐Wise Breakdown ---
with tab3:
    st.header("🕰️ Decade‐Wise Defence Investment Breakdown")

    country = st.selectbox("Select Country", df["Country Name"].unique(), key="tab3_country")
    sel = df[df["Country Name"] == country]

    # Prepare data for sunburst
    sunburst_data = []

    # Year-wise data
    year_values = {}
    for start in range(1960, 2020, 10):
        years = [str(y) for y in range(start, start + 10)]
        for year in years:
            year_values[year] = sel[year].values[0]

    # Root node (1960–2020)
    all_years = [sel[str(y)].values[0] for y in range(1960, 2020)]
    root_avg = sum(all_years) / len(all_years)
    root_sum = sum(all_years)

    decade_values = {}
    decade_averages = {}
    for start in range(1960, 2020, 10):
        years = [str(y) for y in range(start, start + 10)]
        decade_label = f"{start}s"
        values = [year_values[y] for y in years]
        decade_values[decade_label] = sum(values)         # Sum for hierarchy
        decade_averages[decade_label] = sum(values) / len(values)  # Average for color and hover

    # Build hierarchy
    sunburst_data.append({
        "id": "1960–2020",
        "label": "1960–2020",
        "parent": "",
        "Value": root_sum,         # Sum is used for correct hierarchy
        "%GDP": root_avg,          # Hover and color based on average
        "ColorMetric": root_avg
    })

    for decade_label, dec_sum in decade_values.items():
        sunburst_data.append({
            "id": decade_label,
            "label": decade_label,
            "parent": "1960–2020",
            "Value": dec_sum,
            "%GDP": decade_averages[decade_label],
            "ColorMetric": decade_averages[decade_label]
        })
        start_year = int(decade_label[:4])
        for y in range(start_year, start_year + 10):
            y_str = str(y)
            sunburst_data.append({
                "id": y_str,
                "label": y_str,
                "parent": decade_label,
                "Value": year_values[y_str],         # Use spending % for size
                "%GDP": year_values[y_str],          # Same here for hover
                "ColorMetric": year_values[y_str]
            })

    df_sunburst = pd.DataFrame(sunburst_data)

    # Sunburst Chart
    st.subheader(f"🌐 Decade-wise Defense Spending (1960–2020) – **{country}**")
    fig_sb = px.sunburst(
        df_sunburst,
        names="label",
        parents="parent",
        values="Value",   # <- Sum is used to construct chart
        color="ColorMetric",
        color_continuous_scale="Blues",
        branchvalues="total",
        hover_data={"%GDP": True, "parent": False, "ColorMetric": False, "Value": False}  # only %GDP shown
    )

    fig_sb.update_traces(
        insidetextorientation='auto',
        selector=dict(type='sunburst'),
        textinfo='label',
        maxdepth=2
    )

    fig_sb.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        coloraxis_colorbar=dict(title="% GDP")   # <<< Update color bar title
    )
    st.plotly_chart(fig_sb, use_container_width=True)

    st.markdown("---")

    # Radial Bar Chart
    st.subheader("📅 Choose a Decade to Explore Year-wise Trends")
    decade_options = ["1960–2020"] + [f"{year}s" for year in range(1960, 2020, 10)]
    decade_choice = st.selectbox("Select Decade", decade_options, key="tab3_decade")

    if decade_choice == "1960–2020":
        years = [str(y) for y in range(1960, 2020)]
    else:
        start_decade = int(decade_choice[:4])
        years = [str(y) for y in range(start_decade, start_decade + 10)]

    trend = sel[years].T.reset_index()
    trend.columns = ["Year", "Spending"]
    trend["Year"] = trend["Year"].astype(int)

    avg_spending = trend["Spending"].mean()
    st.markdown(f"### 📊 Average Spending in {decade_choice}: **{avg_spending:.2f}% of GDP**")

    st.subheader("🌀 Year-wise Defense Spending (Radial Bar View)")

    col_center = st.columns([1, 4, 1])
    with col_center[1]:
        angles = np.linspace(0, 2 * np.pi, len(trend), endpoint=False)
        radii = trend["Spending"].values
        labels = trend["Year"].astype(str).tolist()

        fig_r, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

        norm = plt.Normalize(radii.min(), radii.max())
        colors = plt.cm.viridis(norm(radii))

        bars = ax.bar(angles, radii, width=2*np.pi/len(angles), bottom=0.0,
                      color=colors, edgecolor="black")

        ax.set_xticks([])
        ax.set_yticklabels([])

        # Place year labels slightly outside the bar
        for angle, label in zip(angles, labels):
            ax.plot([angle, angle], [0, max(radii) + 1], color="gray", linewidth=0.5, linestyle="--")

            rotation = np.degrees(angle)
            alignment = 'left'
            if 90 < rotation < 270:
                rotation += 180
                alignment = 'right'

            ax.text(angle, max(radii) + 1.5, label,
                    rotation=rotation,
                    ha=alignment,
                    va='center',
                    fontsize=9,
                    rotation_mode='anchor')

        # Colorbar
        sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
        sm.set_array([])
        cbar = fig_r.colorbar(sm, ax=ax, pad=0.15, fraction=0.035, shrink=0.6)
        cbar.ax.set_title('% of GDP', fontsize=10, pad=10)

        fig_r.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        st.image(buf)
        plt.close()

    st.markdown("---")









