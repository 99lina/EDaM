import streamlit as st
from src.edam.profile.profiles import ProfileFilter, DataProfile, ColumnMetricsProfile

from ..single_dataset.representations import RepresentationOptions, RepresentationRegistry, MetricRepresentation
from .cached import cached_find_matching_representations


type RepresentationSelection = dict[str, dict[str, RepresentationRegistry]]

def setup_selections(representations: list[RepresentationOptions], profile: ColumnMetricsProfile) -> RepresentationSelection:
    return {
        column.name: {
            transformation.name: 
            cached_find_matching_representations(
                representations, transformation, 
                column.name, transformation.name
            ).filter_default()
            for transformation in column
        }
        for column in profile
    }

def update_selections(representations: RepresentationRegistry, selection: RepresentationSelection, col_name: str, trans_name: str):
    selection[col_name][trans_name] = representations

def build_filter(selection: RepresentationSelection) -> ProfileFilter:
    return {
        column_name: {
            trans_name: 
            dict.fromkeys(representations.get_requirements())
            for trans_name, representations 
            in column_transformations.items()
        }
        for column_name, column_transformations 
        in selection.items()
    }