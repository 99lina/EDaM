import pandas as pd
import re
from grex import RegExpBuilder


def _format_grex_output(regex: str, values: list[str]) -> str:
    """Converts grex shorthand tokens into explicit, readable character classes."""
    joined = ''.join(values)

    # Replace \d with [0-9]
    regex = regex.replace(r'\d', '[0-9]')

    # Replace \s with a literal space if no tabs/newlines exist in the column
    if not re.search(r'[\t\n\r\f\v]', joined):
        regex = regex.replace(r'\s', ' ')

    # Replace \w with the exact letter/digit subset present in the column
    has_upper = bool(re.search(r'[A-Z]', joined))
    has_lower = bool(re.search(r'[a-z]', joined))
    has_accent = bool(re.search(r'[À-ÿ]', joined))
    has_digit = bool(re.search(r'[0-9]', joined))
    has_under = '_' in joined

    w_parts = []
    if has_upper and has_lower:
        w_parts.append('A-Za-z')
    elif has_upper:
        w_parts.append('A-Z')
    elif has_lower:
        w_parts.append('a-z')

    if has_accent:
        w_parts.append('À-ÿ')
    if has_digit:
        w_parts.append('0-9')
    if has_under:
        w_parts.append('_')

    w_class = f"[{''.join(w_parts)}]" if w_parts else '[A-Za-z]'
    regex = regex.replace(r'\w', w_class)

    return regex


def build_column_regex(column: pd.Series, max_branches: int = 2) -> str:
    values = column.dropna().astype(str).unique().tolist()
    if not values:
        return r'(?!)'

    # 1. Instantiate RegExpBuilder directly with the list of strings
    regex = (
        RegExpBuilder(values)
        .with_conversion_of_digits()
        .with_conversion_of_words()
        .with_conversion_of_whitespace()
        .with_minimum_repetitions(1)
        .build()
    )

    readable = _format_grex_output(regex, values)

    # 2. Collapse high-branching text (Type, Name, Review) into a minimal character class
    if readable.count('|') >= max_branches:
        has_period = all(v.endswith('.') for v in values)
        trimmed = [v[:-1] for v in values] if has_period else values
        joined = ''.join(trimmed)

        parts = []
        if re.search(r'[A-Z]', joined) and re.search(r'[a-z]', joined):
            parts.append('A-Za-z')
        elif re.search(r'[A-Z]', joined):
            parts.append('A-Z')
        elif re.search(r'[a-z]', joined):
            parts.append('a-z')

        if re.search(r'[À-ÿ]', joined):
            parts.append('À-ÿ')
        if re.search(r'[0-9]', joined):
            parts.append('0-9')
        if ' ' in joined:
            parts.append(' ')

        punct = sorted(set(re.findall(r"[^\w\sÀ-ÿ]", joined)))
        for ch in punct:
            parts.append('\\' + ch if ch in r'\-[]^' else ch)

        char_class = f"[{''.join(parts)}]"
        end_anchor = r'\.$' if has_period else '$'
        return f"^{char_class}+{end_anchor}"

    return readable


if __name__ == '__main__':
    df = pd.read_csv("cheese.csv")

    for col in df.columns:
        print(f"{col}: {build_column_regex(df[col])}")