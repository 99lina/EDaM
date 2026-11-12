from __future__ import annotations
from datetime import datetime
from typing import Self
from collections.abc import Iterable
from itertools import chain

import json

import pandas as pd

from .profiles import TransformationProfile, ColumnProfile, ColumnMetricsProfile, GeneralMetricsProfile, DataProfile, Metadata
from .exceptions import *

from ..schema.schema import Schema, FeaturedType, Property
from ..schema.extractor import SchemaExtractor
from ..metrics.metrics import Metric
from ..metrics.registry import select_metrics, METRIC_REGISTRY, get_metrics_subset
from ..transformer.registry import select_transformers
from ..transformer.transformer import ColumnTransformer
from ..config.config import EdamConfig, Dataset, MetricPreselection
from ..helpers import file_hash, filter_dict


def calculate_transformation_profile(data: pd.Series, transformer: ColumnTransformer) -> TransformationProfile:
    data = transformer(data)
    metrics = select_metrics(transformer.target_type)
    if transformer.target_type is FeaturedType.DATE:
        data = pd.to_datetime(data)
    return TransformationProfile.from_list(
        transformer.name,
        [metric(data) for metric in metrics]
    )

def calculate_column_profile(data: pd.DataFrame, property: Property) -> ColumnProfile:
    column = data[property.name]
    transformers = select_transformers(property.featured_type)

    return ColumnProfile.from_list(
        property.name,
        [
            calculate_transformation_profile(column, transformer)
            for transformer in transformers
        ]
    )

def compute_column_metrics(data: pd.DataFrame, schema: Schema) -> ColumnMetricsProfile:
    column_profiles = [
        calculate_column_profile(data, prop)
        for prop in schema.properties.values()
    ]

    return ColumnMetricsProfile.from_list(column_profiles)

def compute_general_metrics(data: pd.DataFrame) -> GeneralMetricsProfile:
    return GeneralMetricsProfile.from_list(
        metric(data) for metric in select_metrics(FeaturedType.GENERAL)
    )


class DataProfileBuilder:
    """This class enables the creation of a data profile. 
    
    It has a fluent API where you can add 
    customization steps. With the call of the method ```build()```, the data 
    profile gets created.
    """

    @classmethod
    def build_from_config(cls, config: EdamConfig) -> DataProfile:
        return (
            cls()
            .init_metadata()
            .read_dataset(config.dataset)
            .set_fixed_categorical_properties(config.categorical_columns)
            .extract_schema(
                config.schema_extractor,
                # kwargs for SchemaExtractor
                threshold_categorical=config.categorical_threshold,
                genson_schema=config.genson.enabled,
                schema_output_path=config.genson.output_path,
            )
            .compute_metrics()
            .build()
        )

    def init_metadata(self) -> Self:
        self._metadata = Metadata()
        return self

    def read_dataset(self, dataset: Dataset) -> Self:
        self._dataset = dataset    # vlt falsch!
        match dataset.path.suffix:
            case ".json":
                self._input_data = json.load(dataset.get_bytesio())
            case ".csv":
                self._input_data = pd.read_csv(dataset.get_bytesio())
            case _:
                raise FileFormatNotSupportedError(
                    f"File {dataset} can not be processed. File has to be of type JSON or CSV"
                )
        return self

    def set_fixed_categorical_properties(self, categorical_properties: Iterable[str]) -> Self:
        self._categorical_properties = list[categorical_properties]
        return self

    def extract_schema(self, schema_extractor_class: type[SchemaExtractor], **kwargs) -> Self:
        if self._input_data is None:
            raise InputNotGivenError("No data provided for schema extraction")
        self._schema = schema_extractor_class.extract_schema(
            self._input_data,
            categorical_properties=getattr(self, "_categorical_properties", []),
            **kwargs
        )
        return self

    
    def compute_metrics(self) -> Self:
        if not self._schema:
            raise NoSchemaFoundError()
        if isinstance(self._input_data, dict | list):
            normalized_data = pd.json_normalize(self._input_data)
        else:
            normalized_data = pd.DataFrame(self._input_data)
        self._column_metrics = compute_column_metrics(normalized_data, self._schema)
        self._general_metrics = compute_general_metrics(normalized_data)
        return self 
    
    def build(self) -> DataProfile:
        self._metadata.filename = self._dataset.path.name
        self._metadata.hash = file_hash(self._dataset.get_bytesio(), self._dataset.path.suffix)
        self._metadata.set_end()
        return DataProfile(
            self._schema,
            self._column_metrics,
            self._general_metrics,
            self._metadata
        )  


# TODO: Add MetricRegistry class for selection of metrics to compute