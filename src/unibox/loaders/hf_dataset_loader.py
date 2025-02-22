from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

import pandas as pd
from datasets import Dataset, load_dataset

from .base_loader import BaseLoader

import logging
logger = logging.getLogger(__name__)


class HFDatasetLoader(BaseLoader):
    """Loader for HuggingFace datasets using the datasets library.
    This loader handles only the data format conversion between DataFrame/Dataset objects
    and local dataset files. Remote operations are handled by the HF backends."""

    SUPPORTED_LOAD_CONFIG = {
        "split",  # str: Which split to load (e.g., 'train', 'test')
        "revision",  # str: Git revision to use
        "to_pandas",  # bool: Whether to convert to pandas DataFrame
        "name",  # str: Dataset name/configuration
        "cache_dir",  # str: Where to cache the dataset
        "streaming",  # bool: Whether to stream the dataset
        "num_proc",  # int: Number of processes for loading
    }

    def load(self, local_path: Union[str, Path], loader_config: Optional[Dict] = None) -> Any:
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
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Extract supported arguments from config
        kwargs = {}
        for key in self.SUPPORTED_LOAD_CONFIG - {"to_pandas"}:  # Handle to_pandas separately
            if key in config:
                kwargs[key] = config[key]
                used_keys.add(key)

        # Load the dataset from local path
        try:
            dataset = Dataset.load_from_disk(str(local_path))
            logger.debug(f"Successfully loaded dataset from: {local_path}")
        except Exception as e:
            logger.error(f"Failed to load dataset from {local_path}: {e}")
            raise

        # Convert to pandas if requested
        if config.get("to_pandas", False):
            used_keys.add("to_pandas")
            try:
                if isinstance(dataset, dict):
                    # If multiple splits, convert each to DataFrame
                    return {k: v.to_pandas() for k, v in dataset.items()}
                return dataset.to_pandas()
            except Exception as e:
                logger.error(f"Failed to convert dataset to pandas: {e}")
                raise

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "HFDatasetLoader")

        return dataset

    def save(self, local_path: Union[str, Path], data: Any, loader_config: Optional[Dict] = None) -> None:
        """Save data as a HuggingFace dataset to a local path.
        
        Args:
            local_path (Union[str, Path]): Local path to save dataset
            data (Union[Dataset, pd.DataFrame]): Dataset to save
            loader_config (Optional[Dict]): Configuration options
        """
        # Convert DataFrame to Dataset if needed
        if isinstance(data, pd.DataFrame):
            data = Dataset.from_pandas(data)
        elif not isinstance(data, Dataset):
            raise ValueError("Data must be either a pandas DataFrame or a HuggingFace Dataset")

        # Save to local path
        try:
            data.save_to_disk(str(local_path))
            logger.debug(f"Successfully saved dataset to {local_path}")
        except Exception as e:
            logger.error(f"Failed to save dataset to {local_path}: {e}")
            raise
