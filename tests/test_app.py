import importlib
import pytest

from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def reset_app_module():
    # reload the module to clear in-memory state between tests
    import src.app as app_module
    importlib.reload(app_module)
    yield


def test_get_activities_returns_seed_data():
    from src.app import app
    client = TestClient(app)

    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # basic sanity checks on the seeded activities
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant_and_prevents_duplicates():
    from src.app import app
    client = TestClient(app)

    activity = "Chess Club"
    email = "teststudent@mergington.edu"

    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # second attempt should fail
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400
    assert "already signed up" in resp2.json()["detail"]


def test_signup_unknown_activity_gives_404():
    from src.app import app
    client = TestClient(app)

    resp = client.post("/activities/Nope/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_unregister_removes_participant_and_handles_errors():
    from src.app import app
    client = TestClient(app)

    activity = "Chess Club"
    email = "someone@mergington.edu"

    # first sign up so we can remove
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # now remove
    resp = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Removed" in resp.json()["message"]

    # removing again should give 404
    resp2 = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 404


def test_unregister_unknown_activity_gives_404():
    from src.app import app
    client = TestClient(app)

    resp = client.delete("/activities/Nope/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404
