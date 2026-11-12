from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, field
from enum import StrEnum

import io

from ..schema.extractor import EXTRACTORS

class MetricPreselection(StrEnum):
    NONE = "none"
    DEFAULT = "default"
    ALL = "all"


@dataclass(unsafe_hash=True)
class GensonConfig:
    enabled: bool = False
    output_path: str = "genson.json"


@dataclass(unsafe_hash=True)
class EdamConfig:
    dataset: Dataset | Path
    preselection: MetricPreselection = MetricPreselection.NONE
    metrics: dict[str, list[str]] = field(default_factory=dict, hash=False)
    precision: int = 3
    categorical_columns: tuple[str, ...] = field(default_factory=tuple)
    categorical_threshold: float = 0.5
    genson: GensonConfig = field(default_factory=GensonConfig)

    def __post_init__(self):
        if isinstance(self.dataset, str | Path):
            self.dataset = Dataset(Path(self.dataset))

    @property
    def schema_extractor(self):
        return EXTRACTORS[self.dataset.path.suffix]

class Dataset:
    def __init__(self, path: Path | None = None, contents: io.BytesIO | None = None):
        if path is not None and contents is None:
            self.path = path
            self._bytes = None
        elif path is None and contents is not None:
            self.path = Path(contents.name) if hasattr(contents, "name") else Path("")
            self._bytes = contents.getvalue()
        else:
            raise ValueError("Exactly one of 'path' and 'contents' must be given.")

    @property
    def has_only_bytes(self):
        return self._bytes is not None

    def get_bytesio(self) -> io.BytesIO:
        if self._bytes is not None:
            return io.BytesIO(self._bytes)
        return io.BytesIO(self.path.read_bytes())

    def __hash__(self) -> int:
        return hash((self.path, self._bytes))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dataset):
            return NotImplemented
        return self.path == other.path and self._bytes == other._bytes