import streamlit as st
import pandas as pd

from src.gui.components.comparison import make_comparison_page, make_comparison_toolbar
from src.gui.components.cached import get_edam_output
from src.gui.components.column_display import make_column_container
from src.gui.components.bottom_toolbar import make_bottom_toolbar, _reset_profile
from src.gui.components.welcome import make_welcome_page
from src.gui.components.session_state import SessionKey
from src.edam.column_embeddings.embeddings import get_column_embeddings, visualize_column_embeddings

import itertools


def load_embeddings() -> pd.DataFrame | None:
    future = st.session_state[SessionKey.COLUMN_EMBEDDINGS]
    if future.done():
        return future.result()
    return None


def main():
    if SessionKey.CONFIG in st.session_state:
        data = get_edam_output(st.session_state[SessionKey.CONFIG])
        st.header("EDaM Profile Visualization")
        make_bottom_toolbar(data)  # display the toolbar first

        with st.expander("Column Embedding Visualization", expanded=True):
            embeddings = load_embeddings()
            if embeddings is None:
                with st.container(horizontal=True, vertical_alignment="center"):
                    st.write("Embeddings generation in progress...")
                    st.space("stretch")
                    st.button("", icon=":material/refresh:", help="Try again", on_click=st.rerun, type="primary")
            else:
                visualize_column_embeddings(emb_df=embeddings)

        # NOTE: Upgrade streamlit to 1.67 for this to work.
        #       This is equivalent to the commented 
        #       implementation below but cleaner.
        grid = st.grid(2, dense=True)
        for col in data.column_metrics:
            with grid.container(border=True, height="stretch"):
                make_column_container(col, data)


        # for columns in itertools.batched(data.column_metrics.children.values(), 2):
        #     ui_columns = st.columns(2)
        #     for i, col in enumerate(columns):
        #         with ui_columns[i]:
        #             with st.container(border=True, height="stretch"):
        #                 make_column_container(col, data)

    elif SessionKey.UPLOADED_PROFILES in st.session_state:
        make_comparison_page()
        make_comparison_toolbar()
    else:
        make_welcome_page()

main()