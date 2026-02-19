from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid4())


@dataclass(slots=True)
class Notebook:
    title: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    language: str = "es"
    template_id: str | None = None
    id: str = field(default_factory=new_id)
    sections: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class ChangeLog:
    notebook_id: str
    action: str
    actor: str = "system"
    diff_summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=new_id)
    timestamp: datetime = field(default_factory=utc_now)
