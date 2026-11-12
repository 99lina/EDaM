import json
from pathlib import Path

import pandas as pd
from rich.jupyter import display


class DataProfileDiff:
    @staticmethod
    def load_data_profile(file_path):  # überflüssig?
        with open(file_path, "r") as file:
            return json.load(file)

    @staticmethod
    def calculate_diff(profile_old, profile_new):

        def diff_recursive(old, new):
            diffs = {}

            keys = set(old.keys()) | set(new.keys())

            for key in keys:
                val_old = old.get(key)
                val_new = new.get(key)

                # Handle missing values
                if val_old is None or val_new is None:
                    diffs[key] = None
                    continue

                # Recursive comparison for dictionaries
                if isinstance(val_old, dict) and isinstance(val_new, dict):
                    diffs[key] = diff_recursive(val_old, val_new)

                # Numeric difference
                elif (
                        isinstance(val_old, (int, float))
                        and isinstance(val_new, (int, float))
                        and not isinstance(val_old, bool)
                        and not isinstance(val_new, bool)
                ):
                    diff = val_new - val_old

                    if isinstance(diff, float):
                        diff = round(diff, 6)

                    if diff == 0:
                        continue

                    diffs[key] = diff

                # List difference
                elif isinstance(val_old, list) and isinstance(val_new, list):

                    if len(val_old) == len(val_new):
                        try:
                            diffs[key] = [
                                round(v_new - v_old, 6)
                                if isinstance(v_new - v_old, float)
                                else v_new - v_old
                                for v_old, v_new in zip(val_old, val_new) if v_old != val_new
                            ]
                            if len(diffs[key]) == 0:
                                continue
                        except (TypeError, ValueError):
                            diffs[key] = val_new
                    else:
                        diffs[key] = val_new

                # Non-numeric values
                else:
                    diffs[key] = val_new

            return diffs

        properties_old = profile_old.get("PROPERTIES", {})
        properties_new = profile_new.get("PROPERTIES", {})

        result = {}

        # Iterate over columns
        for column in set(properties_old.keys()) | set(properties_new.keys()):
            old_column = properties_old.get(column, {})
            new_column = properties_new.get(column, {})

            # Only calculate differences for STATISTICS
            old_stats = old_column.get("STATISTICS", {})
            new_stats = new_column.get("STATISTICS", {})

            result[column] = {
                "STATISTICS": diff_recursive(old_stats, new_stats)
            }

        return pd.DataFrame.from_dict({"PROPERTIES": result})

    @staticmethod
    def calculate_schema_diff(schema1, schema2):
        props1 = {prop["name"] for prop in schema1.get("properties", []) if "name" in prop}
        props2 = {prop["name"] for prop in schema2.get("properties", []) if "name" in prop}

        added = sorted(list(props2 - props1))
        removed = sorted(list(props1 - props2))
        unchanged = sorted(list(props1 & props2))

        return {
            "added_columns": added,
            "removed_columns": removed,
            "unchanged_columns": unchanged
        }

    @staticmethod
    def export_diff_to_json(diff_obj: dict, output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(diff_obj, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    profile_diff = DataProfileDiff()
    profile = profile_diff.load_data_profile(Path("cheese_profile.json"))
    profile2 = profile_diff.load_data_profile(Path("cheese2_profile.json"))
    # print(profile)
    print(profile_diff.calculate_diff(profile, profile2).to_string())
