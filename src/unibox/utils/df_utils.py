# pandas related code

import logging

import pandas as pd
import numpy as np
import collections.abc


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


def generate_dataset_readme(data: pd.DataFrame, repo_id: str):
    """Generate a README markdown text for the dataset with truncated values.
    Handles mixed types and unhashable objects safely.
    """
    if not isinstance(data, pd.DataFrame):
        return None

    # Get column memory usage separately
    mem_df = column_memory_usage(data)

    # Compute missing stats
    missing_count = data.isnull().sum()
    missing_rate = (missing_count / len(data) * 100).round(2).astype(str) + "%"

    # Handle duplicates safely - convert unhashable types to strings first
    safe_df = data.copy()

    # Convert potentially unhashable columns to string representation
    for col in safe_df.columns:
        col_dtype = safe_df[col].dtype
        if col_dtype == "object" or str(col_dtype) == "category":
            # Convert each value in the column to its string representation
            safe_df[col] = safe_df[col].astype(str)

    # Now safely compute duplicates
    try:
        duplicate_count = safe_df.duplicated().sum()
        duplicate_rate = f"{(duplicate_count / len(safe_df) * 100):.2f}%"
    except Exception:
        # Fallback if duplicated still fails
        duplicate_count = "N/A"
        duplicate_rate = "N/A"

    # Truncate long string values for preview
    preview_data = data.copy()
    for col in preview_data.select_dtypes(include=["object"]):
        try:
            preview_data[col] = preview_data[col].apply(lambda x: truncate_text(x) if x is not None else None)
        except Exception:
            # If truncation fails, convert to string and then truncate
            preview_data[col] = (
                preview_data[col].astype(str).apply(lambda x: truncate_text(x) if x is not None else None)
            )

    # Combine all stats
    stats_df = pd.DataFrame(
        {
            "Column": data.columns,
            "Memory Usage": mem_df.set_index("Column")["Readable Memory Usage"],
            "Dtype": mem_df.set_index("Column")["Dtype"],
            "Missing Count": missing_count.values,
            "Missing Rate": missing_rate.values,
        },
    ).reset_index(drop=True)

    # Add total row
    total_memory = human_readable_size(data.memory_usage(deep=True).sum())
    total_row = pd.DataFrame(
        [
            {"Column": "", "Memory Usage": "", "Dtype": "", "Missing Count": "", "Missing Rate": ""},
            {
                "Column": "**TOTAL**",
                "Memory Usage": total_memory,
                "Dtype": "N/A",
                "Missing Count": missing_count.sum(),
                "Missing Rate": f"{(missing_count.sum() / (len(data) * len(data.columns)) * 100):.2f}%",
            },
        ],
    )

    stats_df = pd.concat([stats_df, total_row], ignore_index=True)

    # Safely convert to markdown by handling possible errors
    try:
        stats_table = stats_df.to_markdown(index=False)
    except Exception:
        # Fallback if to_markdown fails
        stats_table = "Error generating stats table"

    try:
        # Safely generate head table, handling potential errors
        head_table = preview_data.head().to_markdown(index=False)
    except Exception:
        # Create a simpler fallback version if to_markdown fails
        head_table = "Error generating preview table"

    # Include safe column list representation
    try:
        columns_list = str(data.columns.tolist())
    except Exception:
        columns_list = "Error generating columns list"

    readme_text = f"""# {repo_id}
(Auto-generated from latest commit)

## Using Dataset:

```python
import unibox as ub
df = ub.loads("hf://{repo_id}").to_pandas()
```

## Row samples:

```
{data.shape}
{columns_list}
```

{head_table}

## Column statistics: 

{stats_table}

## Saving to dataset:

```python
import unibox as ub
ub.saves(df, "hf://{repo_id}")
```

(last updated: {pd.Timestamp.now()})
"""
    return readme_text


import pandas as pd
import numpy as np
import collections.abc

def summarize_dataframe(df: pd.DataFrame, repo_id: str,
                        sample_rows: int = 3, max_unique_for_freq: int = 20) -> str:
    sample_rows = int(sample_rows)  # Ensure it's an integer
    max_unique_for_freq = int(max_unique_for_freq)

    lines = []
    lines.append(f"🧱 DataFrame Shape: {df.shape[0]} rows × {df.shape[1]} columns")

    # Column types
    dtype_counts = df.dtypes.value_counts()
    lines.append("\n📦 Column Types:")
    for dtype, count in dtype_counts.items():
        lines.append(f"  - {dtype}: {count}")

    # Missing values
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        lines.append("\n⚠️ Missing Values:")
        for col, count in missing.items():
            percent = count / len(df) * 100
            lines.append(f"  - {col}: {count} missing ({percent:.2f}%)")
    else:
        lines.append("\n✅ No missing values")

    # Column-wise summaries
    lines.append("\n## Column Summaries:")
    for col in df.columns:
        col_data = df[col]
        dtype = col_data.dtype
        lines.append(f"\n→ {col} ({dtype})")

        if pd.api.types.is_numeric_dtype(col_data):
            desc = col_data.describe()
            parts = []
            for key in ['min', 'max', 'mean', 'std']:
                if key in desc:
                    val = desc[key]
                    if pd.notna(val):
                        parts.append(f"{key.capitalize()}: {val:.3f}" if isinstance(val, float) else f"{key.capitalize()}: {val}")
            if parts:
                lines.append("  - " + ", ".join(parts))
            else:
                lines.append("  - No valid numeric summary available")

        elif pd.api.types.is_bool_dtype(dtype):
            total = len(col_data)
            true_count = (col_data == True).sum()
            false_count = (col_data == False).sum()
            na_count = col_data.isna().sum()
            lines.append(f"  - True: {true_count} ({true_count/total:.2%}), "
                        f"False: {false_count} ({false_count/total:.2%})")
            if na_count > 0:
                lines.append(f"  - Missing: {na_count} ({na_count/total:.2%})")

        elif pd.api.types.is_object_dtype(dtype):
            # Handle object types that may include unhashable or long sequences
            sample_val = col_data.dropna().iloc[0] if not col_data.dropna().empty else None
            if isinstance(sample_val, (collections.abc.Sequence, np.ndarray, bytes)) and not isinstance(sample_val, str):
                example_type = type(sample_val).__name__
                lines.append(f"  - Contains unhashable type: {example_type}")
                if isinstance(sample_val, (list, np.ndarray)):
                    lengths = col_data.dropna().map(lambda x: len(x) if isinstance(x, (list, np.ndarray)) else None)
                    lengths = pd.to_numeric(lengths, errors='coerce').dropna()
                    if not lengths.empty:
                        lines.append(
                            f"    - Typical length: mean={lengths.mean():.2f}, "
                            f"min={lengths.min()}, max={lengths.max()}"
                        )
                    else:
                        lines.append("    - Could not determine typical length (non-numeric or empty)")
                continue

            unique_vals = col_data.dropna().unique()
            nunique = len(unique_vals)
            lines.append(f"  - Unique values: {nunique}")
            if nunique <= max_unique_for_freq:
                freqs = col_data.value_counts(dropna=False).head(max_unique_for_freq)
                for val, count in freqs.items():
                    percent = count / len(df) * 100
                    lines.append(f"    - {repr(val)}: {count} ({percent:.2f}%)")

        elif pd.api.types.is_datetime64_any_dtype(dtype):
            min_date = col_data.min()
            max_date = col_data.max()
            if pd.notna(min_date) and pd.notna(max_date):
                lines.append(f"  - Range: {min_date} → {max_date}")
            else:
                lines.append("  - Date range unavailable (contains all NaT)")

        else:
            lines.append("  - Unhandled dtype")

    if sample_rows > 0:
        lines.append(f"\n🧪 Sample Rows (first {sample_rows}):")
        try:
            lines.append(df.head(sample_rows).to_string(index=False))
        except Exception as e:
            lines.append(f"  [Error printing sample rows: {e}]")

    return "\n".join(lines)


import pandas as pd
import numpy as np
import collections.abc

import pandas as pd
import numpy as np
import collections.abc

def generate_dataset_summary(
    df: pd.DataFrame,
    repo_id: str,
    sample_rows: int = 3,
    max_unique_for_freq: int = 20
) -> str:
    """
    Generate a combined dataset summary markdown text that merges:
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
        """
        Compute per-column memory usage. Returns a DataFrame with:
          Column, Dtype, Memory Usage (bytes), and Readable Memory Usage.
        """
        usage_info = []
        for col in df.columns:
            try:
                col_bytes = df[col].memory_usage(deep=True)
            except Exception:
                # Fallback in case deep=True fails for any reason
                col_bytes = df[col].memory_usage(deep=False)
            usage_info.append({
                "Column": col,
                "Dtype": str(df[col].dtype),
                "Memory Usage (bytes)": col_bytes,
                "Readable Memory Usage": human_readable_size(col_bytes)
            })
        return pd.DataFrame(usage_info)

    def truncate_text(text, max_len=50):
        """Truncate text to a max length for preview."""
        if not isinstance(text, str):
            text = str(text)
        return text if len(text) <= max_len else text[: max_len - 3] + "..."

    def compute_duplicates_count(df: pd.DataFrame) -> (int, str):
        """
        Compute duplicated row count and duplicate rate (%) in a dataframe.
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

    # -------------------------------------------------------------
    # 2) Build robust column summaries
    # -------------------------------------------------------------
    def build_robust_column_summaries(df: pd.DataFrame) -> str:
        lines = []
        lines.append("## Column Summaries:")

        for col in df.columns:
            col_data = df[col]
            dtype = col_data.dtype
            lines.append(f"\n→ {col} ({dtype})")

            # Numeric
            if pd.api.types.is_numeric_dtype(col_data) and not pd.api.types.is_bool_dtype(col_data):
                desc = col_data.describe()
                parts = []
                for key in ["min", "max", "mean", "std"]:
                    if key in desc:
                        val = desc[key]
                        if pd.notna(val):
                            parts.append(
                                f"{key.capitalize()}: {val:.3f}" 
                                if isinstance(val, float) else f"{key.capitalize()}: {val}"
                            )
                if parts:
                    lines.append("  - " + ", ".join(parts))
                else:
                    lines.append("  - No valid numeric summary available")

            # Booleans
            elif pd.api.types.is_bool_dtype(col_data):
                total = len(col_data)
                true_count = (col_data == True).sum()
                false_count = (col_data == False).sum()
                na_count = col_data.isna().sum()

                lines.append(f"  - True: {true_count} ({true_count/total:.2%}), "
                             f"False: {false_count} ({false_count/total:.2%})")
                if na_count > 0:
                    lines.append(f"  - Missing: {na_count} ({na_count/total:.2%})")

            # Datetime
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                min_date = col_data.min()
                max_date = col_data.max()
                if pd.notna(min_date) and pd.notna(max_date):
                    lines.append(f"  - Range: {min_date} → {max_date}")
                else:
                    lines.append("  - Date range unavailable (all NaT?)")

            # Object or fallback
            else:
                # Check if first non-null entry is unhashable
                sample_val = col_data.dropna().iloc[0] if not col_data.dropna().empty else None
                if (isinstance(sample_val, (collections.abc.Sequence, np.ndarray, bytes))
                        and not isinstance(sample_val, str)):
                    # It's an unhashable sequence-like
                    example_type = type(sample_val).__name__
                    lines.append(f"  - Contains unhashable type: {example_type}")
                    if isinstance(sample_val, (list, np.ndarray)):
                        lengths = col_data.dropna().map(
                            lambda x: len(x) if isinstance(x, (list, np.ndarray)) else None
                        )
                        lengths = pd.to_numeric(lengths, errors='coerce').dropna()
                        if not lengths.empty:
                            lines.append(
                                f"    - Typical length: mean={lengths.mean():.2f}, "
                                f"min={lengths.min()}, max={lengths.max()}"
                            )
                        else:
                            lines.append("    - Could not determine typical length (non-numeric or empty)")
                else:
                    # Normal object dtype
                    unique_vals = col_data.dropna().unique()
                    nunique = len(unique_vals)
                    lines.append(f"  - Unique values: {nunique}")
                    if nunique <= max_unique_for_freq:
                        freqs = col_data.value_counts(dropna=False).head(max_unique_for_freq)
                        for val, count in freqs.items():
                            percent = count / len(df) * 100
                            lines.append(f"    - {repr(val)}: {count} ({percent:.2f}%)")

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
    stats_df = pd.DataFrame({
        "Column": df.columns,
        "Dtype": mem_df["Dtype"],
        "Memory Usage": mem_df["Readable Memory Usage"],
        "Missing Count": missing_count.values,
        "Missing Rate": missing_rate.values
    })

    # Add a total row at the bottom
    total_row = pd.DataFrame([
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
            "Missing Rate": f"{(missing_count.sum() / (len(df)*len(df.columns))*100):.2f}%",
        }
    ])

    stats_df = pd.concat([stats_df, total_row], ignore_index=True)

    # Safely convert stats_df to a markdown table
    try:
        stats_table = stats_df.to_markdown(index=False)
    except Exception:
        stats_table = "Error generating stats table."

    # -------------------------------------------------------------
    # 4) Build column summaries
    # -------------------------------------------------------------
    column_summaries_text = build_robust_column_summaries(df)

    # -------------------------------------------------------------
    # 5) Build a safe sample preview
    # -------------------------------------------------------------
    preview_df = df.copy()

    # Truncate long object columns for preview
    for col in preview_df.select_dtypes(include=["object"]):
        try:
            preview_df[col] = preview_df[col].apply(
                lambda x: truncate_text(x) if x is not None else None
            )
        except Exception:
            # If something fails, coerce to string and then truncate
            preview_df[col] = preview_df[col].astype(str).apply(
                lambda x: truncate_text(x) if x else None
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