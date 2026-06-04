import inspect
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

import unibox as ub
from unibox.loaders.cdc_parquet_loader import CdcParquetLoader
from unibox.loaders.hf_dataset_loader import HFDatasetLoader
from unibox.loaders.loader_router import get_loader_for_path


class FakeProgressBar:
    def __init__(self, n: int, total: int):
        self.n = n
        self.total = total
        self.description = None
        self.refreshed = False

    def update(self, value: int) -> None:
        self.n += value

    def set_description(self, value: str, refresh: bool = True) -> None:
        self.description = value

    def refresh(self) -> None:
        self.refreshed = True


class FakeXetProgressReporter:
    def __init__(self):
        self.data_processing_bar = FakeProgressBar(n=158, total=162)
        self.upload_bar = FakeProgressBar(n=133, total=133)
        self.per_file_progress = True
        self.current_bars = [FakeProgressBar(n=158, total=162)]
        self.known_items = {"data/train-00000-of-00001.parquet"}
        self.completed_items = set()
        self.total_files = None
        self.notified_complete = False

    def format_desc(self, name: str, indent: bool) -> str:
        return name

    def notify_upload_complete(self) -> None:
        self.notified_complete = True

    def update_progress(self, total_update: SimpleNamespace, item_updates: list[SimpleNamespace]) -> None:
        raise AssertionError("The test only needs this as a bound callback")


@pytest.mark.parametrize(
    "uri, expected_non_empty, is_image",
    [
        # Local file tests
        ("tests/test_files/sample.csv", True, False),
        ("tests/test_files/sample.parquet", True, False),
        ("tests/test_files/sample.txt", True, False),
        pytest.param(
            "tests/test_files/sample.jpg",
            False,
            True,
            marks=pytest.mark.filterwarnings("ignore::ResourceWarning"),
        ),
        ("tests/test_files/sample.jsonl", True, False),
        ("tests/test_files/sample.json", True, False),
        # HuggingFace dataset scenario
        pytest.param(
            "hf://trojblue/test-anime-rating-v3-partial",
            True,
            False,
            id="HuggingFace Dataset",
        ),
        # S3 file scenario
        pytest.param(
            "s3://dataset-ingested/temp/unibox_debug/clip_prompts_list_full_v2.txt",
            True,
            False,
            id="S3 Text File",
        ),
    ],
)
def test_loads_and_saves(uri: str, expected_non_empty: bool, is_image: bool, tmp_path: Path) -> None:
    """Test loading and saving files with different loaders."""
    # Load the data
    data = ub.loads(uri)
    assert data is not None
    if expected_non_empty:
        assert len(data) > 0

    # Skip save tests for images and remote datasets
    if is_image or uri.startswith(("hf://", "s3://")):
        return

    # Get the appropriate loader
    local_path = Path(uri)
    loader = get_loader_for_path(local_path)
    assert loader is not None

    # Save to a temporary file
    save_path = tmp_path / local_path.name
    ub.saves(data, save_path)

    # Load back and verify
    reloaded = ub.loads(save_path)
    if hasattr(data, "equals"):  # pandas DataFrame
        assert data.equals(reloaded)
    else:  # other types
        assert data == reloaded


def test_saves_creates_parent_dir(tmp_path: Path) -> None:
    data = {"hello": "world"}
    save_path = tmp_path / "nested" / "dir" / "sample.json"

    ub.saves(data, save_path)

    assert save_path.exists()
    assert ub.loads(save_path) == data


def test_cdc_parquet_roundtrip(tmp_path: Path) -> None:
    if "use_content_defined_chunking" not in inspect.signature(pd.DataFrame.to_parquet).parameters:
        pytest.skip("Parquet CDC not supported by installed pandas/pyarrow.")

    df = pd.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})
    save_path = tmp_path / "sample.cdc.parquet"

    loader = get_loader_for_path(save_path)
    assert isinstance(loader, CdcParquetLoader)

    ub.saves(df, save_path)
    reloaded = ub.loads(save_path)

    assert df.equals(reloaded)

    alias_path = tmp_path / "sample_alias.parquet"
    ub.saves(df, alias_path, cdc=True)
    alias_reloaded = ub.loads(alias_path)

    assert df.equals(alias_reloaded)


def test_hf_xet_upload_progress_finalizer_completes_successful_upload_bars() -> None:
    reporter = FakeXetProgressReporter()

    HFDatasetLoader._finalize_hf_xet_upload_progress(reporter.update_progress)

    assert reporter.data_processing_bar.n == reporter.data_processing_bar.total
    assert reporter.upload_bar.n == reporter.upload_bar.total
    assert reporter.current_bars[0].n == reporter.current_bars[0].total
    assert reporter.completed_items == reporter.known_items
    assert reporter.data_processing_bar.description == "Processing Files (1 / 1)"
    assert reporter.notified_complete
