# script to calculate the similarity/difference between 2 profiles

from pathlib import Path
import json
import io

import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.metrics.pairwise import cosine_similarity
import altair as alt

from src.edam.profile.profiles import DataProfile, TransformationProfile
from Levenshtein import distance

def load_profile(file: Path | io.BytesIO) -> tuple[DataProfile, str]:
    if isinstance(file, Path):
        text = file.read_text()
        data = json.loads(text)
    else:
        data = json.load(file)
    profile_name, _, _ = Path(file.name).name.rpartition("_")
    return DataProfile.from_dict(data), profile_name

def load_embeddings(path: Path | io.BytesIO) -> tuple[pd.DataFrame, str]:
    data = pd.read_parquet(path).T
    profile_name, _, _ = Path(path.name).name.rpartition("_")

    return data, profile_name

def regex_similarity(regex1: str, regex2: str) -> float:
    """
    Calculate normalized similarity between two regex strings.
    Returns a score between 0 and 1.
    """
    if regex1 == regex2:
        return 1.0

    max_len = max(len(regex1), len(regex2))

    if max_len == 0:
        return 1.0

    dist = distance(regex1, regex2)

    return 1 - dist / max_len


def compare_profiles(profile1: DataProfile, profile2: DataProfile) -> pd.DataFrame:

    d = {}

    for col1 in profile1.column_metrics:
        d[col1.name] = {}

        for col2 in profile2.column_metrics:
            d[col1.name][col2.name] = compare_transformations(
                col1.children["_UNION"],
                col2.children["_UNION"]
            )

    matrix = pd.DataFrame.from_dict(d, orient="index")

    return matrix


def compare_profiles_type(profile1: DataProfile, profile2: DataProfile) -> pd.DataFrame:

    d = {}
    for prop1, data1 in profile1.schema.properties.items():
        d[prop1] = {}
        for prop2, data2 in profile2.schema.properties.items():
            d[prop1][prop2] = data1.init_type == data2.init_type
    return pd.DataFrame.from_dict(d, orient="index")


def compare_profiles_syntax(profile1: DataProfile, profile2: DataProfile) -> pd.DataFrame:

    d = {}
    for prop1, data1 in profile1.schema.properties.items():
        d[prop1] = {}
        for prop2, data2 in profile2.schema.properties.items():
            d[prop1][prop2] = regex_similarity(data1.syntax_pattern, data2.syntax_pattern)
    return pd.DataFrame.from_dict(d, orient="index")

def calc_cos_similarity(embedding1, embedding2):
    similarity_matrix = cosine_similarity(embedding1, embedding2)
    similarity_df = pd.DataFrame(
        similarity_matrix,
        index=embedding1.index,
        columns=embedding2.index,
    )
    return similarity_df



def compare_transformations(
    transformation_1: TransformationProfile,
    transformation_2: TransformationProfile
) -> float:

    children_1 = transformation_1.children
    children_2 = transformation_2.children

    all_keys = set(children_1.keys()) | set(children_2.keys())

    if not all_keys:
        return 1.0

    counter = []

    for key in all_keys:

        # Key exists in both dictionaries
        if key in children_1 and key in children_2:

            v1 = children_1[key].data
            v2 = children_2[key].data

            # Both values are lists
            if isinstance(v1, list) and isinstance(v2, list):

                diff_count = (
                    sum(1 for a, b in zip(v1, v2) if a != b)
                    + abs(len(v1) - len(v2))
                )

                counter.append(1 / (1 + diff_count))

            # Both values are numeric
            elif (
                isinstance(v1, (int, float))
                and isinstance(v2, (int, float))
            ):
                counter.append(1 / (1 + abs(v1 - v2)))

            # Values are equal but not numeric or lists
            else:
                counter.append(1.0 if v1 == v2 else 0.0)

        # Key is missing in one dictionary
        else:
            counter.append(-1.0)

    return sum(counter) / len(counter)


def generate_heat_matrix_alt(matrix_df: pd.DataFrame, name_1: str, name_2: str, title: str = "") -> alt.Chart:
    if name_1 == name_2:
        name_2 = name_1 + "2"
    # 1. DataFrame ins Long-Format bringen (notwendig für Altair)
    index_col_name = matrix_df.index.name if matrix_df.index.name else "index"
    df_long = matrix_df.reset_index().melt(
        id_vars=index_col_name,
        var_name=name_2,
        value_name="value"
    )
    df_long = df_long.rename(columns={index_col_name: name_1})

    # 2. Altair Heatmap erstellen
    chart = alt.Chart(df_long).mark_rect(
        stroke="white",
        strokeWidth=0.5
    ).encode(
        x=alt.X(f"{name_2}:O", title=name_2.title(), axis=alt.Axis(labelAngle=-90)),
        y=alt.Y(f"{name_1}:O", title=name_1.title()),
        color=alt.Color(
            "value:Q",
            scale=alt.Scale(
                domain=[0, 1],
                range=["#FFFFFF", "#C1E3DD"]
            ),
        ),
        tooltip=[
            alt.Tooltip(name_1, title=name_1.title()),
            alt.Tooltip(name_2, title=name_2.title()),
            alt.Tooltip("value:Q", format=".3f", title="Wert")
        ]
    ).properties(
        title=title.title()
    )

    return chart


def combine_and_match(matrix1, matrix2, matrix3, matrix4):

    matrices = [matrix1, matrix2, matrix3, matrix4]

    # Check that all matrices have identical dimensions and labels
    for matrix in matrices[1:]:
        if not matrix.index.equals(matrix1.index) or \
           not matrix.columns.equals(matrix1.columns):
            raise ValueError("All matrices must have identical row and column labels.")

    # 1. Add all four matrices
    combined = sum(matrices)

    # 2. Apply Hungarian algorithm (maximize similarity)
    row_ind, col_ind = linear_sum_assignment(
        combined.to_numpy(),
        maximize=True
    )

    # 3. Extract matching pairs
    matches = pd.DataFrame({
        "row": combined.index[row_ind],
        "column": combined.columns[col_ind],
        "similarity": combined.to_numpy()[row_ind, col_ind]/4
    })

    return combined, matches

if __name__ == "__main__":
    emb_df1, name_1 = load_embeddings(Path("cheese_embeddings.parquet"))
    emb_df2, name_2 = load_embeddings(Path("cheese_embeddings.parquet"))

    # print(match_column_simi(emb_df1, emb_df2))

    profile1, name_1 = load_profile(Path("cheese_profile.json"))
    profile2, name_2 = load_profile(Path("cheese_profile.json"))

    # print("Statistics similarity: ", compare_profiles(profile1, profile2))
    # print("Semantic cosin: ", clac_cos_similarity(emb_df1, emb_df2))
    comp_matrix = compare_profiles(profile1, profile2)
    cos_matrix = calc_cos_similarity(emb_df1, emb_df2)
    # print("matrix2", cos_matrix)
    # generate_heat_matrix_alt(comp_matrix, name_1, name_2, "Data Profile Comparison").save(Path(__file__).parent / "comparison_heatmap.svg")
    # generate_heat_matrix_alt(cos_matrix, name_1, name_2, "Embeddings Comparison (Cosine)").save(Path(__file__).parent / "cosine_heatmap.svg")

    test = compare_profiles_syntax(profile1, profile2)
    test2 = compare_profiles_type(profile1, profile2)

    print(combine_and_match(comp_matrix, cos_matrix, test2, test))

