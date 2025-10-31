# Repository Guidelines

## Project Structure & Module Organization
- Core services live in `podfilter/`: `app.py` wires the Litestar app, `auth.py` handles JWT auth, and `database.py` owns the async SQLite engine.
- Feature logic is split across `podfilter/routes/` (REST and UI routes) and `podfilter/models/` (SQLAlchemy models). Import new routers in `podfilter/app.py`.
- Templates render from `podfilter/templates/` and static assets load from `podfilter/static/`; shared helpers sit in `podfilter/utils.py`.
- `run.py` starts the development server, pointing to the default `podfilter.db` file in the repo root.

## Environment Setup
- Use Python 3.13. Create an isolated env with `python -m venv .venv && source .venv/bin/activate`.
- Install project and dev tooling via `pip install -e .[dev]`.
- Override configuration (for example `DATABASE_URL`) through environment variables or a local `.env` ignored by Git.

## Build, Test, and Development Commands
- `python run.py` — launch the Litestar app with uvicorn and hot reload.
- `robot acceptance/suites` — run the end to end tests located in `acceptance/`.
- `pytest tests/` — execute unit tests in `tests/` folder.
- `ruff check podfilter tests` — lint; auto-fix when possible using `ruff check --fix`.
- `ruff format .` or `black podfilter tests` — apply the shared 130-character formatting profile.
- `mypy podfilter` — execute the strict typing gate before opening a pull request.

## Coding Style & Naming Conventions
- Follow 2-space indentation, 130-character lines, and double quotes as enforced by the repo tooling.
- Use `snake_case` for functions and modules, `PascalCase` for classes, and uppercase for module-level constants.
- Type hints are required for all new interfaces; if you must suppress a check, add a concise justification after `# type: ignore`.

## Testing Guidelines
- Place tests in `tests/` named `test_<feature>.py`; mark async cases with `pytest.mark.asyncio`.
- Cover both success and error paths for new features, using shared fixtures or factories where possible.
- Run `pytest -k <keyword>` while iterating, then ensure `pytest` passes cleanly before requesting review.

## Commit & Pull Request Guidelines
- Match the existing Conventional Commit format (`type(scope): summary`), for example `chore(ci): update ruff config`.
- Keep commits focused; document context, testing, and linked issues in the PR description.
- Attach screenshots or sample payloads when changing UI templates or API schemas.
- When creatin a feature or a bug request, always file it into github repository.

## Security & Configuration Tips
- Store secrets in your shell environment or `.env`; never commit access tokens, feed URLs tied to users, or raw exports.
- Use sanitized sample feeds when sharing reproduction steps, and remove personal data from logs before uploading.
