from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Callable, Any, ClassVar
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime
import itertools

import pandas as pd

from .visuals import Visuals
from .dependencies import DependencyMap

from .render_funcs import *

_ROWID_GENERATOR = itertools.count()
def _generate_rowid() -> int:
    return next(_ROWID_GENERATOR)

@dataclass(frozen=True, order=True)
class ForeignID:
    representation_id: int
    column: str
    transformation: str



@dataclass(frozen=True)
class Row(ABC):
    graph_group: str
    label: str
    foreign_id: ForeignID = field(repr=False)
    id: int = field(init=False, default_factory=_generate_rowid)
    is_tabular: ClassVar[bool] = False

    @property
    def representation_id(self) -> int:
        return self.foreign_id.representation_id

    def to_record(self) -> dict:
        return {**self._metadata_record(), **self._data_record()}

    def _metadata_record(self) -> dict:
        return {
            "rowid": self.id,
            "label": self.label
        }
    
    @abstractmethod
    def _data_record(self) -> dict:
        ...

    @staticmethod
    def renderer(filtered_data: pd.DataFrame, all_data: pd.DataFrame):
        raise NotImplementedError
    
@dataclass(frozen=True)
class VLineRow(Row):
    value: float

    @classmethod
    def default_extractor(cls, data: DependencyMap, visuals: Visuals, id: ForeignID) -> list[VLineRow]:
        return [cls(
            visuals.graph_group,
            visuals.label,
            id,
            data["value"]
        )]

    def _data_record(self):
        return {"x": self.value}

    @staticmethod
    def renderer(filtered_data: pd.DataFrame, all_data: pd.DataFrame):
        return render_vlines(filtered_data, all_data)

@dataclass(frozen=True)
class TableRow(Row):
    value: Any
    is_tabular: ClassVar[bool] = True

    @classmethod
    def default_extractor(cls, data: DependencyMap, visuals: Visuals, id: ForeignID) -> list[TableRow]:
        return [cls(
            visuals.graph_group,
            visuals.label_long,
            id,
            data["value"]
        )]

    def _data_record(self) -> dict:
        return {"value": str(self.value)}


@dataclass(frozen=True)
class RangeRow(Row):
    center: float
    deviation: float
    is_left: bool

    @classmethod
    def default_extractor(cls, data: DependencyMap, visuals: Visuals, foreign_id: ForeignID) -> list[RangeRow]:
        return [
            cls(
                visuals.graph_group,
                visuals.label,
                foreign_id,
                data["center"],
                data["deviation"],
                is_left=True
            ),
            cls(
                visuals.graph_group,
                visuals.label,
                foreign_id,
                data["center"],
                data["deviation"],
                is_left=False
            )
        ]

    def _data_record(self) -> dict:
        match self.is_left:
            case True: x_adj = self.center - self.deviation
            case False: x_adj = self.center + self.deviation
        return {
            "label": self.label,
            "center": self.center,
            "deviation": self.deviation,
            "x_adj": x_adj,
            "is_left": self.is_left
        }

    @staticmethod
    def renderer(filtered_data: pd.DataFrame, all_data: pd.DataFrame):
        return render_range(filtered_data, all_data)


@dataclass(frozen=True)
class HistogramRow(Row):
    x_start: float
    x_end: float
    height: float

    @classmethod
    def default_extractor(cls, data: DependencyMap, visuals: Visuals, id: ForeignID) -> list[HistogramRow]:
        hist_data = data["histogram"]

        bin_start = hist_data["edges"][:-1]
        bin_end = hist_data["edges"][1:]
        height = hist_data["bins"]

        return [
            cls(visuals.graph_group, visuals.label, id, b_s, b_e, h)
            for b_s, b_e, h in zip(bin_start, bin_end, height)
        ]

    def _data_record(self) ->  dict:
        return {
            "x_start": self.x_start, 
            "x_end": self.x_end, 
            "height": self.height
        }

    @staticmethod
    def renderer(filtered_data: pd.DataFrame, all_data: pd.DataFrame):
        return render_hist(filtered_data, all_data)

@dataclass(frozen=True)
class BarChartRow(Row):
    value: str
    height: float

    @classmethod
    def default_extractor(cls, data: DependencyMap, visuals: Visuals, id: ForeignID) -> list[BarChartRow]:
        bar_data = data["barchart"]

        return [
            cls(visuals.graph_group, visuals.label, id, value, height)
            for value, height in bar_data.items()
        ]

    def _data_record(self) -> dict:
        return {
            "value": self.value,
            "height": self.height
        }

    @staticmethod
    def renderer(filtered_data: pd.DataFrame, all_data: pd.DataFrame):
        return render_categorical_distribution(filtered_data, all_data)

@dataclass(frozen=True)
class DateHistogramRow(Row):
    x_start: str
    x_end: str
    height: float

    @classmethod
    def default_extractor(cls, data: DependencyMap, visuals: Visuals, id: ForeignID) -> list[DateHistogramRow]:
        hist_data = data["histogram"]

        bin_start = hist_data["edges"][:-1]
        bin_end = hist_data["edges"][1:]
        height = hist_data["bins"]

        return [
            cls(visuals.graph_group, visuals.label, id, b_s, b_e, h)
            for b_s, b_e, h in zip(bin_start, bin_end, height)
        ]

    def _data_record(self) ->  dict:
        return {
            "x_start": pd.Timestamp.fromisoformat(self.x_start), 
            "x_end": pd.Timestamp.fromisoformat(self.x_end), 
            "height": self.height
        }

    @staticmethod
    def renderer(filtered_data: pd.DataFrame, all_data: pd.DataFrame):
        return render_date_hist(filtered_data, all_data)


@dataclass(frozen=True)
class DateVLineRow(Row):
    value: str

    @classmethod
    def default_extractor(cls, data: DependencyMap, visuals: Visuals, id: ForeignID) -> list[DateVLineRow]:
        return [cls(
            visuals.graph_group,
            visuals.label,
            id,
            data["value"]
        )]

    def _data_record(self):
        return {"x": pd.Timestamp.fromisoformat(self.value)}

    @staticmethod
    def renderer(filtered_data: pd.DataFrame, all_data: pd.DataFrame):
        return render_date_vlines(filtered_data, all_data)