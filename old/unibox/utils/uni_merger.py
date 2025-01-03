import pandas as pd
import warnings
from pathlib import Path
from typing import Union, List, Dict, Any

import unibox
from unibox import UniLogger


class UniMerger:
    def __init__(self, logger: UniLogger = None):
        self.logger = logger if logger else UniLogger(file_suffix="UniMerger")

    def _merge_dicts(self, *dicts):
        result = {}
        for d in dicts:
            if not isinstance(d, dict):
                self.logger.warning(f"Expected a dictionary, but got {type(d)}. Skipping...")
                continue

            for key, value in d.items():
                if key in result and type(result[key]) != type(value):
                    self.logger.warning(
                        f"Data type mismatch for key '{key}': {type(result[key])} vs {type(value)}. Proceeding with the merge...")
                result[key] = value
        return result

    def _merge_dataframes(self, *dfs):
        common_columns = set(dfs[0].columns)
        for df in dfs[1:]:
            common_columns &= set(df.columns)

        if not common_columns:
            raise ValueError("All dataframes must have at least one column in common for merging.")

        all_columns = set()
        for df in dfs:
            all_columns |= set(df.columns)

        missing_columns = all_columns - common_columns
        if missing_columns:
            self.logger.warning(f"Columns missing in at least one dataframe: {missing_columns}")

        result = pd.concat(dfs, ignore_index=True, sort=False)
        return result

    def merges(self, *data: Union[str, Dict, pd.DataFrame, Any]):
        loaded_data = []
        for d in data:
            if isinstance(d, str):
                loaded = unibox.loads(Path(d))
                if loaded is not None:
                    loaded_data.append(loaded)
            else:
                loaded_data.append(d)

        if all(isinstance(d, dict) for d in loaded_data):
            return self._merge_dicts(*loaded_data)
        elif all(isinstance(d, pd.DataFrame) for d in loaded_data):
            return self._merge_dataframes(*loaded_data)
        else:
            self.logger.error(
                "All inputs must be of the same type (either all dictionaries, all dataframes, or all file paths).")
            return None


def demo():
    # Usage example
    data_merger = UniMerger()

    # Merging dictionaries
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'c': 3, 'd': 4}
    dict3 = {'e': 5, 'f': 6}
    merged_dicts = data_merger.merges(dict1, dict2, dict3)
    print(merged_dicts)

    # Merging dataframes
    df1 = pd.DataFrame({'filename': ['file1', 'file2'], 'A': [1, 2]})
    df2 = pd.DataFrame({'filename': ['file3', 'file4'], 'B': [3, 4]})
    df3 = pd.DataFrame({'filename': ['file5', 'file6'], 'C': [5, 6]})
    merged_dfs = data_merger.merges(df1, df2, df3)
    print(merged_dfs)



if __name__ == "__main__":

    # demo()

    file1 = r"D:\Andrew\Downloads\combined_upscale_todo_v2_part5.parquet"
    file2 = r"D:\Andrew\Downloads\combined_upscale_todo_v2_part3.parquet"
    merger = UniMerger()
    df3 = merger.merges(file1, file2)

    print("D")







