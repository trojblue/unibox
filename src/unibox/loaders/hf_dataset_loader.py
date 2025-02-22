from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

import pandas as pd
from datasets import load_dataset

from .base_loader import BaseLoader


class HFDatasetLoader(BaseLoader):
    """Load datasets from Hugging Face hub."""

    SUPPORTED_LOAD_CONFIG = {
        "split",  # str: Which split to load (e.g., 'train', 'test')
        "revision",  # str: Git revision to use
        "to_pandas",  # bool: Whether to convert to pandas DataFrame
        "name",  # str: Dataset name/configuration
        "cache_dir",  # str: Where to cache the dataset
        "streaming",  # bool: Whether to stream the dataset
        "num_proc",  # int: Number of processes for loading
    }

    def load(self, file_path: Path, loader_config: Optional[Dict] = None) -> Union[pd.DataFrame, Any]:
        """Load a dataset from Hugging Face hub.

        Args:
            file_path (Path): Path-like string in format 'hf://dataset_id'
                            e.g., 'hf://huggingface/datasets/squad'
            loader_config (Optional[Dict]): Configuration options for dataset loading

        Returns:
            Union[pd.DataFrame, Any]: Dataset as DataFrame if to_pandas=True, otherwise
                                    as HuggingFace Dataset object
        """
        if not str(file_path).startswith("hf://"):
            raise ValueError("HFDatasetLoader requires path starting with 'hf://'")

        # Extract dataset_id from path
        dataset_id = str(file_path).replace("hf://", "")

        config = loader_config or {}
        used_keys: Set[str] = set()

        # Extract supported arguments from config
        kwargs = {}
        for key in self.SUPPORTED_LOAD_CONFIG - {"to_pandas"}:  # Handle to_pandas separately
            if key in config:
                kwargs[key] = config[key]
                used_keys.add(key)

        # Load the dataset
        dataset = load_dataset(dataset_id, **kwargs)

        # Convert to pandas if requested
        if config.get("to_pandas", False):
            used_keys.add("to_pandas")
            if isinstance(dataset, dict):
                # If multiple splits, convert each to DataFrame
                return {k: v.to_pandas() for k, v in dataset.items()}
            return dataset.to_pandas()

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "HFDatasetLoader")

        return dataset

    def save(self, file_path: Path, data: Any, loader_config: Optional[Dict] = None) -> None:
        """Saving to Hugging Face hub is not supported through this interface.

        For pushing datasets to the hub, please use the Dataset.push_to_hub() method directly.
        """
        raise NotImplementedError(
            "Saving to Hugging Face hub is not supported through this interface. "
            "Please use Dataset.push_to_hub() method directly.",
        )
