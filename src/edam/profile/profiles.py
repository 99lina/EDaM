from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from copy import deepcopy
from typing import Self, Any, override
from collections.abc import Iterator, Iterable
from datetime import datetime

import itertools
import json

from ..schema.schema import Schema, Property
from ..helpers import round, normalize_types
from .filter import ProfileFilter


@dataclass
class DataProfile:
    """"This data class represents a data profile. 
    
    It can be created directly via a 
    constructor or from a JSON file. It can also be exported as a JSON file.
    """
    schema: Schema 
    column_metrics: ColumnMetricsProfile
    general_metrics: GeneralMetricsProfile
    metadata: Metadata

    def to_dict(self, compact: bool = True) -> dict[str, Any]:
        if compact:
            return {
                "PROPERTIES": self.column_metrics.to_dict(self.schema),
                "GENERAL/META": {
                    "GENERAL": self.general_metrics.to_dict(),
                    "METADATA": self.metadata.to_dict()
                }
            }
        else:
            return {
                "SCHEMA": self.schema.to_dict(),
                "PROPERTIES": self.column_metrics.to_dict(),
                "METADATA": self.metadata.to_dict()
            }


    def filter(self, filter: ProfileFilter) -> DataProfile:
        return type(self)(
            self.schema,
            self.column_metrics.filter(filter),
            self.general_metrics,
            self.metadata
        )

    def simplify(self) -> DataProfile:
        return DataProfile(
            self.schema,
            self.column_metrics.simplify(),
            self.general_metrics,
            self.metadata
        )

    def normalize(self) -> DataProfile:
        return DataProfile(
            self.schema,
            self.column_metrics.normalize(),
            self.general_metrics.normalize(),
            self.metadata
        )

    def round(self, precision: int) -> DataProfile:
        return DataProfile(
            self.schema,
            self.column_metrics.round(precision),
            self.general_metrics.round(precision),
            self.metadata
        )

    def to_json(self, output_path: str | Path, compact: bool = True) -> None:
        output_path = Path(output_path)
        output_path.write_text(
            json.dumps(
                self.normalize().to_dict(compact=compact), 
                ensure_ascii=False, 
                indent=4
            )
        )

    @classmethod
    def from_dict(cls, data: dict, simple: bool = True) -> DataProfile:
        return cls(
            Schema.from_dict(data["PROPERTIES"]),
            ColumnMetricsProfile.from_dict(data["PROPERTIES"], simple),
            GeneralMetricsProfile.from_dict(data["GENERAL/META"]["GENERAL"]),
            Metadata.from_dict(data["GENERAL/META"]["METADATA"]),
        )

    @classmethod
    def from_json(cls, file: Path | str, alternative_form: bool = True) -> Self:
        file = Path(file)
        content = file.read_text()
        json_data = json.loads(content)
        raise NotImplementedError


@dataclass
class Metadata:
    filename: str = ""
    hash: str = ""
    exec_start: datetime = field(default_factory=datetime.now)
    exec_end: datetime | None = None

    @property
    def execution_time(self) -> float:
        if self.exec_end is None:
            return 0.0
        return (self.exec_end - self.exec_start).total_seconds()

    
    def to_dict(self) -> dict[str, str | float | None]:
        return {
            "filename": self.filename, "hash": self.hash,
            "start": self.exec_start.isoformat(), 
            "end": self.exec_end.isoformat() if self.exec_end is not None else None,
            "execution_time": self.execution_time
        }

    @classmethod
    def from_dict(cls, data: dict) -> Metadata:
        return cls(
            data["filename"],
            data["hash"],
            datetime.fromisoformat(data["start"]),
            datetime.fromisoformat(data["end"])
        )

    def set_end(self):
        self.exec_end = datetime.now()


@dataclass(frozen=True)
class GeneralMetricsProfile:
    children: dict[str, MetricResult]

    @classmethod
    def from_list(cls, results: Iterable[MetricResult]) -> GeneralMetricsProfile:
        return cls({result.metric_key: result for result in results})

    @classmethod
    def from_dict(cls, data: dict) -> GeneralMetricsProfile:
        return cls({
            metric_name: MetricResult(metric_name, information, False)
            for metric_name, information
            in data.items()
        })

    def round(self, precision: int) -> GeneralMetricsProfile:
        return type(self).from_list(
            result.round(precision) for result in self.children.values()
        )

    def normalize(self) -> GeneralMetricsProfile:
        return type(self).from_list(
            result.normalize() for result in self.children.values()
        )

    def to_dict(self) -> dict[str, Any]:
        return {result.metric_key: result.data for result in self.children.values()}


@dataclass(frozen=True)
class ColumnMetricsProfile:
    """Das Gesamtprofil des Datensatzes."""
    children: dict[str, ColumnProfile] = field(default_factory=dict)

    @classmethod
    def from_list(cls, profiles: Iterable[ColumnProfile]) -> ColumnMetricsProfile:
        return cls(
            {profile.name: profile for profile in profiles}
        )

    def to_dict(self, schema: Schema | None = None) -> dict[str, Any]:
        if schema is not None:
            return {col.name: col.to_dict(schema.properties[col.name]) for col in self.children.values()}
        else:
            return {col.name: col.to_dict() for col in self.children.values()}
        
    @classmethod
    def from_dict(cls, data: dict, simple: bool = True) -> ColumnMetricsProfile:
        if simple:
            return cls({
                name: SimpleColumnProfile.from_dict(information["STATISTICS"], name)
                for name, information
                in data.items()
            })
        else:
            return cls({
                name: ColumnProfile.from_dict(information["STATISTICS"], name)
                for name, information
                in data.items()
            })

    def simplify(self) -> ColumnMetricsProfile:
        return type(self).from_list(
            SimpleColumnProfile.from_column_profile(col) 
            for col in self
        )

    def normalize(self) -> ColumnMetricsProfile:
        return type(self).from_list(
            col.normalize() for col in self.children.values()
        )

    def round(self, precision: int) -> ColumnMetricsProfile:
        return type(self).from_list(
            col.round(precision) for col in self.children.values()
        )

    def filter(self, filter: ProfileFilter) -> ColumnMetricsProfile:
        if isinstance(filter, dict):
            return type(self).from_list(
                self.children[key].filter(subfilter) 
                for key, subfilter in filter.items()
            )
        else:
            return self

    def __iter__(self) -> Iterator[ColumnProfile]:
        return iter(self.children.values())


@dataclass(frozen=True)
class ColumnProfile:
    """Profilergebnisse für eine spezifische Spalte."""

    name: str
    children: dict[str, TransformationProfile]


    @classmethod
    def from_list(cls, name: str, children: Iterable[TransformationProfile]) -> Self:
        return cls(
            name,
            {child.name: child for child in children}
        )

    @classmethod
    def from_dict(cls, data: dict, col_name: str) -> ColumnProfile:
        return cls(
            col_name,
            {
                trans_name: TransformationProfile.from_dict(metrics, trans_name)
                for trans_name, metrics
                in data.items()
            }
        )
    

    def normalize(self) -> Self:
        return type(self).from_list(
            self.name,
            [child.normalize() for child in self.children.values()]
        )

    def round(self, precision: int) -> Self:
        return type(self).from_list(
            self.name,
            [child.round(precision) for child in self.children.values()]
        )

    
    def filter(self, filter: ProfileFilter) -> ColumnProfile:
        if isinstance(filter, dict):
            return type(self).from_list(
                self.name,
                (
                    self.children[key].filter(subfilter) 
                    for key, subfilter in filter.items()
                )
            )
        else:
            return self
        
    def to_dict(self, property: Property | None = None) -> dict:
        statistics = {child.name: child.to_dict() for child in self.children.values()}
        if property is not None:
            d = {
                **property.to_dict(),
                "STATISTICS": statistics
                }
            # move STATISTICS to index 2 in dict keys
            keys = list(d.keys())
            keys.insert(2, keys.pop())
            return {key: d[key] for key in keys}
        else:
            return statistics

    @property
    def transformations(self) -> dict[str, TransformationProfile]:
        return self.children

    def __getitem__(self, key: str) -> TransformationProfile:
        return self.children[key]

    def __iter__(self) -> Iterator[TransformationProfile]:
        return iter(self.children.values())


@dataclass(frozen=True)
class SimpleColumnProfile(ColumnProfile):
    def _post_init__(self):
        if len(self.transformations) != 1:
            raise ValueError("SimpleColumnProfile should have exactly one child")

    @classmethod
    def from_column_profile(cls, profile: ColumnProfile) -> SimpleColumnProfile:
        transformation = TransformationProfile.from_list(
            "_UNION", itertools.chain.from_iterable(profile)
        )
        return cls.from_list(profile.name, [transformation])
        
    @property
    def transformation(self) -> TransformationProfile:
        return next(iter(
            self.transformations.values()
        ))
    
    @override
    def to_dict(self, property: Property | None = None) -> dict:
        statistics = self.transformation.to_dict()
        if property is not None:
            d = {
                **property.to_dict(),
                "STATISTICS": statistics
                }
            # move STATISTICS to index 2 in dict keys
            keys = list(d.keys())
            keys.insert(2, keys.pop())
            return {key: d[key] for key in keys}
        else:
            return statistics

    @override
    @classmethod
    def from_dict(cls, data: dict, col_name: str) -> SimpleColumnProfile:
        return cls(
            col_name,
            {"_UNION": TransformationProfile.from_dict(data, "_UNION")},
        )


@dataclass(frozen=True)
class TransformationProfile:
    """Ergebnisse von Metriken auf einer Spalte (entweder original/identity oder transformiert)."""
    name: str
    children: dict[str, MetricResult]


    @classmethod
    def from_list(cls, name: str, children: Iterable[MetricResult]) -> TransformationProfile:
        return cls(
            name, {child.name: child for child in children}
        )

    @classmethod
    def from_dict(cls, data: dict, trans_name: str) -> TransformationProfile:
        return cls(
            trans_name,
            {
                metric_name: MetricResult(metric_name, information, False)
                for metric_name, information
                in data.items()
            }
        )

    def normalize(self) -> TransformationProfile:
        return type(self).from_list(
            self.name, 
            [child.normalize() for child in self.children.values()]
        )

    def round(self, precision: int) -> TransformationProfile:
        return type(self).from_list(
            self.name,
            [child.round(precision) for child in self.children.values()]
        )


    def filter(self, filter: ProfileFilter) -> TransformationProfile:
        if isinstance(filter, dict):
            return type(self).from_list(
                self.name,
                (self.children[key] for key in filter)
            )
        else:
            return self
        

    def to_dict(self) -> dict:
        return {child.name: child.to_dict() for child in self.children.values()}

    @property
    def results(self) -> dict[str, MetricResult]:
        return self.children

    def __getitem__(self, key: str) -> MetricResult:
        return self.children[key]

    def __iter__(self) -> Iterator[MetricResult]:
        return iter(self.children.values())

    def __contains__(self, item):
        return item in self.children


@dataclass(frozen=True)
class MetricResult:
    """Das Einzelergebnis einer Metrik (z.B. Mean, Missing-Count)."""
    name: str
    data: Any
    is_roundable: bool

    @property
    def metric_key(self):
        return self.name

    def round(self, precision: int) -> MetricResult:
        if self.is_roundable:
            return MetricResult(
                self.metric_key, 
                round(self.data, precision), 
                False
            )
        return self

    def normalize(self) -> MetricResult:
        return MetricResult(
            self.metric_key,
            normalize_types(self.data),
            self.is_roundable
        )

    def to_dict(self) -> Any:
        return self.data
