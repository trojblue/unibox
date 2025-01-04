from pathlib import Path

import pytest

import unibox as ub


@pytest.fixture
def test_folder(tmp_path):
    """Creates a temporary test folder with sample files for testing."""
    # Create test folder structure
    test_dir = tmp_path / "test_files"
    test_dir.mkdir()

    # Add sample files in the root directory
    extensions = ["jpg", "json", "parquet"]
    file_counts = {"jpg": 6, "json": 3, "parquet": 1}
    for ext, count in file_counts.items():
        for i in range(count):
            (test_dir / f"file_{i}.{ext}").touch()

    # Add a nested directory with a sample file
    nested_dir = test_dir / "nested"
    nested_dir.mkdir()
    (nested_dir / "nested_file.jpg").touch()

    return test_dir


@pytest.mark.parametrize("relative_unix, expected_relative", [(False, False), (True, True)])
def test_ls_paths(test_folder, relative_unix, expected_relative):
    """Test that ls() returns the correct paths (absolute or relative based on `relative_unix`)."""
    files = ub.ls(test_folder, relative_unix=relative_unix)

    # Ensure all paths are valid and have the correct type (absolute/relative)
    for file in files:
        path = Path(file)
        if expected_relative:
            assert not path.is_absolute(), f"Path {file} should be relative"
            if "nested/" in file:
                assert "/" in file, f"Nested path {file} should use Unix-style slashes"
        else:
            assert path.is_absolute(), f"Path {file} should be absolute"


def test_ls_exts(test_folder):
    """Test that ls() filters files correctly by extensions."""
    # Filter for jpg and json files
    files = ub.ls(test_folder, exts=["jpg", "json"])

    # Ensure all files have the correct extensions
    allowed_exts = {".jpg", ".json"}
    for file in files:
        assert Path(file).suffix in allowed_exts, f"File {file} has an unexpected extension"

    # Ensure the total number of files is correct
    assert len(files) == 6 + 3 + 1, "Incorrect number of files returned for extensions jpg and json"


def test_ls_backward_compatibility(test_folder):
    """Test that traverses() raises a DeprecationWarning and returns the same result as ls()."""
    with pytest.warns(DeprecationWarning):
        files_old = ub.traverses(test_folder, relative_unix=True)

    files_new = ub.ls(test_folder, relative_unix=True)

    # Ensure the results are identical
    assert files_old == files_new, "Results from traverses() and ls() should match"


def test_ls_absolute_paths(test_folder):
    """Test that ls() returns absolute paths when relative_unix=False."""
    files = ub.ls(test_folder, relative_unix=False)

    # Ensure all paths are absolute
    for file in files:
        assert Path(file).is_absolute(), f"Path {file} is not absolute"


def test_ls_relative_unix(test_folder):
    """Test that ls() returns relative Unix-style paths when relative_unix=True."""
    files = ub.ls(test_folder, relative_unix=True)

    # Ensure all paths are relative and use Unix-style slashes
    for file in files:
        path = Path(file)
        assert not path.is_absolute(), f"Path {file} should be relative"
        if "nested/" in file:
            assert "/" in file, f"Nested path {file} should use Unix-style slashes"


def test_ls_with_exts(test_folder):
    """Test that ls() correctly filters by extensions."""
    # Filter only for jpg files
    files = ub.ls(test_folder, exts=["jpg"])

    # Ensure all returned files have the correct extension
    for file in files:
        assert file.endswith(".jpg"), f"File {file} does not have the expected extension"

    # Ensure the correct number of jpg files is returned
    assert len(files) == 6 + 1, "Incorrect number of jpg files returned"
