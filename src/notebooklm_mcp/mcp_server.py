from __future__ import annotations

"""Servidor MCP inicial para gestión y análisis de cuadernos."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .analysis import AnalysisService
from .prompts import PromptService
from .research import ResearchService
from .resources import ResourceService
from .services import DEFAULT_TEMPLATES, NotebookService
from .material import MaterialService
from .study import StudyService
from .validation import SchemaValidationError, validate_input


SERVER_NAME = "notebooklm-mcp-server"
SERVER_VERSION = "0.1.0"
PROTOCOL_VERSION = "2025-01-01"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., Any]


class NotebookLMMCPServer:
    def __init__(self, service: NotebookService | None = None) -> None:
        self.service = service or NotebookService()
        self.analysis = AnalysisService(self.service.repo)
        self.research = ResearchService()
        self.material = MaterialService(self.service.repo)
        self.study = StudyService(self.service.repo)
        self.resources = ResourceService(self.service.repo)
        self.prompts = PromptService(self.service.repo)
        self._tools = self._register_tools()

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema,
            }
            for tool in self._tools.values()
        ]

    def server_info(self) -> dict[str, Any]:
        """Información de handshake/descubrimiento para clientes MCP."""
        return {
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "protocol_version": PROTOCOL_VERSION,
            "generated_at": _utc_now(),
        }

    def capabilities(self) -> dict[str, Any]:
        return {
            "tools": {
                "count": len(self._tools),
                "names": sorted(self._tools.keys()),
            },
            "resources": {"supported": True},
            "prompts": {"supported": True},
        }

    def descriptor(self) -> dict[str, Any]:
        """Descriptor amigable para Agent Manager (descubrimiento básico)."""
        return {
            "server": self.server_info(),
            "capabilities": self.capabilities(),
            "tools": self.list_tools(),
            "resources": self.list_resources(),
            "prompts": self.list_prompts(),
        }

    def list_resources(self) -> list[dict[str, str]]:
        return self.resources.list_resources()

    def read_resource(self, uri: str) -> dict[str, Any]:
        return self.resources.read_resource(
            uri=uri,
            server_info=self.server_info(),
            templates=DEFAULT_TEMPLATES,
        )

    def list_prompts(self) -> list[dict[str, Any]]:
        return self.prompts.list_prompts()

    def get_prompt(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return self.prompts.get_prompt(name=name, arguments=arguments)

    def compatibility_report(self) -> dict[str, Any]:
        """Reporte rápido de compatibilidad para Agent Manager."""
        descriptor = self.descriptor()
        checks = {
            "has_server_name": bool(descriptor.get("server", {}).get("name")),
            "has_server_version": bool(descriptor.get("server", {}).get("version")),
            "has_protocol_version": bool(descriptor.get("server", {}).get("protocol_version")),
            "has_tools": len(descriptor.get("tools", [])) > 0,
            "resources_supported": bool(descriptor.get("capabilities", {}).get("resources", {}).get("supported")),
            "prompts_supported": bool(descriptor.get("capabilities", {}).get("prompts", {}).get("supported")),
        }
        return {
            "compatible": all(checks.values()),
            "checks": checks,
            "summary": f"{sum(checks.values())}/{len(checks)} checks OK",
        }

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        if tool_name not in self._tools:
            raise KeyError(f"Tool no encontrada: {tool_name}")

        tool = self._tools[tool_name]
        validate_input(arguments, tool.input_schema, tool_name)

        try:
            return tool.handler(**arguments)
        except TypeError as exc:
            raise SchemaValidationError(f"{tool_name}: argumentos inválidos ({exc})") from exc

    def _register_tools(self) -> dict[str, ToolDefinition]:
        return {
            "notebook.create": ToolDefinition(
                name="notebook.create",
                description="Crea un cuaderno nuevo con metadata opcional y plantilla.",
                input_schema={
                    "type": "object",
                    "required": ["title"],
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "language": {"type": "string"},
                        "template_id": {"type": "string"},
                        "actor": {"type": "string"},
                    },
                },
                handler=self.service.create_notebook,
            ),
            "notebook.merge": ToolDefinition(
                name="notebook.merge",
                description="Fusiona múltiples cuadernos en uno nuevo.",
                input_schema={
                    "type": "object",
                    "required": ["source_ids", "destination_title"],
                    "properties": {
                        "source_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 2,
                        },
                        "destination_title": {"type": "string"},
                        "strategy": {"type": "string"},
                        "actor": {"type": "string"},
                    },
                },
                handler=self.service.merge_notebooks,
            ),
            "notebook.cleanup": ToolDefinition(
                name="notebook.cleanup",
                description="Elimina secciones vacías/duplicadas de un cuaderno.",
                input_schema={
                    "type": "object",
                    "required": ["notebook_id"],
                    "properties": {
                        "notebook_id": {"type": "string"},
                        "actor": {"type": "string"},
                    },
                },
                handler=self.service.cleanup_notebook,
            ),
            "notebook.search": ToolDefinition(
                name="notebook.search",
                description="Búsqueda rápida por texto y tag.",
                input_schema={
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": {"type": "string"},
                        "tag": {"type": "string"},
                    },
                },
                handler=self.service.search_notebooks,
            ),
            "notebook.apply_template": ToolDefinition(
                name="notebook.apply_template",
                description="Aplica una plantilla predefinida al cuaderno.",
                input_schema={
                    "type": "object",
                    "required": ["notebook_id", "template_id"],
                    "properties": {
                        "notebook_id": {"type": "string"},
                        "template_id": {"type": "string"},
                        "actor": {"type": "string"},
                    },
                },
                handler=self.service.apply_template,
            ),
            "notebook.history": ToolDefinition(
                name="notebook.history",
                description="Consulta el historial de cambios del cuaderno.",
                input_schema={
                    "type": "object",
                    "required": ["notebook_id"],
                    "properties": {
                        "notebook_id": {"type": "string"},
                    },
                },
                handler=self.service.notebook_history,
            ),
            "analysis.find_contradictions": ToolDefinition(
                name="analysis.find_contradictions",
                description="Detecta contradicciones e información faltante en un cuaderno.",
                input_schema={
                    "type": "object",
                    "required": ["notebook_id"],
                    "properties": {"notebook_id": {"type": "string"}},
                },
                handler=self.analysis.find_contradictions,
            ),
            "analysis.suggest_questions": ToolDefinition(
                name="analysis.suggest_questions",
                description="Sugiere preguntas clave según las secciones del cuaderno.",
                input_schema={
                    "type": "object",
                    "required": ["notebook_id"],
                    "properties": {
                        "notebook_id": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                    },
                },
                handler=self.analysis.suggest_questions,
            ),
            "analysis.tone": ToolDefinition(
                name="analysis.tone",
                description="Analiza el tono dominante en el contenido del cuaderno.",
                input_schema={
                    "type": "object",
                    "required": ["notebook_id"],
                    "properties": {"notebook_id": {"type": "string"}},
                },
                handler=self.analysis.analyze_tone,
            ),
            "research.web_search_with_citations": ToolDefinition(
                name="research.web_search_with_citations",
                description="Busca información adicional y devuelve citas estructuradas.",
                input_schema={
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                        "language": {"type": "string"},
                    },
                },
                handler=self.research.web_search_with_citations,
            ),
            "research.translate_source": ToolDefinition(
                name="research.translate_source",
                description="Traduce contenido de fuente manteniendo trazabilidad básica.",
                input_schema={
                    "type": "object",
                    "required": ["text", "target_language"],
                    "properties": {
                        "text": {"type": "string"},
                        "target_language": {"type": "string"},
                        "source_language": {"type": "string"},
                    },
                },
                handler=self.research.translate_source,
            ),
            "material.generate_audiovisual_pack": ToolDefinition(
                name="material.generate_audiovisual_pack",
                description="Genera un paquete audiovisual inicial (escenas y prompts).",
                input_schema={
                    "type": "object",
                    "required": ["notebook_id"],
                    "properties": {
                        "notebook_id": {"type": "string"},
                        "style": {"type": "string"},
                    },
                },
                handler=self.material.generate_audiovisual_pack,
            ),
            "material.preview": ToolDefinition(
                name="material.preview",
                description="Genera vista previa dinámica en bloques de contenido.",
                input_schema={
                    "type": "object",
                    "required": ["notebook_id"],
                    "properties": {
                        "notebook_id": {"type": "string"},
                        "mode": {"type": "string"},
                    },
                },
                handler=self.material.preview,
            ),
            "material.generate_mindmap": ToolDefinition(
                name="material.generate_mindmap",
                description="Genera un mapa mental base con nodos y relaciones.",
                input_schema={
                    "type": "object",
                    "required": ["notebook_id"],
                    "properties": {"notebook_id": {"type": "string"}},
                },
                handler=self.material.generate_mindmap,
            ),
            "material.export_summary": ToolDefinition(
                name="material.export_summary",
                description="Exporta resumen a formato md/txt/json.",
                input_schema={
                    "type": "object",
                    "required": ["notebook_id"],
                    "properties": {
                        "notebook_id": {"type": "string"},
                        "format": {"type": "string"},
                    },
                },
                handler=self.material.export_summary,
            ),
            "study.generate_quiz": ToolDefinition(
                name="study.generate_quiz",
                description="Genera tests automáticos desde el contenido del cuaderno.",
                input_schema={
                    "type": "object",
                    "required": ["notebook_id"],
                    "properties": {
                        "notebook_id": {"type": "string"},
                        "difficulty": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                    },
                },
                handler=self.study.generate_quiz,
            ),
            "study.interactive_mindmap": ToolDefinition(
                name="study.interactive_mindmap",
                description="Genera mapa mental interactivo para estudio y repaso.",
                input_schema={
                    "type": "object",
                    "required": ["notebook_id"],
                    "properties": {"notebook_id": {"type": "string"}},
                },
                handler=self.study.interactive_mindmap,
            ),
        }
