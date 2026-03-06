from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.repositories.base import StoredScenario, StoredScenarioEntry


class InMemoryScenarioRepository:
    def __init__(self) -> None:
        # {user_id: {course_id: {scenario_id: StoredScenario}}}
        self._store: dict[UUID, dict[UUID, dict[UUID, StoredScenario]]] = {}

    def _user_course_bucket(self, user_id: UUID, course_id: UUID) -> dict[UUID, StoredScenario]:
        return self._store.setdefault(user_id, {}).setdefault(course_id, {})

    def create(
        self,
        user_id: UUID,
        course_id: UUID,
        name: str,
        entries: list[StoredScenarioEntry],
    ) -> StoredScenario:
        scenario_id = uuid4()
        stored = StoredScenario(
            scenario_id=scenario_id,
            name=name,
            entries=list(entries),
            created_at=datetime.now(UTC).isoformat(),
        )
        self._user_course_bucket(user_id, course_id)[scenario_id] = stored
        return stored

    def list_all(self, user_id: UUID, course_id: UUID) -> list[StoredScenario]:
        bucket = self._user_course_bucket(user_id, course_id)
        return list(bucket.values())

    def get_by_id(self, user_id: UUID, course_id: UUID, scenario_id: UUID) -> StoredScenario | None:
        bucket = self._user_course_bucket(user_id, course_id)
        return bucket.get(scenario_id)

    def delete(self, user_id: UUID, course_id: UUID, scenario_id: UUID) -> bool:
        bucket = self._user_course_bucket(user_id, course_id)
        if scenario_id not in bucket:
            return False
        del bucket[scenario_id]
        return True

    def clear(self) -> None:
        self._store.clear()
