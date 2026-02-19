from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .repository import NotebookRepository


@dataclass(frozen=True, slots=True)
class ResourceItem:
    uri: str
    name: str
    description: str
    mime_type: str = "application/json"


class ResourceService:
    """Recursos MCP básicos (estáticos + dinámicos por notebook)."""

    def __init__(self, repo: NotebookRepository) -> None:
        self.repo = repo

    def list_resources(self) -> list[dict[str, str]]:
        static_resources = [
            ResourceItem(
                uri="mcp://server/info",
                name="ServerInfo",
                description="Información del servidor MCP y versión de protocolo.",
            ),
            ResourceItem(
                uri="mcp://templates/notebook",
                name="NotebookTemplates",
                description="Plantillas predefinidas disponibles para cuadernos.",
            ),
            ResourceItem(
                uri="mcp://audit/recent",
                name="AuditRecent",
                description="Últimos eventos de auditoría (redactados).",
            ),
        ]

        notebook_resources = [
            ResourceItem(
                uri=f"mcp://notebooks/{notebook.id}/summary",
                name=f"NotebookSummary:{notebook.title}",
                description="Resumen estructurado del cuaderno.",
            )
            for notebook in self.repo.list()
        ]

        return [self._serialize_resource(item) for item in [*static_resources, *notebook_resources]]

    def read_resource(
        self,
        uri: str,
        server_info: dict[str, Any],
        templates: dict[str, list[str]],
        audit_recent: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if uri == "mcp://server/info":
            return {
                "uri": uri,
                "mimeType": "application/json",
                "contents": server_info,
            }

        if uri == "mcp://templates/notebook":
            return {
                "uri": uri,
                "mimeType": "application/json",
                "contents": templates,
            }

        if uri == "mcp://audit/recent":
            return {
                "uri": uri,
                "mimeType": "application/json",
                "contents": {
                    "events": audit_recent or [],
                    "total": len(audit_recent or []),
                },
            }

        notebook_prefix = "mcp://notebooks/"
        notebook_suffix = "/summary"
        if uri.startswith(notebook_prefix) and uri.endswith(notebook_suffix):
            notebook_id = uri[len(notebook_prefix) : -len(notebook_suffix)]
            notebook = self.repo.get(notebook_id)
            return {
                "uri": uri,
                "mimeType": "application/json",
                "contents": {
                    "id": notebook.id,
                    "title": notebook.title,
                    "description": notebook.description,
                    "language": notebook.language,
                    "tags": notebook.tags,
                    "sections": notebook.sections,
                    "updated_at": notebook.updated_at.isoformat(),
                },
            }

        raise KeyError(f"Resource no encontrada: {uri}")

    def _serialize_resource(self, item: ResourceItem) -> dict[str, str]:
        return {
            "uri": item.uri,
            "name": item.name,
            "description": item.description,
            "mimeType": item.mime_type,
        }
