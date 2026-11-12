import streamlit as st
import pandas as pd

from pathlib import Path

from src.edam.config.config import Dataset, EdamConfig, MetricPreselection
from .background_thread import run_in_background
from .session_state import SessionKey
from src.edam.column_embeddings.embeddings import get_column_embeddings
from .dataprofile_filter import setup_selections
from .cached import get_edam_output
from ..single_dataset.representations import _BUILTIN_REPRESENTATIONS

_WELCOME_TEXT = """# Welcome to EDaM

Welcome to EDaM, the new data profiling tool!
"""


def _make_edam_config() -> None:
    with st.container(border=True, width="stretch"):
        st.subheader("EDaM Profile Calculation")
        file = st.file_uploader("Dataset", type=["csv", "json"], max_upload_size=None)
        config = None
        if file is not None:
            config = EdamConfig(
                Dataset(contents=file),
                MetricPreselection.ALL
            )
            with st.container(horizontal=True):
                config.precision = st.number_input(
                    "Float precision", 
                    min_value=0, 
                    max_value=20, 
                    step=1, 
                    value=config.precision
                )
                config.categorical_threshold = st.number_input(
                    "Categorical threshold", 
                    min_value=0.0, 
                    max_value=1.0, 
                    step=0.05, 
                    value=config.categorical_threshold
                )
            config.categorical_columns = tuple(st.multiselect(
                "Categorical columns", 
                config.categorical_columns, 
                accept_new_options=True, 
                placeholder="Enter column names ..."
            ))
            # config.genson.enabled = st.checkbox(
            #     "Genson", 
            #     value=config.genson.enabled, 
            #     disabled=True
            # )
        with st.container(horizontal_alignment="right"):
            if st.button(
                "Calculate", 
                disabled=file is None, 
                type="primary",
            ):
                st.session_state[SessionKey.CONFIG] = config
                run_in_background(get_column_embeddings, SessionKey.COLUMN_EMBEDDINGS, pd.read_csv(config.dataset.get_bytesio()))
                data = get_edam_output(config)
                st.session_state[SessionKey.SELECTED_METRICS] = setup_selections(_BUILTIN_REPRESENTATIONS, data.column_metrics)
                st.rerun()


def _make_diff_config():
    with st.container(border=True, width="stretch"):
        st.subheader("EDaM Profile Comparison")
        with st.container(horizontal=True):
            first_data = st.file_uploader("Profile 1", accept_multiple_files="directory")
            second_data = st.file_uploader("Profile 2", accept_multiple_files="directory")
        with st.container(horizontal_alignment="right"):
            if st.button("Compare", disabled=(first_data is None or second_data is None), type="primary"):
                st.session_state[SessionKey.UPLOADED_PROFILES] = [
                    {Path(d.name).suffix: d for d in data_upload}
                    for data_upload in (first_data, second_data)
                ]
                st.rerun()



def make_welcome_page():
    left, right = st.columns(2)

    with left:
        st.write(_WELCOME_TEXT)

    with right:
        _make_edam_config()
        _make_diff_config()
