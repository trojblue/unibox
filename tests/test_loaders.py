import unibox as ub
import pytest
import os

@pytest.mark.parametrize("file_name, expected_non_empty", [
    ("sample.csv", True),
    ("sample.parquet", True),
    ("sample.txt", True),
    ("sample.jpg", False),  # Assuming image files won't produce non-empty dictionaries
    ("sample.jsonl", True),
    ("sample.json", True),
])
def test_local_loads(file_name, expected_non_empty):
    """
    Test loader functionality for various file types.
    
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
    
    # Check if the result is valid
    if expected_non_empty:
        assert loaded_data is not None, f"Loaded data from {file_name} is None"
        assert len(loaded_data) > 0, f"Loaded data from {file_name} is empty"
    else:
        assert loaded_data is not None, f"Loaded data from {file_name} is None"
