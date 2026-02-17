from __future__ import annotations

from dataclasses import dataclass


class AuthorizationError(PermissionError):
    """Error de autorización para ejecución de tools MCP."""


@dataclass(frozen=True, slots=True)
class SecurityPolicy:
    role: str
    allowed_tools: tuple[str, ...]


class SecurityService:
    """Capa mínima RBAC para el servidor MCP."""

    def __init__(self) -> None:
        self._policies = {
            "owner": SecurityPolicy(role="owner", allowed_tools=("*",)),
            "editor": SecurityPolicy(
                role="editor",
                allowed_tools=(
                    "notebook.create",
                    "notebook.merge",
                    "notebook.cleanup",
                    "notebook.search",
                    "notebook.apply_template",
                    "notebook.history",
                    "analysis.find_contradictions",
                    "analysis.suggest_questions",
                    "analysis.tone",
                    "research.web_search_with_citations",
                    "research.translate_source",
                    "material.generate_audiovisual_pack",
                    "material.preview",
                    "material.generate_mindmap",
                    "material.export_summary",
                    "study.generate_quiz",
                    "study.interactive_mindmap",
                ),
            ),
            "viewer": SecurityPolicy(
                role="viewer",
                allowed_tools=(
                    "notebook.search",
                    "notebook.history",
                    "analysis.find_contradictions",
                    "analysis.suggest_questions",
                    "analysis.tone",
                    "research.web_search_with_citations",
                    "material.preview",
                    "material.generate_mindmap",
                    "material.export_summary",
                    "study.interactive_mindmap",
                ),
            ),
        }

    def authorize(self, tool_name: str, actor_role: str = "owner") -> None:
        policy = self._policies.get(actor_role)
        if policy is None:
            raise AuthorizationError(f"Rol desconocido: {actor_role}")

        if "*" in policy.allowed_tools or tool_name in policy.allowed_tools:
            return

        raise AuthorizationError(f"Rol '{actor_role}' no autorizado para tool '{tool_name}'")

    def available_roles(self) -> list[str]:
        return sorted(self._policies.keys())
