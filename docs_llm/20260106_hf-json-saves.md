# HF Dataset Saves: JSON/JSONL Inputs (Plan)

## Goal
Enable `ub.saves("hf://...")` to accept JSON-ish inputs (dict, list of dicts, list of scalars) and upload them as Hugging Face datasets. The behavior should be robust for nested structures and mixed key types.

This doc defines the conversion rules, warning behavior for inconsistent inputs, and a minimal implementation plan.

## Scope
- Applies only when saving to an HF dataset URI (no subpath/extension), e.g. `hf://owner/repo`.
- Does **not** change file saves such as `hf://owner/repo/path/file.json` or `.jsonl` (those remain file saves).
- Conversion happens before the dataset is pushed to HF (same as current DataFrame/Dataset flows).

## Input Types & Conversion Rules

### 1) Single dict input
Example:
```python
{"a": 1, "b": {"c": 2}, 3: ["x", "y"]}
```
Conversion:
- Each key/value pair becomes one row.
- Add a `DICT_KEY` column as the first column; its value is the original key (no forced string coercion).
- If the value is a dict, merge it into the row (so keys in the value become columns).
- If the value is not a dict, place it in a `VALUE` column.
- After constructing rows, **flatten** nested dicts into columns (see Flattening section).

Notes:
- If a value is a list, keep it as a list cell (HF datasets support list feature types). No row explosion.
- Mixed key types are allowed; `DICT_KEY` stays as an object column.

### 2) List of dicts (JSONL-style)
Example:
```python
[{"id": 1, "meta": {"x": 10}}, {"id": 2, "meta": {"x": 20}}]
```
Conversion:
- Each dict becomes one row.
- Flatten nested dicts into columns (see Flattening section).

### 3) List of scalars
Example:
```python
["a", "b", "c"]
```
Conversion:
- Create a single-column DataFrame (column name `VALUE` or `item`).
- Each list item becomes a row.

### 4) Mixed list (dicts + scalars)
Example:
```python
[{"a": 1}, "b", 3]
```
Conversion:
- Normalize to a single-row schema by wrapping non-dicts as `{"VALUE": item}`.
- Flatten the result; dict rows may yield additional columns.

## Flattening Behavior
Introduce a small helper that flattens dicts into column-safe structures, with depth limits:
- For dict values, flatten at **most 2 levels** (depth 0 → 1 → 2).
- Anything deeper is serialized using `json.dumps(...)` to avoid exploding columns/rows.
- Lists are kept as-is in cells; they are not exploded or flattened.

Suggested approach:
- A helper like `flatten_value(value, max_depth=2, sep="__")` that returns either a scalar/list, or a flattened dict.
- A `flatten_record(record)` that applies `flatten_value` to dict values and returns a flat dict for row construction.
- Use `pandas.json_normalize` only after pre-flattening to avoid runaway column expansion.

## Inconsistent Input Warning
If the input is not a clean, easily convertible format (e.g., mixed list of scalars + dicts + incompatible types), still attempt conversion **following the rules above**, but emit a `warnings.warn(...)` noting the structure is inconsistent and may produce surprising columns. This should be a non-fatal warning.

## Error Handling
- If conversion fails outright, raise `ValueError` with a clear message (“Cannot convert JSON-like input to DataFrame for HF dataset save”).
- Keep existing behavior for DataFrame/Dataset/DatasetDict unchanged.
- Prefer robust fallback conversion paths; only raise when conversion is impossible.

## Proposed Implementation Plan
1) Add conversion utilities (likely `src/unibox/utils/df_utils.py`):
   - `flatten_value(value, max_depth=2, sep="__")`
   - `flatten_record(record, max_depth=2, sep="__")`
   - `coerce_json_like_to_df(data, dict_key_column="DICT_KEY", value_column="VALUE", flatten_sep="__")`
     - Handles dict, list/tuple, and scalars per rules above.
     - Emits a warning if input is inconsistent but still convertible.
2) Update `HFDatasetLoader.save` to accept dict/list inputs:
   - If `data` is dict or list/tuple, call the helper to obtain a DataFrame.
   - Continue with existing DataFrame → Dataset conversion and README generation.
3) Optional: expose config flags via `loader_config` (e.g., `dict_key_column`, `value_column`, `flatten_sep`, `max_depth`).

## Examples
```python
# dict input
ub.saves({"a": 1, "b": {"c": 2}}, "hf://me/my-ds")

# jsonl-style
ub.saves([{"id": 1}, {"id": 2}], "hf://me/my-ds")

# list of strings
ub.saves(["foo", "bar"], "hf://me/my-ds")

# mixed list (warns, but converts)
ub.saves([{"a": 1}, "b", 3], "hf://me/my-ds")
```

## Testing Notes (for later)
- dict with nested dict → DICT_KEY + flattened columns (depth limit enforced)
- dict with deep nesting → deeper levels JSON-dumped
- dict with list values → list preserved in VALUE column
- list of dicts → rows + flatten
- list of strings → single-column DataFrame
- mixed list → VALUE column + dict columns + warning
- inconsistent input → warning emitted, conversion succeeds
