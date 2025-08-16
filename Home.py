import streamlit as st

st.set_page_config(
    page_title="🎖️ Art of War",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS
st.markdown(
    """
    <style>
    /* Full-screen app container with centered native-size background */
    .stApp {
        background: url('https://static.vecteezy.com/system/resources/previews/027/103/278/non_2x/silhouette-soldiers-descend-from-helicopter-warning-of-danger-against-a-sunset-background-with-space-for-text-promoting-peace-and-cessation-of-hostilities-free-photo.jpg')
                    no-repeat center center fixed;
        background-size: cover;  /* show at native resolution, fully visible */
    }

    /* Make sidebar slightly translucent so the background peeks through */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.6);
    }

    /* Right-aligned hero text */
    .css-1lcbmhc {  /* you may need to adjust this selector to match your Streamlit version */
        text-align: center !important;
        padding: 1rem 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Your rest of Home.py content…
st.markdown("<h1>🎖️ Art of War</h1>", unsafe_allow_html=True)
st.markdown("""
###  Welcome to the Military Data Analysis Platform

Embark on a journey through the unseen dynamics of global defense.

**What you’ll discover:**
- **Defense Budgets** – track spending trends across decades  
- **Military Strength** – compare personnel, tanks, aircraft and more  
- **Trade & Alliances** – map out import/export flows and partnerships  
- **Hidden Patterns** – uncover insights with interactive charts  

Dive deep into data and explore the forces shaping our world — all in one place!
""")
