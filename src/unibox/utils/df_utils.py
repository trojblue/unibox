# pandas related code

import collections.abc
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

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


def generate_dataset_summary(
    df: pd.DataFrame,
    repo_id: str,
    sample_rows: int = 3,
    max_unique_for_freq: int = 20,
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

    def column_memory_usage(df: pd.DataFrame) -> pd.DataFrame:
        """Compute per-column memory usage. Returns a DataFrame with:
        Column, Dtype, Memory Usage (bytes), and Readable Memory Usage.
        """
        usage_info = []
        for col in df.columns:
            try:
                col_bytes = df[col].memory_usage(deep=True)
            except Exception:
                # Fallback in case deep=True fails for any reason
                col_bytes = df[col].memory_usage(deep=False)
            usage_info.append(
                {
                    "Column": col,
                    "Dtype": str(df[col].dtype),
                    "Memory Usage (bytes)": col_bytes,
                    "Readable Memory Usage": human_readable_size(col_bytes),
                },
            )
        return pd.DataFrame(usage_info)

    def truncate_text(text, max_len=50):
        """Truncate text to a max length for preview."""
        if not isinstance(text, str):
            text = str(text)
        return text if len(text) <= max_len else text[: max_len - 3] + "..."

    def compute_duplicates_count(df: pd.DataFrame) -> (int, str):
        """Compute duplicated row count and duplicate rate (%) in a dataframe.
        For safety, converts unhashable (object) columns to string representation
        before calling .duplicated().
        """
        safe_df = df.copy()
        for col in safe_df.columns:
            # Convert 'object' or 'category' dtypes to string for safe dedup check
            col_dtype = safe_df[col].dtype
            if str(col_dtype) in ["object", "category"]:
                safe_df[col] = safe_df[col].astype(str)

        try:
            duplicate_count = safe_df.duplicated().sum()
            if len(safe_df) > 0:
                duplicate_rate = f"{(duplicate_count / len(safe_df) * 100):.2f}%"
            else:
                duplicate_rate = "N/A"
        except Exception:
            duplicate_count = "N/A"
            duplicate_rate = "N/A"

        return duplicate_count, duplicate_rate

    def build_robust_column_summaries(df: pd.DataFrame, max_unique_for_freq=10) -> str:
        lines = []
        lines.append("## Column Summaries:")

        for col in df.columns:
            lines.append(f"\n→ {col} ({df[col].dtype})")
            try:
                col_data = df[col]
                dtype = col_data.dtype

                if pd.api.types.is_numeric_dtype(col_data) and not pd.api.types.is_bool_dtype(col_data):
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

                elif pd.api.types.is_bool_dtype(col_data):
                    total = len(col_data)
                    true_count = (col_data == True).sum()
                    false_count = (col_data == False).sum()
                    na_count = col_data.isna().sum()
                    lines.append(
                        f"  - True: {true_count} ({true_count / total:.2%}), False: {false_count} ({false_count / total:.2%})",
                    )
                    if na_count > 0:
                        lines.append(f"  - Missing: {na_count} ({na_count / total:.2%})")

                elif pd.api.types.is_datetime64_any_dtype(dtype):
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
                        unique_vals = non_null.unique()
                        nunique = len(unique_vals)
                        lines.append(f"  - Unique values: {nunique}")
                        if nunique <= max_unique_for_freq:
                            freqs = col_data.value_counts(dropna=False).head(max_unique_for_freq)
                            for val, count in freqs.items():
                                percent = count / len(df) * 100
                                lines.append(f"    - {val!r}: {count} ({percent:.2f}%)")

            except Exception as e:
                lines.append(f"  - Summary failed: {type(e).__name__} – {e!s}")

        return "\n".join(lines)

    # -------------------------------------------------------------
    # 3) Compute memory, duplicates, missing info
    # -------------------------------------------------------------
    mem_df = column_memory_usage(df)
    total_mem = mem_df["Memory Usage (bytes)"].sum()
    total_mem_readable = human_readable_size(total_mem)

    # Missing stats
    missing_count = df.isnull().sum()
    missing_rate = (missing_count / len(df) * 100).round(2).astype(str) + "%"

    # Duplicate stats
    duplicate_count, duplicate_rate = compute_duplicates_count(df)

    # Combine memory, dtype, missing info into a single DataFrame
    stats_df = pd.DataFrame(
        {
            "Column": df.columns,
            "Dtype": mem_df["Dtype"],
            "Memory Usage": mem_df["Readable Memory Usage"],
            "Missing Count": missing_count.values,
            "Missing Rate": missing_rate.values,
        },
    )

    # Add a total row at the bottom
    total_row = pd.DataFrame(
        [
            {
                "Column": "",
                "Dtype": "",
                "Memory Usage": "",
                "Missing Count": "",
                "Missing Rate": "",
            },
            {
                "Column": "**TOTAL**",
                "Dtype": "N/A",
                "Memory Usage": total_mem_readable,
                "Missing Count": missing_count.sum(),
                "Missing Rate": f"{(missing_count.sum() / (len(df) * len(df.columns)) * 100):.2f}%",
            },
        ],
    )

    stats_df = pd.concat([stats_df, total_row], ignore_index=True)

    # Safely convert stats_df to a markdown table
    try:
        stats_table = stats_df.to_markdown(index=False)
    except Exception:
        stats_table = "Error generating stats table."

    # -------------------------------------------------------------
    # 4) Build column summaries
    # -------------------------------------------------------------
    try:
        column_summaries_text = build_robust_column_summaries(df)
    except Exception as e:
        column_summaries_text = f"Error generating column summaries: {e}"

    # -------------------------------------------------------------
    # 5) Build a safe sample preview
    # -------------------------------------------------------------
    preview_df = df.copy()

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
            sample_table = preview_df[renderable_cols].head(sample_rows).to_markdown(index=False)
        except Exception:
            # Fallback: try .to_string if to_markdown fails
            try:
                sample_table = preview_df[renderable_cols].head(sample_rows).to_string(index=False)
            except Exception as e:
                sample_table = f"Preview table failed. Error: {e}"

    # -------------------------------------------------------------
    # 6) Construct final markdown output
    # -------------------------------------------------------------
    readme_text = f"""# {repo_id}
(Auto-generated summary)

## Basic Info:
- Shape: **{df.shape[0]}** rows × **{df.shape[1]}** columns
- Total Memory Usage: {total_mem_readable}
- Duplicates: {duplicate_count} ({duplicate_rate})

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
