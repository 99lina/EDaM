from __future__ import annotations

import typing
from dataclasses import dataclass, field, asdict
from enum import StrEnum


class FeatureTypeNotExistingError(ValueError): ...

# TODO: Remove unnecessary feature types
class FeaturedType(StrEnum):
    GENERAL = "general"
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    TEXT = "text"
    ARRAY = "array"
    OBJECT = "object"
    OTHER = "other"
    DATE = "date"  # TODO: Implement date detection (NOT as transformation), some metrics; cosine Similarity




JsonSchema = dict[str, typing.Any]

@dataclass
class Property:
    name: str
    init_type: str
    featured_type: FeaturedType
    semantic_pattern: None = None  # add later
    syntax_pattern: None | str = None
    probability: float | None = field(default=None, repr=False)

    def to_dict(self):
        d = asdict(self)
        if self.probability is None:
            del d["probability"]
        del d["name"]
        return d

    @classmethod
    def from_dict(cls, data: dict, name: str) -> Property:
        return cls(
            name=name,
            featured_type=FeaturedType(data["featured_type"]),
            init_type=data["init_type"],
            semantic_pattern=data["semantic_pattern"],
            syntax_pattern=data["syntax_pattern"],
        )
        

@dataclass
class Schema:
    properties: dict[str, Property]
    json_schema: JsonSchema | None = None

    @classmethod
    def from_list(cls, properties: list[Property], json_schema: JsonSchema | None = None) -> Schema:
        return cls(
            {p.name: p for p in properties},
            json_schema
        )

    def to_dict(self):
        return {
            "properties": {name: prop.to_dict() for name, prop in self.properties.items()},
            "json_schema": self.json_schema
        }

    @classmethod
    def from_dict(cls, data: dict) -> Schema:
        return cls({
            name: Property.from_dict(information, name)
            for name, information in data.items()
        })

