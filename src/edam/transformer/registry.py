import itertools

from .transformer import ColumnTransformer
from ..schema.schema import FeaturedType

# for ascii transformation

_builtin_transformers = [
    ColumnTransformer("text_len", FeaturedType.TEXT, FeaturedType.NUMERIC, lambda x: x.str.len()),
    ColumnTransformer("array_len", FeaturedType.ARRAY, FeaturedType.NUMERIC, lambda x: x.map(lambda r: len(r))),
#    ColumnTransformer("ascii", FeaturedType.TEXT, FeaturedType.NUMERIC, ascii_transformer)
] + [
    ColumnTransformer("identity", ft, ft, lambda x: x)
    for ft in FeaturedType
] + [
    ColumnTransformer("as_text", ft, FeaturedType.TEXT, lambda x: x.astype(str))
    for ft in FeaturedType if ft not in (FeaturedType.TEXT, FeaturedType.DATE)
]

TRANSFORMERS: dict[FeaturedType, list[ColumnTransformer]] = {
    source_type: list(transformers)
    for source_type, transformers
    in itertools.groupby(
        sorted( _builtin_transformers, key=lambda x: x.source_type),
        key=lambda x: x.source_type
    )
}


def select_transformers(for_featured_type: FeaturedType) -> list[ColumnTransformer]:
    return TRANSFORMERS[for_featured_type]