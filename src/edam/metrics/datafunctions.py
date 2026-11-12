"""This module contains additional functions that
calculate some metric about a :class:`pd.Series` object.
"""
from typing import List, Dict
import pandas as pd
import numpy as np

from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN


def array_metrics(series: pd.Series) -> dict:
    result = {}

    # avg string len 
    if series.apply(lambda x: isinstance(x, list) and all(isinstance(i, str) for i in x)).all():
        avg_lengths_per_array = [
            np.mean([len(i) for i in x]) for x in series if isinstance(x, list) and x
        ]
        result["avg_length"] = float(np.mean(avg_lengths_per_array))
        result["min_length"] = series.apply(lambda x: min([len(i) for i in x]) if isinstance(x, list) and x else 0).min()
        result["max_length"] = series.apply(lambda x: max([len(i) for i in x]) if isinstance(x, list) and x else 0).max()

    # avg value, min value, max value
    elif series.apply(lambda x: isinstance(x, list) and all(isinstance(i, (int, float)) for i in x)).all():
        avg_values_per_array = [
            np.mean(x) for x in series if isinstance(x, list) and x
        ]
        result["avg_value"] = float(np.mean(avg_values_per_array))
        result["min_value"] = series.apply(lambda x: min(x) if isinstance(x, list) and x else 0).min()
        result["max_value"] = series.apply(lambda x: max(x) if isinstance(x, list) and x else 0).max()

    return result

def histogram(series: pd.Series) -> dict:
    try:
        num_bins = int(np.ceil(1 + np.log2(len(series)))*1.5)
        bins, edges = np.histogram(series.dropna(), bins=num_bins)
        return {
            "bins": [float(bin) for bin in bins.tolist()],
            "edges": [float(edge) for edge in edges.tolist()]
        }

    except ValueError:
        return {}

    
def datetime_histogram(series: pd.Series) -> dict:
    try:
        dates = pd.to_datetime(series.dropna())

        if dates.empty:
            return {}

        # Datetime in Unix-Zeit (Nanosekunden) umwandeln
        timestamps = dates.astype("int64")

        num_bins = int(np.ceil(1 + np.log2(len(dates))) * 1.5)

        bins, edges = np.histogram(timestamps, bins=num_bins)

        # Bin-Kanten zurück in Datetime konvertieren
        datetime_edges = pd.to_datetime(edges.astype("int64"))

        return {
            "bins": [float(bin) for bin in bins.tolist()],
            "edges": datetime_edges.tolist()
        }

    except (ValueError, TypeError, OverflowError):
        return {}


def is_numeric_and_not_bool(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)

def iqr(series: pd.Series) -> float | None:
    if is_numeric_and_not_bool(series):
        return series.quantile(0.75) - series.quantile(0.25)
    return None

def data_range(series: pd.Series) -> float | None:
    if is_numeric_and_not_bool(series):
        return series.max() - series.min()
    return None

def min_max(series: pd.Series) -> List[float] | None:
    if is_numeric_and_not_bool(series):
        return [series.min(), series.max()]

def quantiles(series: pd.Series) -> pd.Series | None:
    if is_numeric_and_not_bool(series):
        return series.quantile([0.25, 0.5, 0.75])
    return None

def mad(series: pd.Series) -> float:
    return float((series - series.median()).abs().median())

# OUTLIER FUNCTIONS

def local_outlier_factor(col: pd.Series, contamination=0.05, n_neighbors=5):
    if not col.notna().all():
        return {"WARNING": "column contained NaN", "n_outliers": 0, "n_clusters": 0, "indices": []}
    clf = LocalOutlierFactor(
        n_neighbors=n_neighbors, 
        contamination=contamination, 
        metric='minkowski', 
        p=2
    )

    predictions = clf.fit_predict(pd.DataFrame(col))

    is_outlier_mask = (predictions == -1)

    outlier_indices = np.where(is_outlier_mask)[0].tolist()

    outlier_count = int(is_outlier_mask.sum())

    return {
        "parameters": {
            "contamination": contamination,
            "n_neighbors": n_neighbors
        },
        "n_outliers": outlier_count,
        "indices": outlier_indices
    }

def dbscan(col: pd.Series, eps: float = 0.2, min_samples: int =2, metric: str = 'euclidean'):
    if not col.notna().all():
            return {"WARNING": "column contained NaN", "n_outliers": 0, "n_clusters": 0, "indices": []}
    model = DBSCAN(eps=eps, min_samples=min_samples, metric=metric)
    model.fit(pd.DataFrame(col))
    outlier_indices = np.where(model.labels_ == -1)[0].tolist()
    outlier_count = int(np.count_nonzero(model.labels_ == -1))
    return {
        "parameters": {
            "algorithm": "DBSCAN",
            "eps": eps,
            "min_samples": min_samples,
            "metric": metric
        },
        "n_outliers": outlier_count,
        "n_clusters": len(set(model.labels_)),
        "indices": outlier_indices
    }

def interquartile_range(col: pd.Series, lower_factor: float = 1.5, upper_factor: float = 1.5):
    q1, q3 = col.quantile((0.25, 0.75))

    iqr = q3 - q1

    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    outliers = col[(col < lower_bound) | (col > upper_bound)]
    outlier_indices = outliers.index.to_list()
    outlier_count = len(outliers)

    return {
        "parameters": {
            "lower_factor": lower_factor,
            "upper_factor": upper_factor
        },
        "n_outliers": int(outlier_count),
        "indices": outlier_indices
    }

def z_score(col: pd.Series, threshold: float = 3.0) -> dict:
    z_scores = (col - col.mean()) / col.std(ddof=1)

    is_outlier = np.abs(z_scores) > threshold
    outlier_counts = is_outlier.sum()
    outlier_indices = col[is_outlier].index.tolist()
    return {
        "n_outliers": int(outlier_counts),
        "indices": outlier_indices,
        "parameters": {
            "algorithm": "z-score",
            "sd_factor": threshold
        }
    }