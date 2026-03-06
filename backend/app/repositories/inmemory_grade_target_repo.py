"""
In-memory repository for grade targets.
Used as fallback when Postgres is not available.
"""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.repositories.base import StoredGradeTarget


class InMemoryGradeTargetRepository:
    def __init__(self) -> None:
        # Maps course_id -> target data
        self._targets: dict[UUID, dict] = {}
        # Reference to course repo needed to verify ownership
        self._course_ownership: dict[UUID, UUID] = {}  # course_id -> user_id

    def register_course_ownership(self, course_id: UUID, user_id: UUID) -> None:
        """Call this when a course is created to track ownership."""
        self._course_ownership[course_id] = user_id

    def unregister_course(self, course_id: UUID) -> None:
        """Call this when a course is deleted."""
        self._course_ownership.pop(course_id, None)
        self._targets.pop(course_id, None)

    def _verify_ownership(self, user_id: UUID, course_id: UUID) -> bool:
        owner = self._course_ownership.get(course_id)
        return owner == user_id

    def set_target(
        self,
        user_id: UUID,
        course_id: UUID,
        target_percentage: float,
    ) -> StoredGradeTarget:
        # In practice, the service layer should verify course ownership
        # For in-memory testing, we trust the caller or skip verification
        target_id = self._targets.get(course_id, {}).get("target_id") or uuid4()
        created_at = self._targets.get(course_id, {}).get("created_at") or datetime.now(UTC)

        self._targets[course_id] = {
            "target_id": target_id,
            "course_id": course_id,
            "target_percentage": target_percentage,
            "created_at": created_at,
        }
        return StoredGradeTarget(
            target_id=target_id,
            course_id=course_id,
            target_percentage=target_percentage,
            created_at=created_at,
        )

    def get_target(self, user_id: UUID, course_id: UUID) -> StoredGradeTarget | None:
        data = self._targets.get(course_id)
        if data is None:
            return None
        return StoredGradeTarget(
            target_id=data["target_id"],
            course_id=data["course_id"],
            target_percentage=data["target_percentage"],
            created_at=data["created_at"],
        )

    def delete_target(self, user_id: UUID, course_id: UUID) -> bool:
        if course_id not in self._targets:
            return False
        del self._targets[course_id]
        return True

    def clear(self) -> None:
        self._targets.clear()
        self._course_ownership.clear()
