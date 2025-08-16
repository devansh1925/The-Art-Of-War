import streamlit as st
import base64

st.set_page_config(
    page_title="Acknowledgements",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def set_gif_background(gif_path: str):
    """
    Reads a local GIF and injects CSS to use it as the <body> background.
    """
    with open(gif_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/gif;base64,{b64}") no-repeat center center fixed;
            background-size: cover;
        }}
        /* Apply black, right-aligned text only in the main view container */
        [data-testid="stAppViewContainer"] {{
          color: black !important;
          text-align: right !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
set_gif_background("data/Flag_Animation.gif")

st.title("Acknowledgements")
# Inject custom CSS
st.markdown(
    """
    <style>
    /* Full-screen app container with centered native-size background */
    
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

st.markdown("""
""", unsafe_allow_html=False)
st.markdown("""**The success of this project is attributed to the dedication, expertise,**""", unsafe_allow_html=False)
st.markdown("""**and collaborative efforts of all the team members of Group 8**""", unsafe_allow_html=False)

st.markdown("""
""", unsafe_allow_html=False)
st.markdown("""**Abhijeet Shravansing Rajput**""",unsafe_allow_html=False)
st.markdown("""**Abhinandan Singh Baghel**""",unsafe_allow_html=False)
st.markdown("""**Devansh Dhaval Mehta**""",unsafe_allow_html=False)
st.markdown("""**Divya Sharma**""",unsafe_allow_html=False)
st.markdown("""**Kamal Kant Tripathi**""",unsafe_allow_html=False)
st.markdown("""**Patel Ujjaval Girishbhai**""",unsafe_allow_html=False)
st.markdown("""**Sohel Samirkhan Modi**""",unsafe_allow_html=False)
st.markdown("""**Vishal Kumar**""",unsafe_allow_html=False)

