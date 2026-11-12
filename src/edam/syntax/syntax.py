import pandas as pd
from grex import RegExpBuilder
import re

def _make_regex_readable(regex: str) -> str:
    replacements = {
        r'\w': '[A-Za-z]',
        r'\d': '[0-9]',
        r'\s': '[ \t\n\r\f\v]',
    }

    for old, new in replacements.items():
        regex = regex.replace(old, new)

    return regex

def build_column_regex(column: pd.Series) -> str:
    values = column.dropna().astype(str).tolist()

    # Generate regex
    regex = (
        RegExpBuilder.from_test_cases(values)
        .with_conversion_of_digits()
        .with_conversion_of_words()
        .with_conversion_of_repetitions()
        .with_case_insensitive_matching()
        .build()
    )
    return _make_regex_readable(regex)
