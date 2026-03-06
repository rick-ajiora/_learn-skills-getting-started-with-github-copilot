from fastapi.testclient import TestClient
import pytest

from src import app
from src.app import reset_activities


@pytest.fixture(autouse=True)
def client():
    """Provide a TestClient and reset state before each test."""
    reset_activities()
    with TestClient(app.app) as c:
        yield c


def test_get_activities_returns_initial_data(client):
    # Arrange is handled by fixture
    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_successful_signup_adds_participant(client):
    # Arrange
    email = "new@school.edu"

    # Act
    resp = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in client.get("/activities").json()["Chess Club"]["participants"]


def test_duplicate_signup_returns_400(client):
    # Arrange
    existing = "michael@mergington.edu"

    # Act
    resp = client.post(
        "/activities/Chess%20Club/signup", params={"email": existing}
    )

    # Assert
    assert resp.status_code == 400


def test_signup_to_nonexistent_activity(client):
    # Arrange
    email = "foo@bar.com"

    # Act
    resp = client.post("/activities/DoesNotExist/signup", params={"email": email})

    # Assert
    assert resp.status_code == 404


def test_delete_existing_participant(client):
    # Arrange
    to_remove = "michael@mergington.edu"

    # Act
    resp = client.delete(
        "/activities/Chess%20Club/signup", params={"email": to_remove}
    )

    # Assert
    assert resp.status_code == 200
    assert to_remove not in client.get("/activities").json()["Chess Club"]["participants"]


def test_delete_nonexistent_participant(client):
    # Act
    resp = client.delete(
        "/activities/Chess%20Club/signup", params={"email": "noone@nowhere.com"}
    )

    # Assert
    assert resp.status_code == 404


def test_delete_from_nonexistent_activity(client):
    # Act
    resp = client.delete(
        "/activities/Nope/signup", params={"email": "someone@nowhere.com"}
    )

    # Assert
    assert resp.status_code == 404
