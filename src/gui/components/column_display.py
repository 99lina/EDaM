import streamlit as st

import itertools
from collections.abc import Iterable

from src.edam.profile.profiles import ColumnProfile, SimpleColumnProfile, TransformationProfile, DataProfile
from src.edam.schema.schema import FeaturedType
from ..single_dataset.representations import MetricRepresentation, _BUILTIN_REPRESENTATIONS, RepresentationRegistry
from .cached import cached_find_matching_representations, cached_assign_plot_groups
from ..single_dataset.helpers import groupby
from .helpers import representation_selection_key, transformation_selection_key
from .dataprofile_filter import update_selections
from .session_state import SessionKey

from ..single_dataset.row import ForeignID


_FEATURED_TYPE_COLORS = dict(zip(FeaturedType, itertools.cycle(["red", "orange", "yellow", "blue", "green", "violet", "gray"])))

def _make_selection_group(title: str, options: Iterable[MetricRepresentation], column: str, transformation: str):
    default = filter(lambda o: o.visuals.is_default, options)
    return st.segmented_control(
        title,
        options,
        default=list(default),
        selection_mode="multi",
        width="stretch",
        format_func=lambda spec: spec.visuals.label,
        key=representation_selection_key(column, transformation, title),
        persist_state="session"
    )

def _make_selection_popover(transformation: TransformationProfile, colname: str) -> RepresentationRegistry:
    with st.popover("metrics"):
        matching_representations = cached_find_matching_representations(_BUILTIN_REPRESENTATIONS, transformation, colname, transformation.name).registry
        groups = [
            _make_selection_group(group, list(elements), colname, transformation.name)
            for group, elements 
            in groupby(matching_representations, lambda r: r.visuals.switch_group)
        ]
    return RepresentationRegistry(list(itertools.chain.from_iterable(groups)))

def _make_toolbar(column: ColumnProfile, featured_type: FeaturedType, init_type: str, syntax_pattern: str) -> tuple[TransformationProfile, RepresentationRegistry]:
    with st.container(horizontal=True, vertical_alignment="center"):
        st.subheader(column.name)
        st.badge(init_type)
        st.badge(featured_type, color=_FEATURED_TYPE_COLORS[featured_type])
        st.badge(syntax_pattern)
        if isinstance(column, SimpleColumnProfile):
            transformation = column.transformation
        else:
            transformation_name = st.pills("transformation", column.transformations.keys(), label_visibility="collapsed", required=True, default="identity", key=transformation_selection_key(column.name))
            transformation = column[transformation_name]
        selections = _make_selection_popover(transformation, column.name)
        update_selections(selections, st.session_state[SessionKey.SELECTED_METRICS], column.name, transformation.name)
        return transformation, selections


def _make_display(data: DataProfile, column: str, transformation: str, selected_metrics: Iterable[MetricRepresentation]):
    plot_groups, mapping = cached_assign_plot_groups(data, _BUILTIN_REPRESENTATIONS, column, transformation)
    selection = [ForeignID(m.id, column, transformation) for m in selected_metrics]
    row_keys = list(itertools.chain.from_iterable(
        mapping[rowid] for rowid in selection
    ))
    with st.container():
        for pg in plot_groups:
            [chart, chart_nonempty], tables = pg.render(row_keys)
            if chart_nonempty:
                st.altair_chart(chart)
            for t in tables:
                st.dataframe(t)

@st.fragment
def make_column_container(column: ColumnProfile, data: DataProfile):
    featured_type = data.schema.properties[column.name].featured_type
    init_type = data.schema.properties[column.name].init_type
    syntax_pattern = data.schema.properties[column.name].syntax_pattern

    with st.container():
        transformation, selections = _make_toolbar(column, featured_type, init_type, syntax_pattern)
        _make_display(data, column.name, transformation.name, selections)
        