import pandas as pd

import unibox as ub


def test_to_df_dict():
    df = ub.to_df({"a": 1, "b": {"c": 2}})

    assert isinstance(df, pd.DataFrame)
    assert df.columns[0] == "DICT_KEY"
    assert set(df["DICT_KEY"]) == {"a", "b"}
    assert df.loc[df["DICT_KEY"] == "a", "VALUE"].iloc[0] == 1
    assert df.loc[df["DICT_KEY"] == "b", "c"].iloc[0] == 2


def test_to_df_list_of_scalars():
    df = ub.to_df(["x", "y"])

    assert list(df.columns) == ["VALUE"]
    assert df["VALUE"].tolist() == ["x", "y"]
