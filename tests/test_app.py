import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()

    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    email = "test.student@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 200
    assert f"Signed up {email} for Chess Club" in response.json()["message"]
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_email_returns_400():
    email = "duplicate.student@mergington.edu"
    first_response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    duplicate_response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert first_response.status_code == 200
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_from_activity():
    email = "daniel@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")

    assert response.status_code == 200
    assert f"Removed {email} from Chess Club" in response.json()["message"]
    assert email not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404():
    email = "missing.student@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_participant_from_nonexistent_activity_returns_404():
    response = client.delete("/activities/Unknown%20Club/participants?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
