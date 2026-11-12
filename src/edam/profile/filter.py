from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from collections.abc import Iterable
from typing import Literal


type ProfileFilter = dict[str, ProfileFilter | None] | None



