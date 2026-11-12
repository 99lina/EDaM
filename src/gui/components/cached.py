import streamlit as st

from ..single_dataset.get_plot_groups import assign_plot_groups
from ..single_dataset.representations import MetricRepresentation, RepresentationOptions, RepresentationRegistry
from src.edam.profile.profiles import DataProfile, TransformationProfile
from src.edam.config.config import EdamConfig
from src.edam.profile.builder import DataProfileBuilder




@st.cache_data(hash_funcs={EdamConfig: hash})
def get_edam_output(config: EdamConfig) -> DataProfile:
    return (
        DataProfileBuilder
            .build_from_config(config)
            .round(config.precision)
            .normalize()
            .simplify()
    )

@st.cache_data
def cached_assign_plot_groups(
    _data: DataProfile, 
    _representations: list[RepresentationOptions] | list[MetricRepresentation], 
    column: str, 
    transformation: str
):
    return assign_plot_groups(_data, _representations, column, transformation)

@st.cache_data
def cached_find_matching_representations(
    _representations: list[RepresentationOptions], 
    _transformation: TransformationProfile, 
    column_name: str, 
    transformation_name: str
):
    return RepresentationRegistry.from_displayable(_representations, _transformation)

@st.cache_data
def cached_data_profile_to_dict(hash: str, _data: DataProfile):
    return _data.to_dict(compact=True)