import logging
from typing import Dict, List

import app.src.data_processing.transform as T
import app.src.files_processing.files_processing as P
import pandas as pd


def load_df_from_csv(
    filepath: str, delimiter: str = ",", header: int = 0
) -> pd.DataFrame:
    return pd.read_csv(filepath, delimiter=delimiter, header=header)


def load_df_from_json(filepath: str) -> pd.DataFrame:
    return pd.read_json(filepath)


def load_df_from_dict(dictionary: Dict) -> pd.DataFrame:
    return pd.DataFrame.from_dict(dictionary)


def load_input_data(paths: List) -> pd.DataFrame:
    list_dfs = []

    for path in paths:
        if path.endswith(".csv"):
            df = load_df_from_csv(path)

        elif path.endswith(".json"):
            try:
                df = load_df_from_json(path)
            except ValueError:
                logging.warning(
                    f"Broken json detected in {path}. Attempting to clean it and re-load it."
                )
                fixed_json = P.fix_broken_json(path)
                df = load_df_from_dict(fixed_json)

        else:
            raise Exception(
                f"The provided path {path} has an incompatible file extension (not csv nor json)."
            )

        list_dfs.append(df)

    df = T.merge_dataframes(list_dfs)

    logging.info(f"[Loading] - Successfully loaded and merged dataframes from {paths}.")
    return df
