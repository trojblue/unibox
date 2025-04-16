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

        elif pd.api.types.is_object_dtype(dtype) or pd.api.types.is_bool_dtype(dtype):
            sample_val = col_data.dropna().iloc[0] if not col_data.dropna().empty else None
            if isinstance(sample_val, (collections.abc.Sequence, np.ndarray, bytes)) and not isinstance(sample_val, str):
                example_type = type(sample_val).__name__
                lines.append(f"  - Contains unhashable type: {example_type}")
                if isinstance(sample_val, (list, np.ndarray)):
                    # inside the list/array-like handling block:
                    lengths = col_data.dropna().map(lambda x: len(x) if isinstance(x, (list, np.ndarray)) else None)
                    lengths = pd.to_numeric(lengths, errors='coerce')  # Convert to numbers, force invalid to NaN
                    lengths = lengths.dropna()  # Remove invalid entries
                    if not lengths.empty:
                        lines.append(f"    - Typical length: mean={lengths.mean():.2f}, min={lengths.min()}, max={lengths.max()}")
                    else:
                        lines.append(f"    - Could not determine typical length (non-numeric or empty)")

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
