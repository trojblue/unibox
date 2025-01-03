import os

import pytest
from PIL import Image

import unibox as ub


@pytest.mark.parametrize(
    "file_name, expected_non_empty",
    [
        ("sample.csv", True),
        ("sample.parquet", True),
        ("sample.txt", True),
        # ub.loads(some_imge) returns a opened image file descriptor instead of the actual file, which
        # could lead to resource warnings. We ignore these warnings for this test.
        pytest.param("sample.jpg", False, marks=pytest.mark.filterwarnings("ignore::ResourceWarning")),
        ("sample.jsonl", True),
        ("sample.json", True),
    ],
)
def test_local_loads(file_name, expected_non_empty):
    """Test loader functionality for various file types.

    Parameters:
        file_name: Name of the sample file.
        expected_non_empty: Whether the file should produce a non-empty result when loaded.
    """
    # Path to this test file's directory
    test_dir = os.path.dirname(os.path.abspath(__file__))

    # Relative path to the sample file
    sample_file = os.path.join(test_dir, "test_files", file_name)

    # Ensure the file exists
    assert os.path.exists(sample_file), f"Sample file does not exist: {sample_file}"

    # Load the file using ub.loads
    loaded_data = ub.loads(sample_file)

    # Handle specific cases for images
    if file_name.endswith(".jpg"):
        assert loaded_data is not None, f"Loaded data from {file_name} is None"
        assert isinstance(loaded_data, Image.Image), f"Loaded data from {file_name} is not an image"
    # General case
    elif expected_non_empty:
        assert loaded_data is not None, f"Loaded data from {file_name} is None"
        assert len(loaded_data) > 0, f"Loaded data from {file_name} is empty"
