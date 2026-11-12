from collections.abc import Iterable

import pandas as pd

from ..schema.schema import FeaturedType
from .metrics import Metric
from .datafunctions import *


_builtin_metrics = [
    Metric("mean", pd.Series.mean, FeaturedType.NUMERIC, is_default=True),
    Metric("median", pd.Series.median, FeaturedType.NUMERIC, is_default=True),
    Metric("mode", lambda series: series.mode().to_numpy(), FeaturedType.NUMERIC),

    Metric("sd", pd.Series.std, FeaturedType.NUMERIC, is_default=True),
    Metric("iqr", iqr, FeaturedType.NUMERIC, is_default=True),
    Metric("mad", mad, FeaturedType.NUMERIC),
    Metric("data_range", data_range, FeaturedType.NUMERIC),

    Metric("quantiles", quantiles, FeaturedType.NUMERIC, is_default=True),
    Metric("min", pd.Series.min, FeaturedType.NUMERIC),
    Metric("max", pd.Series.max, FeaturedType.NUMERIC),
    Metric("range", min_max, FeaturedType.NUMERIC),

    Metric("skewness", pd.Series.skew, FeaturedType.NUMERIC),
    Metric("kurtosis", pd.Series.kurt, FeaturedType.NUMERIC),

    Metric("histogram", histogram, FeaturedType.NUMERIC, is_default=True),

    Metric("num_categories", lambda series: series.nunique(), FeaturedType.CATEGORICAL),
    Metric("frequency_dist", lambda series: series.value_counts(), FeaturedType.CATEGORICAL, is_default=True),
    Metric("mode_cat", lambda series: series.mode().to_numpy(), FeaturedType.CATEGORICAL, is_default=True),

    Metric("num_unique_strings", lambda series: series.nunique(dropna=True), FeaturedType.TEXT),

    Metric("avg_length_arr", lambda series: array_metrics(series).get("avg_length"), FeaturedType.ARRAY),
    Metric("min_length_arr", lambda series: array_metrics(series).get("min_length"), FeaturedType.ARRAY),
    Metric("max_length_arr", lambda series: array_metrics(series).get("max_length"), FeaturedType.ARRAY),
    Metric("avg_value", lambda series: array_metrics(series).get("avg_value"), FeaturedType.ARRAY),
    Metric("min_value", lambda series: array_metrics(series).get("min_value"), FeaturedType.ARRAY),
    Metric("max_value", lambda series: array_metrics(series).get("max_value"), FeaturedType.ARRAY),

    Metric("num_rows", lambda df: df.shape[0], FeaturedType.GENERAL, is_default=True),
    Metric("num_columns", lambda df: df.shape[1], FeaturedType.GENERAL, is_default=True),
    Metric("memory_usage", lambda df: df.memory_usage(deep=True).sum(), FeaturedType.GENERAL),

    # Outlier Metrics (not rendered, because very special output structure)

    Metric("outlier_lof", local_outlier_factor, FeaturedType.NUMERIC, round=False),
    Metric("outlier_dbscan", dbscan, FeaturedType.NUMERIC, round=False),
    Metric("outlier_iqr", interquartile_range, FeaturedType.NUMERIC, round=False),
    Metric("outlier_zscore", z_score, FeaturedType.NUMERIC, round=False),


    Metric("min_date", pd.Series.min, FeaturedType.DATE, round=False),
    Metric("max_date", pd.Series.max, FeaturedType.DATE, round=False),
    Metric("mean_date", pd.Series.mean, FeaturedType.DATE, round=False),
    Metric("median_date", pd.Series.median, FeaturedType.DATE, round=False),
    Metric("mode_date", lambda s: s.mode().to_list(), FeaturedType.DATE, round=False),
    Metric("histogram_date", datetime_histogram, FeaturedType.DATE, round=False),
]


METRIC_REGISTRY: dict[str, Metric] = {
    metric.key: metric 
    for metric in _builtin_metrics
}

def register_metrics(*metrics: Metric) -> None:
    METRIC_REGISTRY.update({
        metric.key: metric
        for metric in metrics
    })


def select_metrics(for_featured_type: FeaturedType) -> list[Metric]:
    return list(filter(
        lambda v: v.type is for_featured_type, 
        METRIC_REGISTRY.values()
    ))

def get_metrics_subset(keys: Iterable[str], registry: Dict[str, Metric]) -> Dict[str, Metric]:
    keys = set(keys)
    return {
        key: metric
        for key, metric
        in registry.items()
        if key in keys
    }