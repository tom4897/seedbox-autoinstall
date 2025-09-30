# Contributing

Thanks for your interest in improving this project! This guide keeps contributions fast and consistent.

## Getting started

- **Fork** the repo and **create a branch** from `main` (e.g., `feat/short-title` or `fix/bug-name`).
- Keep PRs **small and focused**. One logical change per PR is ideal.

## Development setup

- Python tools live under `scripts/`. If needed, install deps:
  - `python -m venv .venv && .venv\Scripts\activate` (Windows)
  - `pip install -r scripts/requirements.txt`
- Cloud-init content lives under `cloud-init/`. Treat those files as declarative config.
- Validation: see `scripts/validate_autoinstall.py` and related schema files.

## Coding standards

- **Python**: prefer type hints where reasonable; add concise docstrings; keep code readable.
- **Formatting/Linting**: if you use tools like Black/Ruff, run them before committing. Otherwise, match existing style.
- **YAML/Cloud-Init**: follow upstream cloud-init conventions; prefer explicit over clever.

## Commits and PRs

- Use clear commit messages:
- In PRs, include:
  - What changed and why (problem statement + solution summary)
  - Any validation output or screenshots where relevant
  - Docs updates (e.g., `README.md`) if behavior or usage changed

## Issues

- Open an issue with steps to reproduce, expected vs actual behavior, and environment details. Link to logs or configs when possible.

## License

By contributing, you agree your contributions are licensed under the repository’s `LICENSE`.
