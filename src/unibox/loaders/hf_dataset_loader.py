import logging
from typing import Any, Dict, Optional

import pandas as pd
from datasets import Dataset, DatasetDict, Image as DSImage, load_dataset

from unibox.utils.df_utils import coerce_json_like_to_df, generate_dataset_summary
from unibox.utils.utils import parse_hf_uri

from ..backends.hf_hybrid_backend import HuggingfaceHybridBackend
from .base_loader import BaseLoader

logger = logging.getLogger(__name__)


class HFDatasetLoader(BaseLoader):
    """Loader for HuggingFace datasets using the datasets library.
    This loader handles only the data format conversion between DataFrame/Dataset objects
    and local dataset files. Remote operations are handled by the HF backends.
    """

    SUPPORTED_LOAD_CONFIG = {
        "split",  # str: Which split to load (e.g., 'train', 'test')
        "revision",  # str: Git revision to use
        "to_pandas",  # bool: Whether to convert to pandas DataFrame
        "name",  # str: Dataset name/configuration
        "cache_dir",  # str: Where to cache the dataset
        "streaming",  # bool: Whether to stream the dataset
        "num_proc",  # int: Number of processes for loading
    }

    def __init__(self):
        super().__init__()
        self.hf_api_backend = HuggingfaceHybridBackend()
        self._max_rows_for_df_summary = 200_000

    def load(self, local_path: str, loader_config: Optional[Dict] = None) -> Any:
        """Load a dataset from a local path or cache.

        Args:
            local_path (Union[str, Path]): Local path to dataset files
            loader_config (Optional[Dict]): Configuration options for dataset loading
                split (str): Which split to load (default: None, loads all splits)
                revision (str): Git revision to use
                to_pandas (bool): Whether to convert to pandas DataFrame
                name (str): Dataset name/configuration
                cache_dir (str): Where to cache the dataset
                streaming (bool): Whether to stream the dataset
                num_proc (int): Number of processes for loading

        Returns:
            Union[Dataset, Dict[str, Dataset], pd.DataFrame]: The loaded dataset
                If to_pandas=True, returns DataFrame
                If split is specified, returns Dataset
                Otherwise returns Dict[split_name, Dataset]
        """
        if not loader_config:
            loader_config = {}

        to_pandas = loader_config.get("to_pandas", False)
        repo_id, subpath = parse_hf_uri(local_path)
        split = loader_config.get("split", "train")
        revision = loader_config.get("revision", "main")
        # num_proc = loader_config.get("num_proc", 8)
        num_proc = 8

        if to_pandas:
            return load_dataset(repo_id, split=split, revision=revision, num_proc=num_proc).to_pandas()
        return load_dataset(repo_id, split=split, revision=revision, num_proc=num_proc)

    def save(self, hf_uri: str, data: Any, loader_config: Optional[Dict] = None) -> None:
        """Save data as a HuggingFace dataset to a local path.

        Args:
            local_path (Union[str, Path]): Local path to save dataset
            data (Union[Dataset, pd.DataFrame]): Dataset to save
            loader_config (Optional[Dict]): Configuration options
        """
        # Parse configs
        repo_id, _ = parse_hf_uri(hf_uri)
        if not loader_config:
            loader_config = {}

        dataset_split = loader_config.get("split", "train")
        is_private = loader_config.get("private", True)
        dict_key_column = loader_config.get("dict_key_column")
        value_column = loader_config.get("value_column")
        flatten_sep = loader_config.get("flatten_sep")
        max_depth = loader_config.get("max_depth")

        readme_text = None  # if not a dataframe, we don't generate a readme update

        # Convert JSON-like input to DataFrame if needed
        if isinstance(data, (dict, list, tuple)):
            try:
                data = coerce_json_like_to_df(
                    data,
                    dict_key_column=dict_key_column,
                    value_column=value_column,
                    flatten_sep=flatten_sep,
                    max_depth=max_depth,
                )
            except Exception as e:
                raise ValueError(
                    f"Cannot convert JSON-like input to DataFrame for HF dataset save: {e}",
                ) from e

        # Convert DataFrame to Dataset if needed and prepare README
        if isinstance(data, pd.DataFrame):
            if "__index_level_0__" in data.columns:
                data.drop(columns=["__index_level_0__"], inplace=True)
            try:
                readme_text = generate_dataset_summary(data, repo_id)
            except Exception as e:
                logger.warning(f"Failed to generate dataset summary for {hf_uri}: {e}")
                readme_text = None
            data = Dataset.from_pandas(data)
        elif isinstance(data, Dataset):
            try:
                readme_text = self._generate_hf_readme_for_datasets(repo_id, data)
            except Exception as e:
                logger.warning(f"Failed to generate dataset card for {hf_uri}: {e}")
                readme_text = None
        elif isinstance(data, DatasetDict):
            try:
                readme_text = self._generate_hf_readme_for_datasets(repo_id, data)
            except Exception as e:
                logger.warning(f"Failed to generate dataset card for {hf_uri}: {e}")
                readme_text = None
        else:
            raise ValueError("Data must be a pandas DataFrame, datasets.Dataset, or datasets.DatasetDict")

        # Save to Hugging Face Hub
        try:
            if isinstance(data, DatasetDict):
                for split_name, split_ds in data.items():
                    split_to_use = split_name
                    try:
                        split_ds.push_to_hub(
                            repo_id=repo_id,
                            private=is_private,
                            split=split_to_use,
                        )
                        logger.debug(f"Saved split '{split_to_use}' to {hf_uri}")
                    except Exception as e:
                        logger.error(f"Failed to save split '{split_to_use}' to {hf_uri}: {e}")
                        raise
            else:
                data.push_to_hub(
                    repo_id=repo_id,
                    private=is_private,
                    split=dataset_split,
                )
                logger.debug(f"Successfully saved dataset to {hf_uri}")
        except Exception as e:
            logger.error(f"Failed to save dataset to {hf_uri}: {e}")
            raise

        # Update the README if needed
        if readme_text:
            try:
                self.hf_api_backend.update_readme(repo_id, readme_text, repo_type="dataset")
                logger.info(f"Successfully updated README for dataset {hf_uri}")
            except Exception as e:
                logger.warning(f"Failed to update README for dataset {hf_uri}: {e}")
                # Non-fatal

    def _generate_hf_readme_for_datasets(self, repo_id: str, data: Any) -> str:
        """Generate a dataset card for Dataset or DatasetDict.

        Preference order:
        - If total rows <= threshold, convert to pandas and call generate_dataset_summary (nicer, exact)
        - Otherwise, fall back to a lightweight summary based on features and row counts
        """
        # 1) Try DataFrame-based summary if small enough
        try:
            if isinstance(data, Dataset):
                num_rows = getattr(data, "num_rows", None) or len(data)
                if num_rows <= self._max_rows_for_df_summary:
                    df = data.to_pandas()
                    return generate_dataset_summary(df, repo_id)
            elif isinstance(data, DatasetDict):
                # Sum total rows across splits
                total_rows = 0
                for split_ds in data.values():
                    total_rows += getattr(split_ds, "num_rows", None) or len(split_ds)
                if total_rows <= self._max_rows_for_df_summary:
                    dfs = []
                    for split_name, split_ds in data.items():
                        split_df = split_ds.to_pandas()
                        split_df["split"] = split_name
                        dfs.append(split_df)
                    combined_df = pd.concat(dfs, ignore_index=True)
                    return generate_dataset_summary(combined_df, repo_id)
        except Exception as e:
            logger.warning(f"Falling back to lightweight README generation for {repo_id}: {e}")

        # 2) Lightweight summary fallback (no full DF conversion)
        def feature_to_str(feat_key: str, feat_obj: Any) -> str:
            try:
                if isinstance(feat_obj, DSImage):
                    return f"{feat_key}: Image"
                return f"{feat_key}: {str(feat_obj).split('(')[0]}"
            except Exception:
                return f"{feat_key}: {type(feat_obj).__name__}"

        lines = [f"# {repo_id}", "(Auto-generated summary)", ""]
        if isinstance(data, Dataset):
            num_rows = getattr(data, "num_rows", None) or len(data)
            features = getattr(data, "features", {})
            lines.append("## Split")
            lines.append(f"- Rows: {num_rows}")
            if features:
                lines.append("- Features:")
                for k, v in features.items():
                    lines.append(f"  - {feature_to_str(k, v)}")
        elif isinstance(data, DatasetDict):
            lines.append("## Splits")
            for split_name, split_ds in data.items():
                num_rows = getattr(split_ds, "num_rows", None) or len(split_ds)
                features = getattr(split_ds, "features", {})
                lines.append(f"### {split_name}")
                lines.append(f"- Rows: {num_rows}")
                if features:
                    lines.append("- Features:")
                    for k, v in features.items():
                        lines.append(f"  - {feature_to_str(k, v)}")

        lines.append("")
        lines.append("## Usage Example:")
        lines.append("")
        lines.append("```python")
        lines.append("import unibox as ub")
        lines.append(f"ds = ub.loads(\"hf://{repo_id}\")")
        lines.append("```")
        lines.append("")
        lines.append("## Saving:")
        lines.append("")
        lines.append("```python")
        lines.append("import unibox as ub")
        lines.append(f"ub.saves(ds, \"hf://{repo_id}\")")
        lines.append("```")
        lines.append("")
        return "\n".join(lines)
