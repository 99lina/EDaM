import pandas as pd

from .schema import Schema, Property, FeaturedType
from ..syntax.syntax import build_column_regex


class SchemaExtractor:
    """Interface for a schema extractor"""
    @classmethod
    def extract_schema(cls, data: pd.DataFrame | dict | list, **kwargs) -> Schema:
        """Method for generating the schema for a specific dataset"""
        raise NotImplementedError()



class PandasSchemaExtractor(SchemaExtractor):
    """Class which extracts the schema from a :class:`pd.DataFrame`."""
    @classmethod
    def extract_schema(cls, data: pd.DataFrame | dict | list, categorical_properties: list[str] | None = None, **kwargs) -> Schema:
        categorical_properties = categorical_properties if categorical_properties is not None else []
        if not isinstance(data, pd.DataFrame):
            raise TypeError("'data' must be of type 'pd.DataFrame'")

        properties = [
            Property(
                str(column_name),
                *cls._infer_featured_type(series, categorical_properties),
                syntax_pattern=build_column_regex(series)
                # semantic_pattern=get_semantic_pattern(series), # TODO: add semantic pattern
            )
            for column_name, series in data.items()
        ]
        return Schema.from_list(properties)

    @staticmethod
    def _infer_featured_type(
        series: pd.Series,
        categorical_properties: list[str],
        threshold_categorical: float = 0.5
    ) -> tuple[str, FeaturedType]:
        """This function infers the feature type of a :class:`pd.Series`. 
        
        The possible types are stored in the enum :class:`src.schema.FeatureType`. The method does 
        assume all series which have exclusively numeric values to be of type 
        :class:`~src.schema.FeatureType.NUMERIC`. 
        If such a series should be of type 
        :class:`~src.schema.FeatureType.CATEGORICAL`, 
        you can define it with the parameter ``categorical_properties``.
        """

        if series.name in categorical_properties:
            featured_type = FeaturedType.CATEGORICAL

        elif pd.api.types.is_numeric_dtype(series.dtype):
            featured_type = FeaturedType.NUMERIC

        elif pd.api.types.is_datetime64_any_dtype(series.dtype):
            featured_type = FeaturedType.DATE

        elif pd.api.types.is_string_dtype(series.dtype):
            try:
                x = pd.to_datetime(series, errors="raise")
                featured_type = FeaturedType.DATE
            except:
                if series.nunique() / len(series) > threshold_categorical:
                    featured_type = FeaturedType.TEXT
                else:
                    featured_type = FeaturedType.CATEGORICAL


        else:
            featured_type = FeaturedType.OTHER

        init_type = str(series.dtype)
        return init_type, featured_type

EXTRACTORS = {".csv": PandasSchemaExtractor}