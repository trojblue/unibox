from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

import pandas as pd
from datasets import Dataset, load_dataset

from .base_loader import BaseLoader

import logging
logger = logging.getLogger(__name__)


class HFDatasetLoader(BaseLoader):
    """Loader for HuggingFace datasets using the datasets library."""

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
        """Load a dataset from HuggingFace hub.
        
        Args:
            local_path (Union[str, Path]): Path in format 'hf://owner/repo'
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
        uri = str(local_path)
        if not uri.startswith("hf://"):
            raise ValueError("HFDatasetLoader requires path starting with 'hf://'")

        # Extract dataset_id from path (remove hf:// prefix)
        dataset_id = uri[5:].strip("/")
        
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Extract supported arguments from config
        kwargs = {}
        for key in self.SUPPORTED_LOAD_CONFIG - {"to_pandas"}:  # Handle to_pandas separately
            if key in config:
                kwargs[key] = config[key]
                used_keys.add(key)

        # Load the dataset
        try:
            dataset = load_dataset(dataset_id, **kwargs)
            logger.debug(f"Successfully loaded dataset: {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to load dataset {dataset_id}: {e}")
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
        """Push a dataset to the HuggingFace hub.
        
        Args:
            local_path (Union[str, Path]): Target path in format 'hf://owner/repo'
            data (Union[Dataset, pd.DataFrame]): Dataset to push
            loader_config (Optional[Dict]): Configuration options
                private (bool): Whether to create a private repository
                token (str): HuggingFace token for authentication
                split (str): Dataset split name (default: 'train')
        """
        uri = str(local_path)
        if not uri.startswith("hf://"):
            raise ValueError("HFDatasetLoader requires path starting with 'hf://'")

        # Extract repo_id from path (remove hf:// prefix)
        repo_id = uri[5:].strip("/")
        
        config = loader_config or {}
        
        # Convert DataFrame to Dataset if needed
        if isinstance(data, pd.DataFrame):
            data = Dataset.from_pandas(data)
        elif not isinstance(data, Dataset):
            raise ValueError("Data must be either a pandas DataFrame or a HuggingFace Dataset")

        # Push to hub
        split = config.get("split", "train")
        private = config.get("private", True)
        token = config.get("token", None)
        
        try:
            data.push_to_hub(
                repo_id,
                split=split,
                private=private,
                token=token,
            )
            logger.debug(f"Successfully pushed dataset to {repo_id}")
        except Exception as e:
            logger.error(f"Failed to push dataset to {repo_id}: {e}")
            raise
