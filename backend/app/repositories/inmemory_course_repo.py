from uuid import UUID, uuid4

from app.models import CourseCreate
from app.repositories.base import StoredCourse


class InMemoryCourseRepository:
    def __init__(self) -> None:
        self._courses: dict[UUID, CourseCreate] = {}

    def create(self, course: CourseCreate) -> StoredCourse:
        course_id = uuid4()
        self._courses[course_id] = course
        return StoredCourse(course_id=course_id, course=course)

    def list_all(self) -> list[StoredCourse]:
        return [
            StoredCourse(course_id=course_id, course=course)
            for course_id, course in self._courses.items()
        ]

    def get_by_id(self, course_id: UUID) -> StoredCourse | None:
        course = self._courses.get(course_id)
        if course is None:
            return None
        return StoredCourse(course_id=course_id, course=course)

    def update(self, course_id: UUID, course: CourseCreate) -> StoredCourse:
        if course_id not in self._courses:
            raise KeyError(course_id)
        self._courses[course_id] = course
        return StoredCourse(course_id=course_id, course=course)

    def delete(self, course_id: UUID) -> None:
        if course_id not in self._courses:
            raise KeyError(course_id)
        del self._courses[course_id]

    def clear(self) -> None:
        self._courses.clear()

    def get_index(self, course_id: UUID) -> int | None:
        for index, key in enumerate(self._courses.keys()):
            if key == course_id:
                return index
        return None
