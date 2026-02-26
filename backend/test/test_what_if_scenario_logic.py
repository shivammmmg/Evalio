import copy
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def _create_course():
    payload = {
        "name": "EECS2311",
        "term": "W26",
        "assessments": [
            {"name": "A1", "weight": 20, "raw_score": None, "total_score": None},
            {"name": "Final", "weight": 80, "raw_score": None, "total_score": None},
        ],
    }
    r = client.post("/courses/", json=payload)
    assert r.status_code == 200
    return r.json()["course_id"]

def _set_percent(course_id: str, assessment_name: str, percent: float):
    r = client.put(
        f"/courses/{course_id}/grades",
        json={"assessments": [{"name": assessment_name, "raw_score": percent, "total_score": 100}]},
    )
    assert r.status_code == 200

def _get_course(course_id: str):
    courses = client.get("/courses/").json()
    return next(course for course in courses if course["course_id"] == course_id)

def test_what_if_real_grades_unchanged():
    course_id = _create_course()
    _set_percent(course_id, "A1", 80)

    before = _get_course(course_id)
    before_copy = copy.deepcopy(before)

    r = client.post(
        f"/courses/{course_id}/whatif",
        json={"assessment_name": "Final", "hypothetical_score": 90},
    )
    assert r.status_code == 200
    data = r.json()

    assert data["current_standing"] == pytest.approx(16.0)
    assert data["projected_grade"] == pytest.approx(88.0)

    after = _get_course(course_id)
    assert after == before_copy

def test_what_if_boundary_values_0_and_100():
    course_id = _create_course()
    _set_percent(course_id, "A1", 80)

    r0 = client.post(f"/courses/{course_id}/whatif", json={"assessment_name": "Final", "hypothetical_score": 0})
    assert r0.status_code == 200
    assert r0.json()["projected_grade"] == pytest.approx(16.0)

    r100 = client.post(f"/courses/{course_id}/whatif", json={"assessment_name": "Final", "hypothetical_score": 100})
    assert r100.status_code == 200
    assert r100.json()["projected_grade"] == pytest.approx(96.0)

def test_repeated_what_if_calls_consistent_and_non_mutating():
    course_id = _create_course()
    _set_percent(course_id, "A1", 80)

    before = _get_course(course_id)

    r1 = client.post(f"/courses/{course_id}/whatif", json={"assessment_name": "Final", "hypothetical_score": 75})
    r2 = client.post(f"/courses/{course_id}/whatif", json={"assessment_name": "Final", "hypothetical_score": 75})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["projected_grade"] == r2.json()["projected_grade"]

    after = _get_course(course_id)
    assert after == before

def test_what_if_rejects_unknown_or_already_graded_assessment():
    course_id = _create_course()
    _set_percent(course_id, "A1", 80)

    r = client.post(f"/courses/{course_id}/whatif", json={"assessment_name": "DoesNotExist", "hypothetical_score": 50})
    assert r.status_code == 400

    r2 = client.post(f"/courses/{course_id}/whatif", json={"assessment_name": "A1", "hypothetical_score": 50})
    assert r2.status_code == 400
