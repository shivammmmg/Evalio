from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def _create_course():
    payload = {
        "name": "EECS2311",
        "term": "W26",
        "assessments": [
            {"name": "A1", "weight": 20, "raw_score": None, "total_score": None},
            {"name": "Midterm", "weight": 30, "raw_score": None, "total_score": None},
            {"name": "Final", "weight": 50, "raw_score": None, "total_score": None},
        ],
    }
    r = client.post("/courses/", json=payload)
    assert r.status_code == 200
    return r.json()["course_id"]

def test_current_standing_partial_grade():
    course_id = _create_course()
    r = client.put(
        f"/courses/{course_id}/grades",
        json={"assessments": [{"name": "A1", "raw_score": 80, "total_score": 100}]},
    )
    assert r.status_code == 200
    assert r.json()["current_standing"] == 16.0

def test_current_standing_boundary_0():
    course_id = _create_course()
    r = client.put(
        f"/courses/{course_id}/grades",
        json={"assessments": [{"name": "A1", "raw_score": 0, "total_score": 100}]},
    )
    assert r.status_code == 200
    assert r.json()["current_standing"] == 0.0

def test_current_standing_boundary_100():
    course_id = _create_course()
    r = client.put(
        f"/courses/{course_id}/grades",
        json={"assessments": [{"name": "A1", "raw_score": 100, "total_score": 100}]},
    )
    assert r.status_code == 200
    assert r.json()["current_standing"] == 20.0
