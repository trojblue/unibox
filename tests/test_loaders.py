import os
import pytest
from pathlib import Path
from PIL import Image

import unibox as ub


@pytest.mark.parametrize(
    "file_name, expected_non_empty, is_image",
    [
        ("sample.csv", True, False),
        ("sample.parquet", True, False),
        ("sample.txt", True, False),
        # ub.loads(some_image) returns an opened image file descriptor, which could lead to resource warnings.
        # We ignore these warnings for this test.
        pytest.param("sample.jpg", False, True, marks=pytest.mark.filterwarnings("ignore::ResourceWarning")),
        ("sample.jsonl", True, False),
        ("sample.json", True, False),
    ],
)
def test_local_loads_and_saves(file_name, expected_non_empty, is_image, tmp_path):
    """Test loader functionality for various file types, including saving and reloading.

    Parameters:
        file_name: Name of the sample file.
        expected_non_empty: Whether the file should produce a non-empty result when loaded.
        is_image: Whether the file is an image.
        tmp_path: Temporary directory provided by pytest for saving test files.
    """
    # Path to this test file's directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    sample_file = os.path.join(test_dir, "test_files", file_name)

    # Ensure the file exists
    assert os.path.exists(sample_file), f"Sample file does not exist: {sample_file}"

    # Load the sample file
    loaded_data = ub.loads(sample_file)

    # Validate the loaded content
    if expected_non_empty:
        assert loaded_data is not None, f"Loaded data from {file_name} is None"
        if not is_image:
            assert len(loaded_data) > 0, f"Loaded data from {file_name} is empty"

    # Save the loaded content to a temporary path
    save_path = tmp_path / f"saved_{file_name}"
    ub.saves(loaded_data, save_path)

    # Ensure the saved file exists and is not empty
    assert save_path.exists(), f"Saved file {save_path} does not exist"
    assert save_path.stat().st_size > 0, f"Saved file {save_path} is empty"

    # Reload the saved file
    reloaded_data = ub.loads(save_path)

    # Validate the reloaded content
    assert reloaded_data is not None, f"Reloaded data from {save_path} is None"
    if not is_image:
        assert len(reloaded_data) > 0, f"Reloaded data from {save_path} is empty"
