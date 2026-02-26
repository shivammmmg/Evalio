from fastapi.testclient import TestClient
from uuid import UUID

from app.main import app

client = TestClient(app)

def test_create_course_success():
    payload = {
        "name": "EECS2311",
        "term": "W26",
        "assessments": [
            {"name": "A1", "weight": 20, "grade": None},
            {"name": "Midterm", "weight": 30, "grade": None},
            {"name": "Final", "weight": 50, "grade": None},
        ],
    }
    r = client.post("/courses/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "Course created successfully"
    assert data["total_weight"] == 100
    assert "course_id" in data
    UUID(data["course_id"])

def test_create_course_rejects_empty_assessments():
    payload = {"name": "X", "term": "W26", "assessments": []}
    r = client.post("/courses/", json=payload)
    assert r.status_code == 400
    assert "At least one assessment" in r.json()["detail"]

def test_create_course_rejects_total_weight_over_100():
    payload = {
        "name": "X",
        "term": "W26",
        "assessments": [
            {"name": "A1", "weight": 60, "grade": None},
            {"name": "A2", "weight": 60, "grade": None},
        ],
    }
    r = client.post("/courses/", json=payload)
    assert r.status_code == 400
    assert "cannot exceed 100" in r.json()["detail"]

def test_list_courses_includes_course_id():
    payload = {
        "name": "EECS2311",
        "term": "W26",
        "assessments": [
            {"name": "A1", "weight": 20, "raw_score": None, "total_score": None},
        ],
    }
    created = client.post("/courses/", json=payload)
    assert created.status_code == 200

    listed = client.get("/courses/")
    assert listed.status_code == 200
    courses = listed.json()
    assert len(courses) == 1
    assert "course_id" in courses[0]
    UUID(courses[0]["course_id"])
