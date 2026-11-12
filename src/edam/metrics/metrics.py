from __future__  import annotations
from typing import Any
from collections.abc import Callable
from dataclasses import dataclass, field

import pandas as pd

from ..schema.schema import FeaturedType
from ..profile.profiles import MetricResult

@dataclass(frozen=True)
class Metric[T: pd.DataFrame | pd.Series]:
    key: str
    func: Callable[[T], Any]
    type: FeaturedType
    is_default: bool = False
    round: bool = True

    def __call__(self, data: T) -> MetricResult:
        roundable = self.round and self.type is FeaturedType.NUMERIC
        return MetricResult(
            self.key, 
            self.func(data),
            roundable
        )