# Repository Guidelines

## Project Structure & Module Organization
The FastAPI application lives in `app/main.py`. It defines the `RateLimiter` class, `RateLimitExceeded` exception + handler, and the `/your-endpoint` route. Tests reside in `tests/test_rate_limiter.py`, exercising quota behaviour via `fastapi.testclient.TestClient`. Keep new runtime modules under `app/` and mirror them with sibling test files under `tests/`. Share pytest-wide configuration in `tests/conftest.py` or `pytest.ini`.

## Build, Test, and Development Commands
- `python -m uvicorn app.main:app --reload` runs the API locally with autoreload for development.
- `pytest` executes the test suite; use `pytest tests/test_rate_limiter.py::test_rejects_requests_beyond_limit` for a focused run.
- `pip install fastapi "uvicorn[standard]" pytest` sets up the minimal dependencies inside an active virtual environment.

## Coding Style & Naming Conventions
Use 4-space indentation and type hints throughout; follow the patterns already present in `app/main.py`. Keep pure functions and classes small, preferring descriptive snake_case identifiers for functions and variables, and PascalCase for classes. Preserve docstrings on public callables and keep responses JSON-serialisable with explicit keys. Prefer `async` endpoints and FastAPI dependencies for cross-cutting concerns such as rate limiting. When raising quota errors, surface them through `RateLimitExceeded` so the exception handler can emit consistent payloads and headers (including `Retry-After`).

## Testing Guidelines
Name tests with the `test_` prefix and place shared fixtures near their usage within `tests/`. When extending the rate limiter, cover both happy-path and quota-exceeded scenarios. Target high-level behaviour via `TestClient` and, if adding new helpers, unit-test edge cases without hitting the network. Ensure tests pass locally (`pytest`) before opening a pull request. Keep warning filters in `pytest.ini`/`tests/conftest.py` narrowly scoped to known third-party issues.

## Commit & Pull Request Guidelines
Commit messages follow an imperative, title-case style (`Add FastAPI rate limited endpoint`). Keep the subject under ~50 characters and add body context when behaviour changes. For pull requests, include a concise summary of changes, note configuration updates (e.g., new limits or headers), and list the tests executed. Link related issues and attach screenshots or curl transcripts if the response payload changes.

## Rate Limit Configuration Tips
Adjust the rate limit by editing `limiter = RateLimiter(limit=..., window_seconds=...)` in `app/main.py`. Update the exception handler or response docs if the contract (error payload keys or headers) changes. Document any new defaults in the pull request and add regression tests so each project ID remains isolated within its own quota bucket.
