import streamlit as st

from .session_state import SessionKey
from ..multi_dataset.compare_embeddings import *

@st.cache_data
def _load_plots():
    datasets = st.session_state[SessionKey.UPLOADED_PROFILES]
    emb_df1, name_1 = load_embeddings(datasets[0][".parquet"])
    emb_df2, name_2 = load_embeddings(datasets[1][".parquet"])

    profile1, name_1 = load_profile(datasets[0][".json"])
    profile2, name_2 = load_profile(datasets[1][".json"])

    comp_matrix_type = compare_profiles_type(profile1, profile2)
    comp_matrix_stat = compare_profiles(profile1, profile2)
    cos_matrix = calc_cos_similarity(emb_df1, emb_df2)
    comp_matrix_syntax = compare_profiles_syntax(profile1, profile2)

    type_simi = generate_heat_matrix_alt(comp_matrix_type, name_1, name_2)
    profile_comparison = generate_heat_matrix_alt(comp_matrix_stat, name_1, name_2 )
    embeddings_comparison = generate_heat_matrix_alt(cos_matrix, name_1, name_2)
    syn_similarity = generate_heat_matrix_alt(comp_matrix_syntax, name_1, name_2)

    _, matches = combine_and_match(comp_matrix_type, comp_matrix_stat, cos_matrix, comp_matrix_syntax, name_1, name_2)

    return matches, type_simi, profile_comparison, embeddings_comparison, syn_similarity


def make_comparison_page():
    matches, type_simi, profile_comparison, embeddings_comparison, syn_simi = _load_plots()


    st.space("medium")

    # --------------------------------------------------
    # Mapping overview
    # --------------------------------------------------
    st.subheader("Results of matching columns based on similarity Analysis")

    # Convert results to DataFrame if necessary
    if not isinstance(matches, pd.DataFrame):
        matches = pd.DataFrame(matches)

    st.dataframe(
        matches,
        hide_index=True,
        width=500
    )

    st.space("large")

    # --------------------------------------------------
    # Charts
    # --------------------------------------------------
    st.subheader("Visualization of similarity matrices")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Data type Comparison")
        st.altair_chart(
            type_simi,
            height=500,
            use_container_width=True
        )

        st.markdown("##### Statistics Comparison")
        st.altair_chart(
            profile_comparison,
            height=500,
            use_container_width=True
        )

    with col2:
        st.markdown("##### Semantic Embeddings Comparison")
        st.altair_chart(
            embeddings_comparison,
            height=500,
            use_container_width=True
        )


        st.markdown("##### Syntax Comparison")
        st.altair_chart(
            syn_simi,
            height=500,
            use_container_width=True
        )

def make_comparison_toolbar():
    outer = st.bottom.container(horizontal_alignment="center")
    inner = outer.container(horizontal=True, vertical_alignment="center", border=True, width="content")
    if inner.button("", icon=":material/home:", help="back to home", width="content"):
        del st.session_state[SessionKey.UPLOADED_PROFILES]
        st.rerun()
