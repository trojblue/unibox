from pathlib import Path

import pytest

import unibox as ub
from unibox.loaders.loader_router import get_loader_for_path


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
