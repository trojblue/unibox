import os

import pytest

import unibox as ub


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
            "hf://incantor/aesthetic_eagle_5category_iter99",
            True,
            False,
            id="HuggingFace Dataset",
        ),
        # S3 file scenario
        pytest.param(
            "s3://bucket-external/misc/yada_store/configs/clip_prompts_list_full_v2.txt",
            True,
            False,
            id="S3 Text File",
        ),
    ],
)
def test_loads_and_saves(uri: str, expected_non_empty, is_image, tmp_path):
    """Test loader functionality for various URIs, including saving and reloading.

    Parameters:
        uri: The URI to load the file or dataset.
        expected_non_empty: Whether the loaded result should be non-empty.
        is_image: Whether the file is an image.
        tmp_path: Temporary directory provided by pytest for saving test files.
    """
    # Load the URI
    loaded_data = ub.loads(uri)

    # Validate the loaded content
    if expected_non_empty:
        assert loaded_data is not None, f"Loaded data from {uri} is None"
        if not is_image:
            assert len(loaded_data) > 0, f"Loaded data from {uri} is empty"

    # Save the loaded content to a new location
    uri = str(uri)
    if uri.startswith("hf://"):
        save_uri = "hf://datatmp/unibox-debug-repo"
    elif uri.startswith("s3://"):
        save_uri = "s3://dataset-ingested/temp/unibox_debug/" + os.path.basename(uri)
    else:
        save_uri = tmp_path / f"saved_{os.path.basename(uri)}"

    save_uri = str(save_uri)
    ub.saves(loaded_data, save_uri)

    # Ensure the saved file or dataset exists
    if not save_uri.startswith("hf://") and not save_uri.startswith("s3://"):
        assert os.path.exists(save_uri), f"Saved file {save_uri} does not exist"
        assert os.path.getsize(save_uri) > 0, f"Saved file {save_uri} is empty"

    # Reload the saved file or dataset
    reloaded_data = ub.loads(save_uri)

    # Validate the reloaded content
    assert reloaded_data is not None, f"Reloaded data from {save_uri} is None"
    if not is_image:
        assert len(reloaded_data) > 0, f"Reloaded data from {save_uri} is empty"
