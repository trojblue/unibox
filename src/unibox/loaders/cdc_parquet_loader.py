# cdc_parquet_loader.py
import inspect
import warnings
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from .parquet_loader import ParquetLoader


class CdcParquetLoader(ParquetLoader):
    """Load and save Parquet files with content-defined chunking enabled."""

    def save(self, file_path: Path, data: pd.DataFrame, loader_config: Optional[Dict] = None) -> None:
        if "use_content_defined_chunking" not in inspect.signature(pd.DataFrame.to_parquet).parameters:
            raise RuntimeError(
                "Parquet CDC requires pandas/pyarrow with use_content_defined_chunking support.",
            )

        config = dict(loader_config or {})

        if config.get("use_content_defined_chunking") is False or config.get("cdc") is False:
            warnings.warn(
                "CdcParquetLoader forces use_content_defined_chunking=True; overriding False.",
            )
        if "cdc" in config:
            config["cdc"] = True
        config["use_content_defined_chunking"] = True

        engine = config.get("engine")
        if engine and engine != "pyarrow":
            warnings.warn("CdcParquetLoader requires engine='pyarrow'; overriding.")
        config["engine"] = "pyarrow"

        super().save(file_path, data, loader_config=config)
