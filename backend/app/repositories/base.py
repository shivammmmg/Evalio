from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.models import CourseCreate


@dataclass(frozen=True)
class StoredCourse:
    course_id: UUID
    course: CourseCreate


class CourseRepository(Protocol):
    def create(self, course: CourseCreate) -> StoredCourse:
        ...

    def list_all(self) -> list[StoredCourse]:
        ...

    def get_by_id(self, course_id: UUID) -> StoredCourse | None:
        ...

    def update(self, course_id: UUID, course: CourseCreate) -> StoredCourse:
        ...

    def delete(self, course_id: UUID) -> None:
        ...

    def clear(self) -> None:
        ...

    def get_index(self, course_id: UUID) -> int | None:
        ...
