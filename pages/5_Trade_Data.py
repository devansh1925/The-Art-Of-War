import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Trade Balance Analysis", layout="wide")
st.title("Trade Balance Analysis")
st.markdown(
    """
    This section provides insights into the trade balance of various countries, focusing on India's trade partners and historical events.
    """
)        

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


# Custom CSS for popups and styling
st.markdown("""
<style>
/* Animation Definitions */
@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
@keyframes wave {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* General Styling */
body {
    background-color: #F5F5F5; /* Changed to soft gray */
}
.stApp {
    max-width: 100%;
    margin: 0 auto;
    padding: 20px;
}

/* Header and Selection */
.stHeader {
    text-align: center;
    color: #1E3A8A;
    font-size: 28px;
    margin-bottom: 20px;
    animation: fadeIn 0.5s ease-in-out;
}
.stSelectbox {
    text-align: center;
    padding: 10px;
    background: linear-gradient(90deg, #E6F0FA, #FFFFFF);
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    animation: fadeIn 0.5s ease-in-out 0.2s backwards;
}
.stSelectbox:hover {
    background: linear-gradient(90deg, #ADD8E6, #E6F0FA);
}

/* Chart Styling */
.plotly-chart {
    margin: 20px auto;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    animation: fadeIn 0.5s ease-in-out;
}

/* Popup Containers */
.popup-container, .trade-popup-container {
    background: linear-gradient(135deg, #E6F0FA, #FFFFFF);
    border-radius: 15px;
    padding: 25px;
    width: 450px;
    max-width: 90%;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    margin: 20px auto;
    opacity: 0;
    animation: fadeIn 0.5s ease-out forwards, wave 6s infinite;
    font-family: 'Verdana', sans-serif;
    position: relative;
    background-size: 200% 200%;
}
.trade-popup-container {
    background: linear-gradient(135deg, #F0FFF4, #E6FFE6);
}
.popup-container::before {
    content: '📅';
    position: absolute;
    top: 10px;
    left: 10px;
    font-size: 24px;
    color: #1E3A8A;
    opacity: 0.7;
}
.trade-popup-container::before {
    content: '🌐';
    position: absolute;
    top: 10px;
    left: 10px;
    font-size: 24px;
    color: #1E3A8A;
    opacity: 0.7;
}

/* Popup Title and Description */
.popup-title {
    font-size: 24px;
    font-weight: bold;
    color: #1E3A8A;
    margin-bottom: 15px;
    text-align: center;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
}
.popup-description {
    font-size: 16px;
    color: #2A4365;
    line-height: 1.8;
    text-align: justify;
}

/* Trade Info */
.trade-info {
    font-size: 18px;
    color: #1E3A8A;
    font-weight: bold;
    margin-top: 10px;
    text-align: center;
    animation: fadeIn 0.5s ease-in-out 0.3s backwards;
}

/* Close Button */
.close-button {
    display: block;
    margin: 20px auto 0;
    padding: 12px 30px;
    background: linear-gradient(90deg, #3B82F6, #60A5FA);
    color: white;
    border: none;
    border-radius: 25px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s ease;
    animation: pulse 1.5s infinite;
}
.close-button:hover {
    background: linear-gradient(90deg, #1E40AF, #3B82F6);
    transform: scale(1.1);
    box-shadow: 0 5px 15px rgba(59, 130, 246, 0.5);
}

/* Ensure Popups Are Visible When Active */
.popup-container.show {
    display: block !important;
}
.trade-popup-container.show {
    display: block !important;
}
</style>
""", unsafe_allow_html=True)

# Load data first
trade_df = pd.read_csv("data/exports_imports_cleaned.csv")
events_df = pd.read_csv("data/trade_events_updated2.csv", encoding="latin-1")

# Initialize session state for both popups and selected year
if 'show_popup' not in st.session_state:
    st.session_state['show_popup'] = False
if 'popup_content' not in st.session_state:
    st.session_state['popup_content'] = None
if 'show_trade_popup' not in st.session_state:
    st.session_state['show_trade_popup'] = False
if 'trade_popup_content' not in st.session_state:
    st.session_state['trade_popup_content'] = None
if 'selected_year' not in st.session_state:
    st.session_state['selected_year'] = sorted(trade_df['financial_year(start)'].unique())[0]  # Default to first year

# Centered Country Selection
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.header("Select a Country")
    selected_country = st.selectbox("", options=sorted(trade_df["country"].unique()), index=0, help="Choose a country to view its trade balance trends")

# Filter trade data for selected country and add a 'year' column
country_trade_df = trade_df[trade_df['country'] == selected_country].copy()
country_trade_df['year'] = country_trade_df['financial_year(start)'].astype(int)

# Bar Chart: Trade Balance Over Time
st.subheader(f"Trade Balance Trend for {selected_country}")
fig = px.bar(
    country_trade_df,
    x='year',
    y='trade_balance',
    color='trade_balance',
    color_continuous_scale=['#E6F0FA', '#ADD8E6', '#87CEEB', '#4682B4', '#1E40AF'],  # Blue gradient
    labels={'trade_balance': 'Trade Balance (Mil USD)', 'year': 'Year'},
    title=f"Trade Balance Trend for {selected_country}"
)
fig.update_traces(
    marker_line_color='#333333',
    marker_line_width=1.5,
    opacity=0.9,
    hovertemplate='<b>Year</b>: %{x}<br><b>Trade Balance</b>: %{y:.2f}M<extra></extra>'
)
fig.update_layout(
    xaxis=dict(
        title='Year',
        tickangle=45,
        title_font=dict(size=14, color='#333333'),
        tickfont=dict(size=12, color='#333333')
    ),
    yaxis=dict(
        title='Trade Balance (Mil USD)',
        title_font=dict(size=14, color='#333333'),
        tickfont=dict(size=12, color='#333333'),
        zeroline=True,
        zerolinecolor='#333333',
        gridcolor='#E0E0E0'
    ),
    plot_bgcolor='#F0F8FF',
    paper_bgcolor='#F0F8FF',
    title_font_size=20,
    font=dict(color='#333333', size=12),
    margin=dict(l=50, r=50, t=60, b=60),
    showlegend=False
)

fig.update_layout(
    coloraxis_colorbar=dict(
        title="Trade Balance (Mil USD)",
        title_font=dict(color="#333333"),
        tickfont=dict(color="#333333")
    )
)


# Render bar chart with click event capture
event = st.plotly_chart(fig, use_container_width=True, key="trade_balance_chart", on_select="rerun")

# Handle click events for the bar chart and display historical event popup
if event:
    points = event.get("selection", {}).get("points")
    if points:
        year_clicked = int(points[0]["x"])
        trade_row = country_trade_df[country_trade_df['year'] == year_clicked]
        if not trade_row.empty:
            trade_balance = trade_row['trade_balance'].iloc[0]
            st.markdown(f"<div class='trade-info'>Year: {year_clicked} | Trade Balance: {trade_balance:.2f}M</div>", unsafe_allow_html=True)

            event_row = events_df[(events_df['country'] == selected_country) & (events_df['year'] == year_clicked)]
            if not event_row.empty:
                event_description = event_row['event_description'].iloc[0]
                st.session_state['show_popup'] = True
                st.session_state['popup_content'] = {
                    'year': year_clicked,
                    'description': event_description
                }

# Display historical event popup with dynamic visibility
if st.session_state['show_popup'] and st.session_state['popup_content']:
    popup_content = st.session_state['popup_content']
    st.markdown(
        f"""
        <div class='popup-container show'>
            <div class='popup-title'>Historical Event ({popup_content['year']})</div>
            <div class='popup-description'>{popup_content['description']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Close Popup", key="close_popup_btn"):
        st.session_state['show_popup'] = False
        st.session_state['popup_content'] = None
        st.rerun()
else:
    st.markdown("<style>.popup-container { display: none; }</style>", unsafe_allow_html=True)

# Year selection dropdown
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.subheader("Select Year")
    selected_year = st.selectbox("", options=sorted(trade_df['financial_year(start)'].unique()), index=sorted(trade_df['financial_year(start)'].unique()).index(st.session_state['selected_year']), key="year_select", help="Choose a year to view top trading partners")
    st.session_state['selected_year'] = selected_year  # Update session state

# Filter trade data for selected year and calculate dynamic trade partners
trade_year_df = trade_df[trade_df['financial_year(start)'] == st.session_state['selected_year']]
trade_summary = trade_year_df.groupby('country').agg({
    'import': 'sum',
    'export': 'sum'
}).reset_index()
trade_summary['total_trade'] = trade_summary['import'] + trade_summary['export']
trade_summary['imports_billion'] = trade_summary['import'] / 1000  # Convert to billion USD
trade_summary['exports_billion'] = trade_summary['export'] / 1000  # Convert to billion USD
trade_summary['total_trade_billion'] = trade_summary['total_trade'] / 1000  # Convert to billion USD
trade_summary['trade_balance_billion'] = trade_summary['exports_billion'] - trade_summary['imports_billion']
top_n = 6
trade_partners_df = trade_summary.sort_values(by='total_trade', ascending=False).head(top_n)

# Bubble Chart: Top Trading Partners for Selected Year
st.subheader(f"India's Top Trading Partners (FY {st.session_state['selected_year']})")
fig_bubble = px.scatter(
    trade_partners_df,
    x='country',
    y='total_trade_billion',
    size='total_trade_billion',
    color='country',
    color_discrete_sequence=px.colors.sequential.Blues_r,  # Blue color scheme
    title=f"India's Top Trading Partners (FY {st.session_state['selected_year']})",
    size_max=60,
    hover_data=['total_trade_billion']
)
fig_bubble.update_traces(
    marker=dict(line=dict(color='#333333', width=1.5)),
    hovertemplate='<b>%{x}</b><br>Total Trade: $%{y}B<extra></extra>'
)
fig_bubble.update_layout(
    xaxis=dict(
        title='Country',
        title_font=dict(size=14, color='#333333'),
        tickfont=dict(size=12, color='#333333')
    ),
    yaxis=dict(
        title='Total Trade (Billion USD)',
        title_font=dict(size=14, color='#333333'),
        tickfont=dict(size=12, color='#333333'),
        gridcolor='#E0E0E0'
    ),
    legend=dict(
        title_font_color="#333333",
        font_color="#333333"
    ),
    plot_bgcolor='#F0F8FF',
    paper_bgcolor='#F0F8FF',
    title_font_size=20,
    font=dict(color='#333333', size=12),
    margin=dict(l=50, r=50, t=60, b=60),
    showlegend=True
)


# Render bubble chart with click event capture
bubble_event = st.plotly_chart(fig_bubble, use_container_width=True, key="bubble_chart", on_select="rerun")

# Handle click events for the bubble chart and display trade popup
if bubble_event:
    points = bubble_event.get("selection", {}).get("points")
    if points:
        country_clicked = points[0]["x"]
        trade_row = trade_partners_df[trade_partners_df['country'] == country_clicked]
        if not trade_row.empty:
            st.session_state['show_trade_popup'] = True
            st.session_state['trade_popup_content'] = {
                'country': country_clicked,
                'imports': trade_row['imports_billion'].iloc[0],
                'exports': trade_row['exports_billion'].iloc[0],
                'trade_balance': trade_row['trade_balance_billion'].iloc[0]
            }

# Display trade details popup with dynamic visibility
if st.session_state['show_trade_popup'] and st.session_state['trade_popup_content']:
    trade_popup_content = st.session_state['trade_popup_content']
    st.markdown(
        f"""
        <div class='trade-popup-container show'>
            <div class='popup-title'>Trade Details with {trade_popup_content['country']} (FY {st.session_state['selected_year']})</div>
            <div class='popup-description'>
                Imports: ${trade_popup_content['imports']:.3f}B<br>
                Exports: ${trade_popup_content['exports']:.3f}B<br>
                Trade Balance: ${trade_popup_content['trade_balance']:.3f}B
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Close Trade Popup", key="close_trade_popup_btn"):
        st.session_state['show_trade_popup'] = False
        st.session_state['trade_popup_content'] = None
        st.rerun()
else:
    st.markdown("<style>.trade-popup-container { display: none; }</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 📊 Section 3: Comparative Analysis – Exports & Imports Over Time
st.markdown("---")
st.markdown("### 📊 3. Comparative Analysis: Exports & Imports Over Time")

# Let the user pick multiple countries to compare
compare_countries = st.multiselect(
    "Select countries to compare:",
    options=sorted(trade_df["country"].unique()),
    default=[selected_country]  # default to the one you first picked
)

if compare_countries:
    # Build a small DataFrame with year, country, export & import
    comp_df = trade_df[trade_df["country"].isin(compare_countries)].copy()
    comp_df["year"] = comp_df["financial_year(start)"].astype(int)

    # Exports timeline
    fig_exp = px.line(
        comp_df,
        x="year",
        y="export",
        color="country",
        markers=True,
        title="Exports Over Time",
        labels={"export": "Exports (Mil USD)", "year": "Year"},
        template="plotly_white"
    )
    fig_exp.update_layout(
        xaxis=dict(
            title="Year",
            title_font=dict(color="white"),
            tickmode="linear",
            tick0=comp_df["year"].min(),
            dtick=1,
            tickfont=dict(color="white")
        ),
        yaxis=dict(
            title="Exports (Mil USD)",
            title_font=dict(color="white"),
            tickfont=dict(color="white")
        ),
        legend=dict(
            title="",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig_exp, use_container_width=True)
    
    # Imports timeline
    fig_imp = px.line(
        comp_df,
        x="year",
        y="import",
        color="country",
        markers=True,
        title="Imports Over Time",
        labels={"import": "Imports (Mil USD)", "year": "Year"},
        template="plotly_white",
        color_discrete_sequence=["red"] 
    )
    fig_imp.update_layout(
        xaxis=dict(
            title="Year",
            title_font=dict(color="white"),
            tickmode="linear",
            tick0=comp_df["year"].min(),
            dtick=1,
            tickfont=dict(color="white")
        ),
        yaxis=dict(
            title="Imports (Mil USD)",
            title_font=dict(color="white"),
            tickfont=dict(color="white")
        ),
        legend=dict(
            title="",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig_imp, use_container_width=True)
else:
    st.info("Select at least one country above to see its exports/imports timeline.")

