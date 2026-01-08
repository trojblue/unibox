from unibox.utils.utils import parse_hf_uri


def test_parse_hf_uri_basic() -> None:
    parts = parse_hf_uri("hf://org/repo")
    assert parts.repo_id == "org/repo"
    assert parts.path_in_repo == ""
    assert parts.revision is None
    assert parts.repo_type == "model"


def test_parse_hf_uri_with_path() -> None:
    parts = parse_hf_uri("hf://org/repo/path/to/file.txt")
    assert parts.repo_id == "org/repo"
    assert parts.path_in_repo == "path/to/file.txt"
    assert parts.revision is None


def test_parse_hf_uri_with_revision() -> None:
    parts = parse_hf_uri("hf://org/repo@rev")
    assert parts.repo_id == "org/repo"
    assert parts.path_in_repo == ""
    assert parts.revision == "rev"


def test_parse_hf_uri_with_dataset_prefix() -> None:
    parts = parse_hf_uri("hf://datasets/org/repo")
    assert parts.repo_type == "dataset"
    assert parts.repo_id == "org/repo"


def test_parse_hf_uri_unpacking() -> None:
    repo_id, subpath = parse_hf_uri("hf://org/repo/path")
    assert repo_id == "org/repo"
    assert subpath == "path"
