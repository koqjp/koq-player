# Repository Guidelines

## Project Structure & Module Organization
- `koq/` holds the application package. Bot logic lives under `koq/player/`, with feature cogs in `koq/player/cogs/` and shared helpers in `koq/player/util/`.
- `run.py` is the local entrypoint that loads the initial cogs and starts the Discord bot.
- `tests/` contains pytest suites (see `tests/test_queue.py`).
- Configuration is loaded via Dynaconf from `settings.toml` and `.secrets.toml` (not committed). Docker/compose files live at the repo root.

## Build, Test, and Development Commands
- `uv sync` installs dependencies using the lockfile.
- `uv run python run.py` runs the bot locally with your configured secrets.
- `uv run pytest` executes the full test suite.
- `uv run pytest -m "not slow"` skips slow tests.
- `docker compose up --build` builds and runs the containerized service.

## Coding Style & Naming Conventions
- Python is the primary language; follow 4-space indentation and PEP 8 naming (`snake_case` functions/variables, `PascalCase` classes).
- Format with `black` and lint with `flake8` (both listed in `pyproject.toml`).
- Test files follow `test_*.py` or `*_test.py` and test functions are `test_*`.

## Testing Guidelines
- Pytest with `pytest-asyncio` is configured in `pyproject.toml` (`asyncio_mode=auto`).
- Use markers `slow` and `integration` for long-running or external-dependency tests.
- Keep unit tests close to the behavior in `koq/player/` and prefer isolated fixtures in `tests/conftest.py`.

## Commit & Pull Request Guidelines
- Recent commits favor short, imperative subjects (e.g., “Fix …”, “Add …”, “Bump … to …”).
- For dependency updates, follow the “Bump <name> to <version>” pattern.
- No PR template is present in `.github/`. Use a clear description, linked issue (if applicable), and test results. Include screenshots/log snippets for bot behavior changes.

## Security & Configuration Tips
- Never commit tokens or client IDs. Use `.secrets.toml` or `DYNACONF_*` env vars (`DYNACONF_TOKEN`, `DYNACONF_CLIENT_ID`).
- Verify permissions and scopes when generating the bot invite URL in `run.py`.
