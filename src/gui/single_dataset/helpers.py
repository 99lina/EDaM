import itertools
from collections.abc import Iterable, Iterator, Callable
from collections import defaultdict
from typing import Any

import pandas as pd

def groupby[S, T](iterable: Iterable[S], key: Callable[[S], T]) -> Iterator[tuple[T, list[S]]]:
    # Ein Dictionary, das Elemente nach Key sammelt
    groups = defaultdict(list)
    
    for item in iterable:
        k = key(item)
        groups[k].append(item)
        
    # Gibt ein Iterator-Paar aus (Schlüssel, Liste der Elemente) zurück
    return iter(groups.items())

def build_vega_altair_format_expr(data: pd.DataFrame):
    positions, labels = data.x, data.label
    vega_str = " : ".join(
        map(lambda pos, lab: f"datum.value == {pos} ? '{lab}'", positions, labels)
    )
    vega_str += " : ''"
    return vega_str


def build_vega_altair_format_expr_datetime(data: pd.DataFrame):
    positions, labels = data.x, data.label

    conditions = []

    for pos, lab in zip(positions, labels):
        date_str = pd.Timestamp(pos).strftime("%Y-%m-%dT%H:%M:%S.%f")

        conditions.append(
            f"timeFormat(datum.value, '%Y-%m-%dT%H:%M:%S.%f') "
            f"== '{date_str}' ? '{lab}'"
        )

    return " : ".join(conditions) + " : ''"
