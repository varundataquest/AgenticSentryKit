# Contributing to SentryKit

Thank you for considering a contribution! We welcome bug fixes, features, documentation improvements, and feedback.

## Development Environment

1. Create and activate a virtualenv
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies
   ```bash
   pip install -e ".[dev,docs]"
   ```
3. Run quality gates before submitting
   ```bash
   make fmt
   make lint
   make mypy
   make test
   make docs
   ```

## Coding Guidelines

* Follow the Ruff formatting and linting defaults configured in `pyproject.toml`.
* All new code must include type hints and pass `mypy --strict`.
* Prefer descriptive log messages using the structured logging helpers.
* Add unit tests covering new behavior; maintain ≥90% coverage.
* Document public APIs via docstrings so mkdocstrings can surface them.

## Pull Requests

* Link related issues and explain the problem solved.
* Include screenshots for UI changes (e.g., HTML report) when applicable.
* Update the changelog under the appropriate release heading.
* Ensure CI passes before requesting a review.

## Security

Do not share secrets or production data in issues or PRs. If you discover a vulnerability, please contact the maintainers directly instead of filing a public issue.
