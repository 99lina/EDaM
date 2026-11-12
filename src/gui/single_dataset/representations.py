from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
from collections.abc import Iterator
import uuid

from .row import *
from .visuals import Visuals
from .dependencies import DependencyMap
from .extractors import * 
from .render import *

from src.edam.profile.profiles import TransformationProfile


    
@dataclass(frozen=True, eq=True)
class MetricRepresentation[T: Row]:
    dependencies: DependencyMap = field(hash=False)
    extractor: Callable[[DependencyMap, Visuals, ForeignID], list[T]] = field(hash=False)
    visuals: Visuals = field(hash=False)
    id: int = field(default_factory=lambda: uuid.uuid4().int, init=False, hash=True)

    def get_rows(self, data: TransformationProfile, column: str) -> list[T]:
        if self.can_be_displayed(data):
            row_id = ForeignID(self.id, column, data.name)
            return self.extractor(self.dependencies, self.visuals, row_id)
        else:
            return []

    def can_be_displayed(self, data: TransformationProfile) -> bool:
        self.dependencies.set_target(data)
        return self.dependencies.is_complete()


@dataclass(frozen=True)
class RepresentationOptions[T: Row]:
    _options: list[MetricRepresentation]

    @classmethod
    def from_single_option(
        cls, 
        dependencies: DependencyMap,
        extractor: Callable[[DependencyMap, Visuals, ForeignID], list[T]],
        visuals: Visuals
    ) -> RepresentationOptions:
        return cls([
            MetricRepresentation(dependencies, extractor, visuals)
        ])

    def first_displayable(self, data: TransformationProfile) -> MetricRepresentation | None:
        for o in self._options:
            if o.can_be_displayed(data):
                return o
        return None

    def get_rows(self, data: TransformationProfile, column: str) -> list[T]:
        for o in self._options:
            if o.can_be_displayed(data):
                return o.get_rows(data, column)
        return []


_BUILTIN_REPRESENTATIONS: list[RepresentationOptions] = [
    RepresentationOptions.from_single_option(
        DependencyMap(value="min"),
        VLineRow.default_extractor,
        Visuals("Minimum", "Locations")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="max"),
        VLineRow.default_extractor,
        Visuals("Maximum", "Locations")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="quantiles"),
        quantiles_extractor,
        Visuals("Quantiles", "Locations")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="mean"),
        VLineRow.default_extractor,
        Visuals("Mean", "Centrality", is_default=True)
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="median"),
        VLineRow.default_extractor,
        Visuals("Median", "Centrality", is_default=True)
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="mode"),
        TableRow.default_extractor,
        Visuals("Mode", "Centrality")
    ),
    RepresentationOptions([
        MetricRepresentation(
            DependencyMap(deviation="sd", center="mean"),
            RangeRow.default_extractor,
            Visuals("SD", "Spread", is_default=True),
        ),
        MetricRepresentation(
            DependencyMap(center="mean"),
            TableRow.default_extractor,
            Visuals("SD", "Spread", is_default=True),
        )
    ]),
    RepresentationOptions([
        MetricRepresentation(
            DependencyMap(deviation="mad", center="mean"),
            RangeRow.default_extractor,
            Visuals("MAD", "Spread", is_default=True),
        ),
        MetricRepresentation(
            DependencyMap(center="mean"),
            TableRow.default_extractor,
            Visuals("MAD", "Spread", is_default=True),
        )
    ]),
    RepresentationOptions([
        MetricRepresentation(
            DependencyMap(deviation="iqr", center="mean"),
            RangeRow.default_extractor,
            Visuals("IQR", "Spread", is_default=True),
        ),
        MetricRepresentation(
            DependencyMap(center="mean"),
            TableRow.default_extractor,
            Visuals("IQR", "Spread", is_default=True),
        )
    ]),
    RepresentationOptions.from_single_option(
        DependencyMap(value="data_range"),
        TableRow.default_extractor,
        Visuals("Range", "Spread")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap("histogram"),
        HistogramRow.default_extractor,
        Visuals("Histogram", "Other", is_default=True)
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="skewness"),
        TableRow.default_extractor,
        Visuals("Skewness", "Other")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="kurtosis"),
        TableRow.default_extractor,
        Visuals("Kurtosis", "Other")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="num_categories"),
        TableRow.default_extractor,
        Visuals("Number of categories", "General", is_default=True)
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="mode_cat"),
        TableRow.default_extractor,
        Visuals("Mode", "General", is_default=True)
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(barchart="frequency_dist"),
        BarChartRow.default_extractor,
        Visuals("Distribution", "General")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="min_length"),
        VLineRow.default_extractor,
        Visuals("Minimum", "Length")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="max_length"),
        VLineRow.default_extractor,
        Visuals("Maximum", "Length")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="avg_length"),
        VLineRow.default_extractor,
        Visuals("Mean", "Length", is_default=True)
    ),
    RepresentationOptions.from_single_option(                
        DependencyMap(histogram="length_dist"),
        HistogramRow.default_extractor,
        Visuals("Distribution", "Length", is_default=True)
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="num_unique_strings"),
        TableRow.default_extractor,
        Visuals("Unique strings", "Other")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="min_length_arr"),
        TableRow.default_extractor,
        Visuals("Minimum", "Length")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="max_length_arr"),
        TableRow.default_extractor,
        Visuals("Maximum", "Length")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="avg_length_arr"),
        TableRow.default_extractor,
        Visuals("Mean", "Length")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="min_count"),
        TableRow.default_extractor,
        Visuals("Minimum", "Count")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="max_count"),
        TableRow.default_extractor,
        Visuals("Maximum", "Count")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="avg_count"),
        TableRow.default_extractor,
        Visuals("Mean", "Count")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="min_value"),
        TableRow.default_extractor,
        Visuals("Minimum", "Values")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="max_value"),
        TableRow.default_extractor,
        Visuals("Maximum", "Values")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="avg_value"),
        TableRow.default_extractor,
        Visuals("Mean", "Values")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="outlier_lof"),
        n_outliers_extractor,
        Visuals("LOF", "Outlier Count", "outliers")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="outlier_dbscan"),
        n_outliers_extractor,
        Visuals("DBSCAN", "Outlier Count", "outliers")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="outlier_iqr"),
        n_outliers_extractor,
        Visuals("IQR", "Outlier Count", "outliers")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="outlier_zscore"),
        n_outliers_extractor,
        Visuals("z-score", "Outlier Count", "outliers")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="min_date"),
        DateVLineRow.default_extractor,
        Visuals("Minimum", "Values")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="max_date"),
        DateVLineRow.default_extractor,
        Visuals("Maximum", "Values")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="mean_date"),
        DateVLineRow.default_extractor,
        Visuals("Mean", "Centrality")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="median_date"),
        DateVLineRow.default_extractor,
        Visuals("Median", "Centrality")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(value="mode_date"),
        TableRow.default_extractor,
        Visuals("Mode", "Centrality")
    ),
    RepresentationOptions.from_single_option(
        DependencyMap(histogram="histogram_date"),
        DateHistogramRow.default_extractor,
        Visuals("Histogram", "Other")
    )
]


@dataclass(frozen=True)
class RepresentationRegistry:
    registry: list[MetricRepresentation]

    @classmethod
    def from_displayable(
        cls, 
        options: list[RepresentationOptions], 
        transformation: TransformationProfile
    ) -> RepresentationRegistry:
        representations = map(lambda o: o.first_displayable(transformation), options)
        return cls([
            repr for repr in representations
            if repr is not None
        ])

    def filter_default(self) -> RepresentationRegistry:
        return type(self)(
            [repr for repr in self.registry if repr.visuals.is_default]
        )

    def get_requirements(self) -> Iterator[str]:
        return itertools.chain.from_iterable(
            repr.dependencies.dependency_keys() for repr in self.registry
        )

    def __iter__(self) -> Iterator[MetricRepresentation]:
        return iter(self.registry)