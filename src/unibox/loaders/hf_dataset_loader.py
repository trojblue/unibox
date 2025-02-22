import logging
from typing import Any, Dict, Optional

import pandas as pd
from datasets import Dataset, load_dataset

from unibox.utils.df_utils import generate_dataset_readme
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

        if to_pandas:
            return load_dataset(repo_id, split=split, revision=revision).to_pandas()
        return load_dataset(repo_id, split=split, revision=revision)

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

        readme_text = None  # if not a dataframe, we don't generate a readme update

        # Convert DataFrame to Dataset if needed
        if isinstance(data, pd.DataFrame):
            readme_text = generate_dataset_readme(data, repo_id)
            data = Dataset.from_pandas(data)
        elif not isinstance(data, Dataset):
            raise ValueError("Data must be either a pandas DataFrame or a HuggingFace Dataset")

        # Save to huggingface
        try:
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
                logger.error(f"Failed to update README for dataset {hf_uri}: {e}")
                raise
