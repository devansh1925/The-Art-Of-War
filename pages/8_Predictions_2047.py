import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(page_title="Top Military Powers Prediction 2047", layout="wide")

st.title("Top Military Powers Prediction for 2047")

# ─── INJECT GLOBAL CSS ─────────────────────────────────────────────────────────
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

# Load data
@st.cache_data
def load_data():
    ms = pd.read_csv("data/2024_military_strength_by_country.csv")
    db = pd.read_csv("data/Cleaned_Defence_Budget.csv")
    return ms, db

military_strength, defense_budget = load_data()

def create_strength_score(df):
    metrics = [
        'total_national_populations',
        'active_service_military_manpower',
        'total_military_aircraft_strength',
        'total_combat_tank_strength',
        'navy_strength',
        'national_annual_defense_budgets',
        'purchasing_power_parities'
    ]
    for m in metrics:
        if m in df.columns:
            df[m] = pd.to_numeric(df[m], errors='coerce')
    df_clean = df.dropna(subset=[m for m in metrics if m in df.columns])
    scaler = StandardScaler()
    scaled = scaler.fit_transform(df_clean[metrics])
    sdf = pd.DataFrame(scaled, columns=metrics)
    sdf['strength_score'] = sdf.mean(axis=1)
    sdf['country'] = df_clean['country'].values
    sdf['pwr_index'] = pd.to_numeric(df_clean['pwr_index'], errors='coerce')
    return sdf.sort_values('strength_score', ascending=False)

def analyze_growth_trajectory(strength_df, budget_df):
    growth = []
    for c in strength_df['country']:
        subset = budget_df[budget_df['Country Name'] == c]
        years = [str(y) for y in range(2000, 2021) if str(y) in subset.columns]
        if subset.empty or len(years) < 5:
            growth.append(0)
        else:
            vals = subset[years].values.flatten().astype(float)
            idx = np.arange(len(vals))[~np.isnan(vals)].reshape(-1,1)
            y = vals[~np.isnan(vals)]
            model = LinearRegression().fit(idx, y)
            growth.append(model.coef_[0])
    strength_df['growth_slope'] = growth
    gs = strength_df['growth_slope']
    strength_df['growth_norm'] = (gs - gs.min())/(gs.max()-gs.min() + 1e-9)
    return strength_df

def predict_future(df, target_year=2047):
    years_proj = target_year - 2024
    df['projected_strength'] = df['strength_score'] + df['growth_norm'] * (years_proj / 5)
    df['projection_score'] = df['projected_strength'] - 0.1 * df['pwr_index']
    return df.sort_values('projection_score', ascending=False)

# Select top N
top_n = st.slider("Select how many top countries to display", min_value=5, max_value=30, value=10)

# Run predictions
with st.spinner("Calculating predictions..."):
    strength = create_strength_score(military_strength)
    strength = analyze_growth_trajectory(strength, defense_budget)
    future = predict_future(strength)

# Display current vs predicted
col1, col2 = st.columns(2)
with col1:
    st.subheader(f"Current Top {top_n} Military Powers (2024)")
    cur = strength[['country','strength_score']].head(top_n).rename(columns={'country':'Country','strength_score':'Strength Score'})
    st.table(cur)
with col2:
    st.subheader(f"Predicted Top {top_n} Military Powers (2047)")
    pred = future[['country','projection_score']].head(top_n).rename(columns={'country':'Country','projection_score':'Projection Score'})
    st.table(pred)

# Show rank changes
st.subheader(f"Changes in Rankings (2024 → 2047)")

cr = {c:i+1 for i,c in enumerate(cur['Country'])}
pr = {c:i+1 for i,c in enumerate(pred['Country'])}
changes=[]
for c in set(list(cr.keys())+list(pr.keys())):
    changes.append({'Country':c,'2024':cr.get(c,top_n+10),'2047':pr.get(c,top_n+10)})
chg_df = pd.DataFrame(changes)

fig, ax = plt.subplots(figsize=(8,6))
for _, r in chg_df.iterrows():
    ax.plot([1, 2], [r['2024'], r['2047']], '-', alpha=0.3)
ax.scatter([1]*len(chg_df), chg_df['2024'], s=80, label='2024')
ax.scatter([2]*len(chg_df), chg_df['2047'], s=80, label='2047')
for _, r in chg_df.iterrows():
    ax.text(0.8, r['2024'], r['Country'], ha='right')
    ax.text(2.1, r['2047'], r['Country'], ha='left')
ax.set_xticks([1, 2])
ax.set_xticklabels(['2024', '2047'])
ax.set_ylim(top_n + 5, 0)
ax.set_ylabel('Rank')
ax.legend()
st.pyplot(fig)

