import logging
from uuid import uuid4

from unibox.utils.logger import UniLogger
from unibox.utils.utils import parse_hf_uri


def test_unilogger_reuses_existing_handlers(tmp_path) -> None:
    logger_name = f"test-unibox-{uuid4()}"
    first = UniLogger(output_dir=str(tmp_path), logger_name=logger_name)
    try:
        initial_handlers = list(first.logger.handlers)

        UniLogger(output_dir=str(tmp_path), logger_name=logger_name)
        UniLogger(output_dir=str(tmp_path), logger_name=logger_name)

        assert first.logger.handlers == initial_handlers
        assert sum(isinstance(handler, logging.FileHandler) for handler in initial_handlers) == 1
    finally:
        for handler in list(first.logger.handlers):
            first.logger.removeHandler(handler)
            handler.close()


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
