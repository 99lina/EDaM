from __future__ import annotations
from collections.abc import Iterable
from dataclasses import dataclass
import time

import altair as alt
import pandas as pd

from ..single_dataset.row import *


@dataclass(frozen=True)
class PlotData[R: Row]:
    _data: pd.DataFrame

    @classmethod
    def from_rows(cls, rows: Iterable[R]) -> PlotData:
        records = map(Row.to_record, rows)
        data = pd.DataFrame.from_records(records, index="rowid")
        return cls(data)

    def filter_data(self, keys: list[int]) -> pd.DataFrame:
        existing_keys = self._data.index.intersection(keys)
        return self._data.loc[existing_keys]

    @property
    def all_data(self) -> pd.DataFrame:
        return self._data


@dataclass(frozen=True)
class AltairPlot:
    _data: PlotData
    _renderer: Callable[[pd.DataFrame, pd.DataFrame], alt.Chart]

    def render(self, keys: list[int]) -> tuple[alt.Chart, bool]:
        plot_data = self._data.filter_data(keys)
        return self._renderer(plot_data, self._data.all_data), len(plot_data) > 0

@dataclass(frozen=True)
class AltairVConcatPlot:
    subplots: list[AltairPlot] = field(default_factory=list)

    def render(self, keys: list[int]) -> tuple[alt.VConcatChart, bool]:
        charts = [chart.render(keys) for chart in self.subplots]
        nonempty_charts = [chart for chart, nonempty in charts if nonempty]
        return alt.vconcat(*nonempty_charts).resolve_scale(x="shared"), len(nonempty_charts) > 0

@dataclass(frozen=True)
class PlotGroup:
    plot: AltairVConcatPlot = field(default_factory=AltairVConcatPlot)
    tables: list[PlotData] = field(default_factory=list)
    group_metadata: str = ""

    def render(self, keys: list[int]) -> tuple[tuple[alt.VConcatChart, bool], list[pd.DataFrame]]:
        chart = self.plot.render(keys)
        filtered_tables = [
            table for t in self.tables 
            if len(table:=t.filter_data(keys)) > 0
        ]
        return chart, filtered_tables