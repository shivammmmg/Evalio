import pytest

from app.dependencies import get_course_repo

@pytest.fixture(autouse=True)
def clear_courses_db():
    get_course_repo().clear()
    yield
    get_course_repo().clear()
