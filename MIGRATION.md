Migration to Poetry
===================

This project migrated from a `requirements.txt`-based workflow to Poetry for dependency management.

Why Poetry
----------
- Reproducible, locked dependency graph via `poetry.lock`.
- Clear separation between main and development dependencies.
- Consistent local and Docker workflows.

How to Migrate a Local Environment
----------------------------------
1. Install Poetry
   - macOS/Linux: `curl -sSL https://install.python-poetry.org | python3 -`
   - Windows (PowerShell): `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`
   - Verify: `poetry --version`

2. Remove any old virtualenv you used for this project to avoid conflicts.

3. Install dependencies with Poetry (from project root):
   - `poetry install`

4. Activate the environment when working locally:
   - `poetry shell`

5. Run common tasks:
   - Migrations: `alembic upgrade head`
   - Run bot: `python main.py`

Command Mapping
---------------
- Install deps:
  - Before: `pip install -r requirements.txt`
  - Now: `poetry install`

- Add a runtime dependency:
  - Before: `pip install <pkg> && pip freeze > requirements.txt`
  - Now: `poetry add <pkg>`

- Add a dev dependency:
  - Before: `pip install <pkg> && pip freeze > requirements.txt`
  - Now: `poetry add -D <pkg>`

- Run scripts/commands:
  - Before: `python main.py`
  - Now: `poetry run python main.py` or within `poetry shell`: `python main.py`

Notes
-----
- The Docker image installs dependencies with Poetry and disables nested virtualenvs (`POETRY_VIRTUALENVS_CREATE=false`).
- Keep dependency versions aligned with `pyproject.toml`; lockfile (`poetry.lock`) ensures reproducible builds.
