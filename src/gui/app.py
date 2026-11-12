
import os
import sys
import streamlit as st
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent.parent.absolute()))

dir = Path(__file__).parent.absolute()

pg = st.navigation(
    [
        st.Page(dir / "pages/1_single-analysis-new.py", title="Edam Analysis"),
        #st.Page(dir / "pages/9_single-analysis-old.py", title="Edam Analysis")
    ],
    position="top",
)

st.set_page_config(
    layout="centered",
    page_title="Edam Analyzer",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .block-container {
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 2rem;
            margin: auto;
        }
    </style>
""", unsafe_allow_html=True)

# st.logo(
#     Path("resources/ur-logo.svg").absolute(),
#     link="https://www.uni-regensburg.de/informatik-data-science/fakultaet/einrichtungen/data-engineering"
# )

pg.run()
