from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _make_request(project_id: str):
    return client.get("/your-endpoint", headers={"X-Project-ID": project_id})


def test_allows_up_to_limit_within_window():
    for _ in range(10):
        response = _make_request("project-alpha")
        assert response.status_code == 200
        body = response.json()
        assert body["project_id"] == "project-alpha"
        assert body["message"] == "Request successful"


def test_rejects_requests_beyond_limit():
    # Exhaust the limit first.
    for _ in range(10):
        assert _make_request("project-beta").status_code == 200

    # The next request should be blocked with HTTP 429 and JSON details.
    response = _make_request("project-beta")
    assert response.status_code == 429
    body = response.json()
    assert body["error"] == "Too Many Requests"
    assert body["project_id"] == "project-beta"


def test_limits_are_scoped_by_project():
    # Even though project-gamma has exhausted its quota, a different project
    # should still be able to make requests.
    for _ in range(10):
        assert _make_request("project-gamma").status_code == 200

    assert _make_request("project-delta").status_code == 200
