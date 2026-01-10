# pandas related code

import collections.abc
import json
import logging
import warnings
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

DICT_KEY_COLUMN_DEFAULT = "DICT_KEY"
VALUE_COLUMN_DEFAULT = "VALUE"
FLATTEN_SEP_DEFAULT = "__"
FLATTEN_MAX_DEPTH_DEFAULT = 2


def _key_to_str(key) -> str:
    if isinstance(key, str):
        return key
    try:
        return str(key)
    except Exception:
        return repr(key)


def _flatten_dict(data: dict, parent_key: str, depth: int, max_depth: int, sep: str) -> dict:
    items: dict = {}
    for key, value in data.items():
        key_str = _key_to_str(key)
        new_key = f"{parent_key}{sep}{key_str}" if parent_key else key_str
        if isinstance(value, dict):
            if depth >= max_depth:
                items[new_key] = json.dumps(value, default=str)
            else:
                items.update(_flatten_dict(value, new_key, depth + 1, max_depth, sep))
        else:
            items[new_key] = value
    return items


def flatten_value(value: Any, max_depth: int = FLATTEN_MAX_DEPTH_DEFAULT, sep: str = FLATTEN_SEP_DEFAULT) -> Any:
    if isinstance(value, dict):
        return _flatten_dict(value, "", 0, max_depth, sep)
    return value


def flatten_record(record: dict, max_depth: int = FLATTEN_MAX_DEPTH_DEFAULT, sep: str = FLATTEN_SEP_DEFAULT) -> dict:
    flattened: dict = {}
    for key, value in record.items():
        key_str = _key_to_str(key)
        if isinstance(value, dict):
            if max_depth <= 0:
                flattened[key_str] = json.dumps(value, default=str)
            else:
                flattened.update(_flatten_dict(value, key_str, 1, max_depth, sep))
        else:
            flattened[key_str] = value
    return flattened


def coerce_json_like_to_df(
    data: Any,
    dict_key_column: str = DICT_KEY_COLUMN_DEFAULT,
    value_column: str = VALUE_COLUMN_DEFAULT,
    flatten_sep: str = FLATTEN_SEP_DEFAULT,
    max_depth: int = FLATTEN_MAX_DEPTH_DEFAULT,
) -> pd.DataFrame:
    if dict_key_column is None:
        dict_key_column = DICT_KEY_COLUMN_DEFAULT
    if value_column is None:
        value_column = VALUE_COLUMN_DEFAULT
    if flatten_sep is None:
        flatten_sep = FLATTEN_SEP_DEFAULT
    if max_depth is None:
        max_depth = FLATTEN_MAX_DEPTH_DEFAULT

    if isinstance(data, dict):
        rows = []
        for key, value in data.items():
            row = {}
            if isinstance(value, dict):
                row.update(value)
            else:
                row[value_column] = value
            row[dict_key_column] = key
            rows.append(flatten_record(row, max_depth=max_depth, sep=flatten_sep))
        df = pd.DataFrame(rows)
        if dict_key_column in df.columns:
            ordered_cols = [dict_key_column] + [col for col in df.columns if col != dict_key_column]
            df = df[ordered_cols]
        return df

    if isinstance(data, (list, tuple)):
        if len(data) == 0:
            return pd.DataFrame(columns=[value_column])

        has_dict = any(isinstance(item, dict) for item in data)
        has_non_dict = any(not isinstance(item, dict) for item in data)
        if has_dict and has_non_dict:
            warnings.warn(
                "Input list mixes dict and non-dict items; conversion may be lossy or inconsistent. "
                "Consider normalizing the structure before saving.",
                UserWarning,
                stacklevel=2,
            )

        if has_dict:
            rows = []
            for item in data:
                if isinstance(item, dict):
                    rows.append(flatten_record(item, max_depth=max_depth, sep=flatten_sep))
                else:
                    rows.append({value_column: item})
            return pd.DataFrame(rows)

        return pd.DataFrame({value_column: list(data)})

    raise ValueError("Cannot convert JSON-like input to DataFrame for HF dataset save")

# ===== Sanitize Dataframes =====
# see: https://gist.github.com/trojblue/04ec49e942c9aa72f636a13f387f9038


def human_readable_size(size_bytes):
    """Convert bytes to human readable size"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024


def column_memory_usage(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Function to display memory usage of each column"""
    memory_usage = dataframe.memory_usage(deep=True)
    readable_memory_usage = memory_usage.apply(human_readable_size)
    dtypes = dataframe.dtypes

    mem_df = pd.DataFrame(
        {
            "Column": memory_usage.index[1:],  # Exclude Index
            "Memory Usage": memory_usage.values[1:],  # Exclude Index
            # Exclude Index
            "Readable Memory Usage": readable_memory_usage.values[1:],
            "Dtype": dtypes.values,
        },
    )
    mem_df = mem_df.sort_values(by="Memory Usage", ascending=False)
    return mem_df


def downcast_numerical_columns(df: pd.DataFrame):
    """Reduce precision of numerical columns using to_numeric with downcast"""
    numerical_columns = df.select_dtypes(include=["int64", "float64"]).columns
    for col in numerical_columns:
        df[col] = pd.to_numeric(df[col], downcast="integer" if df[col].dtype == "int64" else "float")
    return df


def convert_object_to_category(df: pd.DataFrame, category_columns: list[str]) -> pd.DataFrame:
    """Convert specified columns in the DataFrame to categorical type.

    :param df: DataFrame to convert columns.
    :param category_columns: List of column names to convert to categorical type.
    :return: DataFrame with specified columns converted to categorical type.
    """
    if not isinstance(category_columns, list):
        raise ValueError("category_columns must be a list of column names")

    for col in category_columns:
        if df[col].isna().sum() > 0:  # Check for NaN values
            df[col] = pd.Categorical(df[col], categories=df[col].dropna().unique())
        df[col] = df[col].astype("category")

    return df


def get_random_df() -> pd.DataFrame:
    """Generate a random DataFrame for testing purposes"""
    import random
    from datetime import datetime

    df = pd.DataFrame(
        {
            "name": [f"Name_{i}" for i in range(1000)],
            "age": [random.randint(18, 80) for _ in range(1000)],
            "height": [random.randint(150, 200) for _ in range(1000)],
            "weight": [random.randint(50, 150) for _ in range(1000)],
            "date": [datetime.now() for _ in range(1000)],
            "is_student": [random.choice([True, False]) for _ in range(1000)],
        },
    )
    return df


def truncate_text(text, max_length=200):
    """Truncate text if it exceeds max_length, adding an ellipsis."""
    if isinstance(text, str):
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text.replace("\n", " ")  # Remove excessive newlines
    return text


import pandas as pd


def _markdown_cell(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    text = str(value)
    return text.replace("\r", " ").replace("\n", " ").replace("|", "\\|")


def dataframe_to_markdown_fallback(df: pd.DataFrame, index: bool = False) -> str:
    """Convert DataFrame to markdown without requiring optional tabulate dependency."""
    try:
        return df.to_markdown(index=index)
    except Exception as e:
        logger.debug("to_markdown failed; falling back to manual markdown: %s", e)

    table_df = df
    if index:
        table_df = df.copy()
        table_df.insert(0, "index", df.index)

    columns = [str(col) for col in table_df.columns]
    if not columns:
        return ""

    rows = [[_markdown_cell(cell) for cell in row] for row in table_df.itertuples(index=False, name=None)]

    widths = [len(col) for col in columns]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))

    def format_row(values: list[str]) -> str:
        padded = [values[i].ljust(widths[i]) for i in range(len(widths))]
        return "| " + " | ".join(padded) + " |"

    lines = [format_row(columns), "| " + " | ".join("-" * w for w in widths) + " |"]
    for row in rows:
        lines.append(format_row(row))
    return "\n".join(lines)


def generate_dataset_summary(
    df: pd.DataFrame,
    repo_id: str,
    sample_rows: int = 3,
    max_unique_for_freq: int = 20,
    profile_rows: int = 200_000,
    max_rows_for_deep_memory: int = 1_000_000,
    max_rows_for_duplicates: int = 200_000,
) -> str:
    """Generate a combined dataset summary markdown text that merges:
    - robust column-wise checks (numeric, datetime, object, bool) and missing values
    - memory usage, duplicates, and table displays
    - sample row previews
    """

    # -------------------------------------------------------------
    # 1) Helper functions
    # -------------------------------------------------------------
    def human_readable_size(size_in_bytes: float) -> str:
        """Convert bytes to a human-readable string."""
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        i = 0
        while size_in_bytes > 1024 and i < len(units) - 1:
            size_in_bytes /= 1024.0
            i += 1
        return f"{size_in_bytes:.2f} {units[i]}"

    def column_memory_usage(df: pd.DataFrame, deep: bool) -> pd.DataFrame:
        """Compute per-column memory usage. Returns a DataFrame with:
        Column, Dtype, Memory Usage (bytes), and Readable Memory Usage.
        """
        try:
            usage = df.memory_usage(deep=deep, index=False)
        except Exception:
            usage = df.memory_usage(deep=False, index=False)
        dtypes = df.dtypes.astype(str)
        usage_values = usage.values if hasattr(usage, "values") else usage
        return pd.DataFrame(
            {
                "Column": df.columns,
                "Dtype": dtypes.values,
                "Memory Usage (bytes)": usage_values,
                "Readable Memory Usage": [human_readable_size(val) for val in usage_values],
            },
        )

    def truncate_text(text, max_len=50):
        """Truncate text to a max length for preview."""
        if not isinstance(text, str):
            text = str(text)
        return text if len(text) <= max_len else text[: max_len - 3] + "..."

    def compute_duplicates_count(df: pd.DataFrame, max_rows: int) -> tuple[Any, str, str]:
        """Compute duplicated row count and duplicate rate (%).
        Uses a capped sample for large frames to avoid full-table scans.
        """
        if len(df) == 0:
            return 0, "N/A", ""

        if max_rows and len(df) > max_rows:
            dup_df = df.head(max_rows)
            note = f"(sample of {len(dup_df)})"
        else:
            dup_df = df
            note = ""

        try:
            duplicate_count = dup_df.duplicated().sum()
        except Exception:
            try:
                obj_cols = dup_df.select_dtypes(include=["object", "category"]).columns
                if len(obj_cols) > 0:
                    safe_df = dup_df.copy()
                    safe_df[obj_cols] = safe_df[obj_cols].astype(str)
                else:
                    safe_df = dup_df
                duplicate_count = safe_df.duplicated().sum()
            except Exception:
                return "N/A", "N/A", note

        total = len(dup_df)
        duplicate_rate = f"{(duplicate_count / total * 100):.2f}%" if total else "N/A"
        return duplicate_count, duplicate_rate, note

    def build_robust_column_summaries(
        summary_df: pd.DataFrame,
        max_unique_for_freq: int = 10,
        sample_note: str | None = None,
    ) -> str:
        lines = []
        header = "## Column Summaries:"
        if sample_note:
            header = f"## Column Summaries ({sample_note}):"
        lines.append(header)

        if summary_df.empty:
            lines.append("\n(No rows available for summary.)")
            return "\n".join(lines)

        numeric_cols = [
            col
            for col in summary_df.columns
            if pd.api.types.is_numeric_dtype(summary_df[col]) and not pd.api.types.is_bool_dtype(summary_df[col])
        ]
        bool_cols = [col for col in summary_df.columns if pd.api.types.is_bool_dtype(summary_df[col])]
        datetime_cols = [col for col in summary_df.columns if pd.api.types.is_datetime64_any_dtype(summary_df[col])]
        numeric_set = set(numeric_cols)
        bool_set = set(bool_cols)
        datetime_set = set(datetime_cols)

        numeric_stats = None
        if numeric_cols:
            try:
                numeric_stats = summary_df[numeric_cols].agg(["min", "max", "mean", "std"])
            except Exception:
                numeric_stats = None

        datetime_stats = None
        if datetime_cols:
            try:
                datetime_stats = summary_df[datetime_cols].agg(["min", "max"])
            except Exception:
                datetime_stats = None

        total_rows = len(summary_df)
        for col in summary_df.columns:
            lines.append(f"\n→ {col} ({summary_df[col].dtype})")
            try:
                col_data = summary_df[col]

                if col in numeric_set:
                    if numeric_stats is not None and col in numeric_stats:
                        desc = numeric_stats[col]
                    else:
                        desc = col_data.describe()
                    parts = []
                    for key in ["min", "max", "mean", "std"]:
                        if key in desc and pd.notna(desc[key]):
                            val = desc[key]
                            parts.append(
                                f"{key.capitalize()}: {val:.3f}"
                                if isinstance(val, float)
                                else f"{key.capitalize()}: {val}",
                            )
                    lines.append("  - " + ", ".join(parts) if parts else "  - No valid numeric summary available")

                elif col in bool_set:
                    total = total_rows
                    true_count = (col_data == True).sum()
                    false_count = (col_data == False).sum()
                    na_count = col_data.isna().sum()
                    if total > 0:
                        lines.append(
                            f"  - True: {true_count} ({true_count / total:.2%}), False: {false_count} ({false_count / total:.2%})",
                        )
                    else:
                        lines.append("  - True: 0 (N/A), False: 0 (N/A)")
                    if na_count > 0:
                        lines.append(f"  - Missing: {na_count} ({na_count / total:.2%})")

                elif col in datetime_set:
                    if datetime_stats is not None and col in datetime_stats:
                        min_date = datetime_stats[col].get("min")
                        max_date = datetime_stats[col].get("max")
                    else:
                        min_date = col_data.min()
                        max_date = col_data.max()
                    if pd.notna(min_date) and pd.notna(max_date):
                        lines.append(f"  - Range: {min_date} → {max_date}")
                    else:
                        lines.append("  - Date range unavailable (all NaT?)")

                else:
                    non_null = col_data.dropna()
                    sample_val = non_null.iloc[0] if not non_null.empty else None

                    if isinstance(sample_val, set):
                        lines.append("  - Contains unhashable type: set")
                        set_lengths = non_null.map(lambda x: len(x) if isinstance(x, set) else None)
                        set_lengths = pd.to_numeric(set_lengths, errors="coerce").dropna()
                        if not set_lengths.empty:
                            lines.append(
                                f"    - Typical set length: mean={set_lengths.mean():.2f}, min={set_lengths.min()}, max={set_lengths.max()}",
                            )
                        else:
                            lines.append("    - Could not determine typical set length")

                    elif isinstance(sample_val, (list, tuple, np.ndarray, collections.abc.Sequence)) and not isinstance(
                        sample_val,
                        str,
                    ):
                        val_type = type(sample_val).__name__
                        lines.append(f"  - Contains unhashable sequence: {val_type}")
                        lengths = non_null.map(lambda x: len(x) if isinstance(x, collections.abc.Sized) else None)
                        lengths = pd.to_numeric(lengths, errors="coerce").dropna()
                        if not lengths.empty:
                            lines.append(
                                f"    - Typical length: mean={lengths.mean():.2f}, min={lengths.min()}, max={lengths.max()}",
                            )
                        else:
                            lines.append("    - Could not determine typical length")

                    else:
                        col_for_freq = col_data
                        try:
                            nunique = col_data.nunique(dropna=True)
                        except Exception:
                            try:
                                col_for_freq = col_data.astype(str)
                                nunique = col_for_freq.nunique(dropna=True)
                            except Exception:
                                lines.append("  - Unique values: N/A")
                                continue

                        lines.append(f"  - Unique values: {nunique}")
                        if nunique <= max_unique_for_freq:
                            freqs = col_for_freq.value_counts(dropna=False).head(max_unique_for_freq)
                            for val, count in freqs.items():
                                percent = count / total_rows * 100 if total_rows else 0
                                lines.append(f"    - {val!r}: {count} ({percent:.2f}%)")

            except Exception as e:
                lines.append(f"  - Summary failed: {type(e).__name__} – {e!s}")

        return "\n".join(lines)

    # -------------------------------------------------------------
    # 3) Compute memory, duplicates, missing info
    # -------------------------------------------------------------
    row_count = len(df)
    col_count = len(df.columns)

    if profile_rows is None or profile_rows <= 0:
        profile_rows = row_count

    if row_count > profile_rows:
        profile_df = df.head(profile_rows)
        profile_note = f"first {len(profile_df)} rows"
    else:
        profile_df = df
        profile_note = ""

    object_cols_count = df.select_dtypes(include=["object"]).shape[1]
    use_deep_memory = object_cols_count > 0 and row_count <= max_rows_for_deep_memory
    mem_df = column_memory_usage(df, deep=use_deep_memory)
    total_mem = mem_df["Memory Usage (bytes)"].sum()
    total_mem_readable = human_readable_size(total_mem)
    memory_note = ""
    if not use_deep_memory and object_cols_count > 0:
        memory_note = "Memory usage excludes deep object sizes for performance."

    # Missing stats
    missing_df = profile_df if profile_note else df
    if len(missing_df) > 0:
        missing_count = missing_df.isnull().sum()
        missing_rate = (missing_count / len(missing_df) * 100).round(2).astype(str) + "%"
    else:
        missing_count = pd.Series([0] * col_count, index=df.columns)
        missing_rate = pd.Series(["N/A"] * col_count, index=df.columns)

    missing_count_label = "Missing Count"
    missing_rate_label = "Missing Rate"
    if profile_note:
        missing_count_label = f"Missing Count (sample {len(missing_df)})"
        missing_rate_label = "Missing Rate (sample)"

    # Duplicate stats
    duplicate_count, duplicate_rate, duplicate_note = compute_duplicates_count(df, max_rows_for_duplicates)

    # Combine memory, dtype, missing info into a single DataFrame
    stats_df = pd.DataFrame(
        {
            "Column": df.columns,
            "Dtype": mem_df["Dtype"],
            "Memory Usage": mem_df["Readable Memory Usage"],
            missing_count_label: missing_count.values,
            missing_rate_label: missing_rate.values,
        },
    )

    # Add a total row at the bottom
    denom = len(missing_df) * col_count if col_count else 0
    total_missing_rate = f"{(missing_count.sum() / denom * 100):.2f}%" if denom else "N/A"
    total_row = pd.DataFrame(
        [
            {
                "Column": "",
                "Dtype": "",
                "Memory Usage": "",
                missing_count_label: "",
                missing_rate_label: "",
            },
            {
                "Column": "**TOTAL**",
                "Dtype": "N/A",
                "Memory Usage": total_mem_readable,
                missing_count_label: missing_count.sum(),
                missing_rate_label: total_missing_rate,
            },
        ],
    )

    stats_df = pd.concat([stats_df, total_row], ignore_index=True)

    # Safely convert stats_df to a markdown table
    try:
        stats_table = dataframe_to_markdown_fallback(stats_df, index=False)
    except Exception:
        stats_table = "Error generating stats table."

    # -------------------------------------------------------------
    # 4) Build column summaries
    # -------------------------------------------------------------
    try:
        column_summaries_text = build_robust_column_summaries(
            profile_df,
            max_unique_for_freq=max_unique_for_freq,
            sample_note=profile_note or None,
        )
    except Exception as e:
        column_summaries_text = f"Error generating column summaries: {e}"

    # -------------------------------------------------------------
    # 5) Build a safe sample preview
    # -------------------------------------------------------------
    preview_df = df.head(sample_rows).copy()

    # Truncate long object columns for preview
    for col in preview_df.select_dtypes(include=["object"]):
        try:
            preview_df[col] = preview_df[col].apply(
                lambda x: truncate_text(x) if x is not None else None,
            )
        except Exception:
            # If something fails, coerce to string and then truncate
            preview_df[col] = (
                preview_df[col]
                .astype(str)
                .apply(
                    lambda x: truncate_text(x) if x else None,
                )
            )

    # Identify columns that can be rendered
    renderable_cols = []
    for col in preview_df.columns:
        try:
            # Test if we can astype str on the first few rows
            preview_df[col].head(sample_rows).astype(str)
            renderable_cols.append(col)
        except Exception:
            pass

    if len(renderable_cols) == 0:
        sample_table = f"No columns available for preview (data shape: {df.shape})."
    else:
        try:
            sample_table = dataframe_to_markdown_fallback(
                preview_df[renderable_cols].head(sample_rows),
                index=False,
            )
        except Exception:
            # Fallback: try .to_string if to_markdown fails
            try:
                sample_table = preview_df[renderable_cols].head(sample_rows).to_string(index=False)
            except Exception as e:
                sample_table = f"Preview table failed. Error: {e}"

    # -------------------------------------------------------------
    # 6) Construct final markdown output
    # -------------------------------------------------------------
    notes = []
    if profile_note:
        notes.append(f"Profiling based on {profile_note}.")
    if memory_note:
        notes.append(memory_note)
    notes_text = f"- Notes: {' '.join(notes)}\n" if notes else ""

    readme_text = f"""# {repo_id}
(Auto-generated summary)

## Basic Info:
- Shape: **{df.shape[0]}** rows × **{df.shape[1]}** columns
- Total Memory Usage: {total_mem_readable}
- Duplicates: {duplicate_count} ({duplicate_rate}) {duplicate_note}
{notes_text}

## Column Stats:

{stats_table}

{column_summaries_text}

## Sample Rows (first {sample_rows}):

```
{sample_table}
```

## Usage Example:

```python
import unibox as ub
df = ub.loads("hf://{repo_id}").to_pandas()
```

## Saving to dataset:

```python
import unibox as ub
ub.saves(df, "hf://{repo_id}")
```

(last updated: {pd.Timestamp.now()})
"""
    return readme_text
