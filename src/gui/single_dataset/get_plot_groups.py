import itertools
from collections.abc import Iterable

import pandas as pd

from .helpers import groupby
from .representations import MetricRepresentation, RepresentationOptions, ForeignID
from .render import PlotGroup, PlotData, AltairPlot, AltairVConcatPlot
from .row import Row
from src.edam.profile.profiles import DataProfile, TransformationProfile


def assign_plot_groups(
    data: DataProfile,
    representations: list[RepresentationOptions] | list[MetricRepresentation],
    column: str,
    transformation: str
) -> tuple[list[PlotGroup], dict[ForeignID, list[int]]]:
    rows = get_all_rows(data, representations, column, transformation)
    rowid_mapping = map_represenation_to_rowid(rows)
    groups = [
        build_group(graph_group, grouped_rows)
        for graph_group, grouped_rows 
        in groupby(rows, lambda r: r.graph_group)
    ]
    return groups, rowid_mapping


def get_all_rows(
    data: DataProfile,
    representations: list[RepresentationOptions] | list[MetricRepresentation],
    column: str,
    transformation: str
) -> list[Row]:
    rows = itertools.chain.from_iterable(
        repr.get_rows(data.column_metrics.children[column][transformation], column)
        for repr in representations
    )
    return list(rows)

def map_represenation_to_rowid(rows: list[Row]) -> dict[ForeignID, list[int]]:
    return {
        row_id: [r.id for r in grouped_rows]
        for row_id, grouped_rows in groupby(rows, lambda r: r.foreign_id)
    }

def build_group(graph_group: str, rows: Iterable[Row]):
    tables, plots = [], []
    for row_type, grouped_rows in groupby(rows, lambda r: type(r)):
        if row_type.is_tabular:
            tables.append(PlotData.from_rows(grouped_rows))
        else:
            plots.append(
                AltairPlot(
                    PlotData.from_rows(grouped_rows), row_type.renderer
                )
            )
    return PlotGroup(AltairVConcatPlot(plots), tables, graph_group)