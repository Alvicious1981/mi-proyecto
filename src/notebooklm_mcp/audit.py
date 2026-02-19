from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _redact_value(key: str, value: Any) -> Any:
    lowered = key.lower()
    if "token" in lowered or "api_key" in lowered or "secret" in lowered:
        return "***REDACTED***"
    if isinstance(value, dict):
        return {k: _redact_value(k, v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_value(key, v) for v in value]
    return value


@dataclass(slots=True)
class AuditEvent:
    timestamp: str
    actor_role: str
    action: str
    status: str
    metadata: dict[str, Any] = field(default_factory=dict)


class AuditService:
    """Bitácora en memoria con redacción básica de datos sensibles."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def log_event(
        self,
        actor_role: str,
        action: str,
        status: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        safe_metadata = _redact_value("metadata", metadata or {})
        event = AuditEvent(
            timestamp=_now_iso(),
            actor_role=actor_role,
            action=action,
            status=status,
            metadata=safe_metadata,
        )
        self._events.append(event)
        return self._serialize(event)

    def list_events(self, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, limit)
        return [self._serialize(event) for event in self._events[-limit:]]

    def _serialize(self, event: AuditEvent) -> dict[str, Any]:
        return {
            "timestamp": event.timestamp,
            "actor_role": event.actor_role,
            "action": event.action,
            "status": event.status,
            "metadata": event.metadata,
        }
