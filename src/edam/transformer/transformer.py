from dataclasses import dataclass
from typing import Any
from collections.abc import Callable
import itertools

import pandas as pd

from src.edam.schema.schema import FeaturedType


@dataclass(frozen=True)
class ColumnTransformer:
    name: str
    source_type: FeaturedType
    target_type: FeaturedType
    transformer: Callable[[pd.Series], pd.Series]

    def __call__(self, data: pd.Series) -> pd.Series:
        return self.transformer(data)