import json

import pandas as pd
import pytest

from unibox.utils.df_utils import coerce_json_like_to_df, generate_dataset_summary


def test_coerce_dict_input_adds_dict_key_and_flattens():
    data = {
        "a": 1,
        "b": {"c": 2},
        3: {"d": {"e": {"f": {"g": 1}}}},
    }
    df = coerce_json_like_to_df(data)

    assert isinstance(df, pd.DataFrame)
    assert df.columns[0] == "DICT_KEY"
    assert set(df["DICT_KEY"]) == {"a", "b", 3}

    row_a = df[df["DICT_KEY"] == "a"].iloc[0]
    assert row_a["VALUE"] == 1

    row_b = df[df["DICT_KEY"] == "b"].iloc[0]
    assert row_b["c"] == 2

    row_three = df[df["DICT_KEY"] == 3].iloc[0]
    assert "d__e__f" in df.columns
    assert isinstance(row_three["d__e__f"], str)
    assert json.loads(row_three["d__e__f"]) == {"g": 1}


def test_coerce_list_of_dicts_flattens():
    data = [
        {"id": 1, "meta": {"x": 10}},
        {"id": 2, "meta": {"x": 20, "y": {"z": 30}}},
    ]
    df = coerce_json_like_to_df(data)

    assert isinstance(df, pd.DataFrame)
    assert "meta__x" in df.columns
    assert df.loc[0, "meta__x"] == 10
    assert df.loc[1, "meta__y__z"] == 30


def test_coerce_list_of_scalars():
    data = ["a", "b", "c"]
    df = coerce_json_like_to_df(data)

    assert list(df.columns) == ["VALUE"]
    assert df["VALUE"].tolist() == ["a", "b", "c"]


def test_coerce_mixed_list_warns_and_converts():
    data = [{"a": 1}, "b", 3]
    with pytest.warns(UserWarning, match="mixes dict and non-dict"):
        df = coerce_json_like_to_df(data)

    assert "VALUE" in df.columns
    assert df.loc[1, "VALUE"] == "b"


def test_generate_dataset_summary_fallback_markdown(monkeypatch):
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})

    def _raise(*args, **kwargs):
        raise ImportError("tabulate missing")

    monkeypatch.setattr(pd.DataFrame, "to_markdown", _raise, raising=True)

    summary = generate_dataset_summary(df, "owner/repo", sample_rows=2)

    assert "## Column Stats:" in summary
    assert "Error generating stats table." not in summary
    assert "Memory Usage" in summary
