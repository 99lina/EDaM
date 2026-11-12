import os
import hashlib
import csv
import json
from pathlib import Path
from typing import Any, TypeVar
from collections.abc import Callable, Iterator
import io

import numpy as np
import pandas as pd


K = TypeVar("K")
V = TypeVar("V")


def filter_dict(
    func: Callable[[K, V], bool],
    dictionary: dict[K, V]
) -> dict[K, V]:
    return {
        key: value 
        for key, value in dictionary.items()
        if func(key, value)
    }


def file_hash(bytes_buffer: io.BytesIO, ext: str) -> str:
    match ext:
        case ".json":
            data = json.load(bytes_buffer)
        case ".csv":
            text_buffer = io.TextIOWrapper(bytes_buffer, encoding="utf-8")
            reader = csv.DictReader(text_buffer)
            data = list(reader)
        case _:
            raise ValueError(f"Unsupported file extension {ext}")

    def sort_json(obj):
        if isinstance(obj, dict):
            return {k: sort_json(obj[k]) for k in sorted(obj)}
        if isinstance(obj, list):
            if all(isinstance(x, dict) for x in obj):
                sorted_objs = [sort_json(x) for x in obj]
                json_strings = [json.dumps(o, ensure_ascii=False, separators=(",", ":")) for o in sorted_objs]
                sorted_pairs = sorted(zip(json_strings, sorted_objs), key=lambda pair: pair[0])
                return [pair[1] for pair in sorted_pairs]
            if all(isinstance(x, (str, int, float)) for x in obj):
                return sorted(obj)
            return [sort_json(x) for x in obj]
        return obj

    sorted_data = sort_json(data)
    json_str = json.dumps(sorted_data, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(json_str.encode("utf-8")).hexdigest()

def get_path(file: Path | io.BytesIO):
    if isinstance(file, io.BytesIO):
        return Path(file.name)
    elif isinstance(file, Path):
        return file
    else:
        raise TypeError("file must be Path or io.BytesIO.")



def round(value: Any, precision: int) -> Any:
    if isinstance(value, np.ndarray):
        return np.round(value, precision)
    elif isinstance(value, dict):
        return {k: round(v, precision) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return type(value)(round(v, precision) for v in value)
    else:
        return np.round(value, precision)


def normalize_types(val: Any):
    """Konvertiert rekursiv Numpy-, Pandas- und andere Typen in JSON/Streamlit-kompatible Standard-Python-Typen."""
    # Numpy Skalare
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_,)):
        return bool(val)

    # Numpy Arrays
    elif isinstance(val, np.ndarray):
        return val.tolist()

    # Pandas Strukturen
    elif isinstance(val, pd.Series):
        # Entweder als Dict (Index -> Wert) oder Liste
        return val.to_dict()
    elif isinstance(val, pd.DataFrame):
        return val.to_dict(orient="records")
    elif isinstance(val, pd.Index):
        return val.tolist()

    # Rekursion für Container-Typen
    elif isinstance(val, dict):
        # Konvertiert Keys sicher zu Strings (wichtig für JSON)
        return {str(k): normalize_types(v) for k, v in val.items()}

    elif isinstance(val, (list, tuple, set)):
        return [normalize_types(item) for item in val]

    # Basis-Typen (int, float, str, None, bool) bleiben unberührt
    return val