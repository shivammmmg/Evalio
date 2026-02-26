from app.repositories.base import CourseRepository
from app.repositories.inmemory_course_repo import InMemoryCourseRepository
from app.services.course_service import CourseService

_course_repo = InMemoryCourseRepository()
_course_service = CourseService(_course_repo)


def get_course_repo() -> CourseRepository:
    return _course_repo


def get_course_service() -> CourseService:
    return _course_service
