import base64

import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("API_USERNAME", "teacher")
    monkeypatch.setenv("API_PASSWORD", "test-password")
    with TestClient(app) as test_client:
        yield test_client


def auth_headers(username: str = "teacher", password: str = "test-password") -> dict:
    encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


def create_sample_assessment(client: TestClient) -> int:
    headers = auth_headers()
    subject_response = client.post(
        "/subjects", json={"name": "Mathematics"}, headers=headers
    )
    assert subject_response.status_code == 201
    assessment_response = client.post(
        "/assessments",
        json={
            "subject_id": subject_response.json()["id"],
            "name": "Quiz 1",
            "max_score": 20,
        },
        headers=headers,
    )
    assert assessment_response.status_code == 201
    return assessment_response.json()["id"]


def test_authentication_is_required(client: TestClient) -> None:
    response = client.get("/subjects")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"


def test_add_update_and_read_student_results(client: TestClient) -> None:
    headers = auth_headers()
    assessment_id = create_sample_assessment(client)

    added = client.post(
        "/scores",
        json={
            "assessment_id": assessment_id,
            "student_id": "STU-001",
            "score": 15,
        },
        headers=headers,
    )
    assert added.status_code == 201
    score_id = added.json()["id"]

    results = client.get("/students/STU-001/results", headers=headers)
    assert results.status_code == 200
    assert results.json()[0]["percentage"] == 75.0

    updated = client.put(
        f"/scores/{score_id}", json={"score": 18}, headers=headers
    )
    assert updated.status_code == 200
    assert updated.json()["percentage"] == 90.0

    average = client.get("/students/STU-001/average", headers=headers)
    assert average.status_code == 200
    assert average.json() == {
        "student_id": "STU-001",
        "average_percentage": 90.0,
        "assessment_count": 1,
    }


def test_rejects_invalid_or_duplicate_scores(client: TestClient) -> None:
    headers = auth_headers()
    assessment_id = create_sample_assessment(client)
    too_high = client.post(
        "/scores",
        json={
            "assessment_id": assessment_id,
            "student_id": "STU-001",
            "score": 21,
        },
        headers=headers,
    )
    assert too_high.status_code == 422
    assert "maximum" in too_high.json()["detail"]

    payload = {
        "assessment_id": assessment_id,
        "student_id": "STU-001",
        "score": 15,
    }
    created = client.post("/scores", json=payload, headers=headers)
    assert created.status_code == 201
    assert isinstance(created.json()["id"], int)
    duplicate = client.post("/scores", json=payload, headers=headers)
    assert duplicate.status_code == 409


def test_average_without_results_is_not_found(client: TestClient) -> None:
    response = client.get(
        "/students/unknown/average", headers=auth_headers()
    )
    assert response.status_code == 404
