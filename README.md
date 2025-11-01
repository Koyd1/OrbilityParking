# Sigmoid2025 Python Scaffold

This repository now contains a minimal Python package so you can start building features straight away.

## Getting Started

1. Ensure you have Python 3.10 or newer available. The repository was bootstrapped using Python 3.12.
2. Create and activate a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the project in editable mode along with optional dev tools:
   ```bash
   pip install --upgrade pip
   pip install -e ".[dev]"
   ```
4. Run the example tests with `pytest`:
   ```bash
   pytest
   ```
!!!!!!
   ```bash
   python3 main.py
   ```

## Project Layout

- `pyproject.toml` — project metadata, dependencies, and build configuration.
- `src/sigmoid2025` — Python package source code (currently exposes a simple `greet` helper).
- `tests/` — pytest tests wired up via `pyproject.toml`.

Feel free to add more modules under `src/sigmoid2025/` and expand the test suite under `tests/`.
