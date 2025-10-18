# FastAPI Rate Limit

A minimal FastAPI service that enforces per-project request limits using an in-memory quota bucket and returns RFC-compliant 429 responses.

## Features
- Enforces rate limits per `X-Project-ID` header with a configurable rolling window.
- Emits structured JSON errors plus a `Retry-After` header when the quota is exceeded.
- Ships with pytest coverage asserting both happy-path and quota-exceeded flows.
- Filters noisy FastAPI deprecation warnings so test runs stay focused on regressions.

## Project Structure
- `app/main.py` — FastAPI app, `RateLimiter`, and example route.
- `tests/test_rate_limiter.py` — pytest suite exercising quota behaviour via `TestClient`.
- `tests/conftest.py` — pytest bootstrap to ensure imports work and to silence known warnings.
- `pytest.ini` — shared pytest configuration for warning filters.
- `AGENTS.md` — contributor guide detailing coding, testing, and PR expectations.

## Quick Start
1. Install Python 3.12 and create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the API locally:
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage
Send GET requests to `/your-endpoint` with a project identifier header:
```bash
curl -H "X-Project-ID: project-alpha" http://127.0.0.1:8000/your-endpoint
```
The default limit allows 10 requests per project within a 60-second window. Adjust `RateLimiter(limit=..., window_seconds=...)` in `app/main.py` to change the policy. Clients that exceed the quota receive HTTP 429 with both a descriptive JSON payload and a `Retry-After` hint.

## Testing
Run the full suite before committing changes:
```bash
pytest
```
Use `pytest tests/test_rate_limiter.py::test_rejects_requests_beyond_limit` for focused debugging. The repository’s `pytest.ini` suppresses the known FastAPI warning about deprecated 422 status constants so genuine issues are easier to spot.

## Contributing
Review `AGENTS.md` for repository guidelines covering style, testing expectations, and pull request checklists. Document any changes to rate-limit defaults and extend the test suite to cover them.
