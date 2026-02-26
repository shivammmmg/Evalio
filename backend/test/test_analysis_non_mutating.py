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

def test_target_check_does_not_change_grades():
    course_id = _create_course()

    r1 = client.put(
        f"/courses/{course_id}/grades",
        json={"assessments": [{"name": "A1", "raw_score": 80, "total_score": 100}]},
    )
    assert r1.status_code == 200

    before = client.get("/courses/").json()
    current_course = next(course for course in before if course["course_id"] == course_id)
    before_state = [
        (a["name"], a["raw_score"], a["total_score"]) for a in current_course["assessments"]
    ]

    r2 = client.post(f"/courses/{course_id}/target", json={"target": 85})
    assert r2.status_code == 200

    after = client.get("/courses/").json()
    current_after = next(course for course in after if course["course_id"] == course_id)
    after_state = [
        (a["name"], a["raw_score"], a["total_score"]) for a in current_after["assessments"]
    ]

    assert before_state == after_state

def test_repeated_target_calls_consistent():
    course_id = _create_course()
    r1 = client.post(f"/courses/{course_id}/target", json={"target": 70})
    r2 = client.post(f"/courses/{course_id}/target", json={"target": 70})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json() == r2.json()
