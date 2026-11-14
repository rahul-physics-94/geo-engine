
import streamlit as st

# --------------------------------------------------
# 1. Application Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Automated Statistical Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# 2. Application Navigation
# --------------------------------------------------

pages = {

    "Workspace": [

        st.Page(
            "pages/data_validation.py",
            title="Data Validation",
            icon=":material/fact_check:"
        )
    ]
}
# --------------------------------------------------
# 3. Initialise Navigation
# --------------------------------------------------

navigation = st.navigation(
    pages,
    position="sidebar"
)

# --------------------------------------------------
# 4. Global Sidebar Branding
# --------------------------------------------------

with st.sidebar:

    st.title("📊 ASA")

    st.caption(
        "Automated Statistical Analyst"
    )

    st.divider()

    st.caption(
        "Statistical Analysis | Experimentation | Causal Inference"
    )

# --------------------------------------------------
# 5. Run Selected Page
# --------------------------------------------------

navigation.run()
