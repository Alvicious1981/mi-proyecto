from __future__ import annotations

from dataclasses import dataclass


class AuthorizationError(PermissionError):
    """Error de autorización para ejecución de tools MCP."""


@dataclass(frozen=True, slots=True)
class SecurityPolicy:
    role: str
    allowed_tools: tuple[str, ...]


class SecurityService:
    """Seguridad simplificada para entorno privado Antigravity.

    La aplicación asume single-user (owner) y no implementa autenticación.
    """

    def __init__(self) -> None:
        self.private_mode = True
        self._policies = {
            "owner": SecurityPolicy(role="owner", allowed_tools=("*",)),
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
