from __future__ import annotations

from dataclasses import dataclass
import os


class AuthorizationError(PermissionError):
    """Error de autorización para ejecución de tools MCP."""


class AuthenticationError(PermissionError):
    """Error de autenticación para contexto privado."""


@dataclass(frozen=True, slots=True)
class SecurityPolicy:
    role: str
    allowed_tools: tuple[str, ...]


class SecurityService:
    """Capa mínima RBAC para el servidor MCP.

    - Por defecto opera en modo privado (single-user), permitiendo solo rol owner.
    - Soporta API key opcional para reforzar acceso del owner.
    """

    def __init__(
        self,
        private_mode: bool | None = None,
        owner_api_key: str | None = None,
    ) -> None:
        self.private_mode = self._resolve_private_mode(private_mode)
        self.owner_api_key = self._resolve_owner_api_key(owner_api_key)

        if self.private_mode:
            self._policies = {
                "owner": SecurityPolicy(role="owner", allowed_tools=("*",)),
            }
            return

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
                    "system.compatibility_report",
                    "system.descriptor",
                    "audit.stats",
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
                    "system.compatibility_report",
                    "system.descriptor",
                    "audit.stats",
                ),
            ),
        }

    def authenticate(self, actor_role: str = "owner", actor_token: str | None = None) -> None:
        # En privado, si existe API key configurada, exigirla para owner.
        if self.private_mode and self.owner_api_key:
            if actor_role != "owner":
                raise AuthenticationError("Modo privado: solo owner autenticado puede ejecutar tools")
            if actor_token != self.owner_api_key:
                raise AuthenticationError("API key inválida para owner")

    def authorize(self, tool_name: str, actor_role: str = "owner") -> None:
        policy = self._policies.get(actor_role)
        if policy is None:
            raise AuthorizationError(f"Rol desconocido: {actor_role}")

        if "*" in policy.allowed_tools or tool_name in policy.allowed_tools:
            return

        raise AuthorizationError(f"Rol '{actor_role}' no autorizado para tool '{tool_name}'")

    def available_roles(self) -> list[str]:
        return sorted(self._policies.keys())

    def _resolve_private_mode(self, private_mode: bool | None) -> bool:
        if private_mode is not None:
            return private_mode
        env_value = os.getenv("NOTEBOOKLM_MCP_PRIVATE_MODE", "true").strip().lower()
        return env_value not in {"0", "false", "no", "off"}

    def _resolve_owner_api_key(self, owner_api_key: str | None) -> str | None:
        if owner_api_key is not None:
            return owner_api_key.strip() or None
        env_value = os.getenv("NOTEBOOKLM_MCP_OWNER_API_KEY", "").strip()
        return env_value or None
