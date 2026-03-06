"""
PostgreSQL repository for grade targets.
Manages user-defined target grades per course.
"""
from __future__ import annotations

from datetime import UTC
from uuid import UUID

from sqlalchemy import select, delete

from app.db import CourseDB, GradeTargetDB, SessionLocal, init_db
from app.repositories.base import StoredGradeTarget


class PostgresGradeTargetRepository:
    def __init__(self, session_factory=SessionLocal) -> None:
        self._session_factory = session_factory
        init_db()

    def _to_stored(self, row: GradeTargetDB) -> StoredGradeTarget:
        created_at = row.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        return StoredGradeTarget(
            target_id=row.id,
            course_id=row.course_id,
            target_percentage=float(row.target_percentage) if row.target_percentage is not None else None,
            created_at=created_at,
        )

    def _get_course(self, session, user_id: UUID, course_id: UUID) -> CourseDB | None:
        return session.scalar(
            select(CourseDB).where(
                CourseDB.id == course_id,
                CourseDB.user_id == user_id,
            )
        )

    def set_target(
        self,
        user_id: UUID,
        course_id: UUID,
        target_percentage: float,
    ) -> StoredGradeTarget:
        with self._session_factory() as session:
            # Verify course belongs to user
            course = self._get_course(session, user_id, course_id)
            if course is None:
                raise KeyError(f"Course {course_id} not found for user {user_id}")

            # Check if target already exists
            existing = session.scalar(
                select(GradeTargetDB)
                .where(GradeTargetDB.course_id == course_id)
                .with_for_update()
            )

            if existing is not None:
                # Update existing target
                existing.target_percentage = target_percentage
                session.commit()
                session.refresh(existing)
                return self._to_stored(existing)

            # Create new target
            row = GradeTargetDB(
                course_id=course_id,
                target_percentage=target_percentage,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._to_stored(row)

    def get_target(self, user_id: UUID, course_id: UUID) -> StoredGradeTarget | None:
        with self._session_factory() as session:
            # Verify course belongs to user
            course = self._get_course(session, user_id, course_id)
            if course is None:
                return None

            row = session.scalar(
                select(GradeTargetDB).where(GradeTargetDB.course_id == course_id)
            )
            if row is None:
                return None
            return self._to_stored(row)

    def delete_target(self, user_id: UUID, course_id: UUID) -> bool:
        with self._session_factory() as session:
            # Verify course belongs to user
            course = self._get_course(session, user_id, course_id)
            if course is None:
                return False

            row = session.scalar(
                select(GradeTargetDB).where(GradeTargetDB.course_id == course_id)
            )
            if row is None:
                return False
            session.delete(row)
            session.commit()
            return True

    def clear(self) -> None:
        with self._session_factory() as session:
            session.execute(delete(GradeTargetDB))
            session.commit()
