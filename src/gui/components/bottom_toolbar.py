import streamlit as st
import pandas as pd

import json
from typing import Any
import io
from collections.abc import Callable
from concurrent.futures import Future


from src.edam.profile.profiles import DataProfile
from src.edam.config.config import EdamConfig
from .cached import cached_data_profile_to_dict
from .helpers import create_zip_archive, df_to_parquet_bytes
from .session_state import SessionKey
from .dataprofile_filter import build_filter, RepresentationSelection




@st.dialog("Data Profile", width="small", position="right")

def _show_profile(profile: dict[str, Any]):
    st.json(profile)

def _reset_profile():
    del st.session_state[SessionKey.CONFIG]
    st.rerun()

d = {"col1": [0, 1, 2, 3], "col2": pd.Series([2, 3], index=[2, 3])}
dummy_data = pd.DataFrame(data=d, index=[0, 1, 2, 3])

def build_downloader(
        data: DataProfile, 
        embeddings_future: Future,
        selected_metrics: RepresentationSelection,
        profile_name: str
    ) -> Callable[[], io.BytesIO]:
    def downloader() -> io.BytesIO:
        filter = build_filter(selected_metrics)
        dict_profile = data.filter(filter).to_dict()
        embeddings = embeddings_future.result()  # waits until finished
        files = {
            f"{profile_name}_profile.json": json.dumps(dict_profile, indent=4),
            f"{profile_name}_embeddings.parquet": df_to_parquet_bytes(embeddings)
        }
        return create_zip_archive(files)
    return downloader



@st.fragment
def make_bottom_toolbar(data: DataProfile, embeddings: pd.DataFrame = dummy_data):
    dict_profile = cached_data_profile_to_dict(data.metadata.hash, data)
    with st.bottom:
        with st.container(horizontal=True, horizontal_alignment="center"):
            with st.container(border=True, width="content", horizontal=True):
                st.button("", on_click=_reset_profile, icon=":material/home:", help="back to home")
                st.button("", on_click=_show_profile, args=(dict_profile,), icon=":material/find_in_page:", help="inspect profile")
                if isinstance(config := st.session_state.get(SessionKey.CONFIG), EdamConfig):
                    default_name = config.dataset.path.stem
                else:
                    default_name = ""
                profile_name = st.text_input(
                    "input", 
                    default_name, 
                    label_visibility="collapsed", 
                    placeholder="profile name", 
                    type="default", 
                    live="0s", 
                    width=150,
                    help="profile name"
                )
                zipfile = build_downloader(
                    data, 
                    st.session_state[SessionKey.COLUMN_EMBEDDINGS],
                    st.session_state[SessionKey.SELECTED_METRICS],
                    profile_name
                )
                st.download_button(
                    "", 
                    data=zipfile, 
                    file_name=f"{profile_name}.zip",
                    mime="application/zip",
                    type="primary", disabled=profile_name.strip() == "",
                    icon=":material/download:",
                    help="download profile"
                )
