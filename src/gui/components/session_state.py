from enum import StrEnum, auto


class SessionKey(StrEnum):
    CONFIG = auto()
    COLUMN_EMBEDDINGS = auto()
    SELECTED_METRICS = auto()
    UPLOADED_PROFILES = auto()