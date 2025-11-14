# Repository Guidelines

This document is a concise contributor guide for the `unibox` repository. It applies to all code and docs under this directory.

## Project Structure & Module Organization

- Core library and CLI live in `src/unibox`, with subpackages like `backends`, `loaders`, and `utils`.
- Tests live in `tests`, mirroring the layout of `src/unibox` (for example, `src/unibox/loaders` has tests in `tests/test_loaders.py`).
- Documentation sources are in `docs` and built with MkDocs (`mkdocs.yml`), while project configuration lives in `pyproject.toml` and `Makefile`.

## Build, Test, and Development Commands

- `make test` – run the full Python test suite.
- `make lint` – run linters and style checks (see `Makefile` for tools in use).
- `make docs-serve` – serve the MkDocs documentation locally for preview.
- `python -m unibox --help` – show CLI usage for quick smoke checks.

## Coding Style & Naming Conventions

- Follow the style enforced by the configured tools in `pyproject.toml` and `Makefile` (e.g., `black`, `ruff`, or similar).
- Use 4-space indentation for Python; prefer explicit imports and module-level constants in `UPPER_SNAKE_CASE`.
- Name modules and packages in `lower_snake_case`; classes in `PascalCase`; functions, variables, and CLI options in `lower_snake_case`.

## Testing Guidelines

- Add or update tests in `tests` alongside any behavior change; mirror source structure where practical.
- Prefer small, focused tests using the existing pytest-based test suite (`conftest.py` contains shared fixtures).
- Run `make test` before opening a pull request; include regression tests for fixed bugs when possible.

## Commit & Pull Request Guidelines

- Write clear, imperative commit messages (for example, `Add loader for XYZ format`, `Fix CLI path handling`).
- Keep pull requests scoped and well-described: include the motivation, a brief summary of changes, and links to related issues.
- When changes affect behavior, tests, or docs, mention how you validated them (e.g., `make test`, `python -m unibox ...`, `make docs-serve`).

