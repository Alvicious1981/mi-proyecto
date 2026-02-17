from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .repository import NotebookRepository


@dataclass(frozen=True, slots=True)
class PromptDefinition:
    name: str
    description: str
    argument_schema: dict[str, Any]


class PromptValidationError(ValueError):
    """Error de validación para argumentos de prompts MCP."""


class PromptService:
    """Prompts MCP básicos para guiar flujos de investigación y estudio."""

    def __init__(self, repo: NotebookRepository) -> None:
        self.repo = repo
        self._definitions = {
            "research_brief": PromptDefinition(
                name="research_brief",
                description="Genera un brief de investigación con objetivos, hipótesis y riesgos.",
                argument_schema={
                    "type": "object",
                    "required": ["notebook_id"],
                    "properties": {
                        "notebook_id": {"type": "string"},
                    },
                },
            ),
            "study_plan": PromptDefinition(
                name="study_plan",
                description="Crea un plan de estudio accionable a partir del cuaderno.",
                argument_schema={
                    "type": "object",
                    "required": ["notebook_id"],
                    "properties": {
                        "notebook_id": {"type": "string"},
                        "days": {"type": "integer", "minimum": 1, "maximum": 60},
                    },
                },
            ),
        }

    def list_prompts(self) -> list[dict[str, Any]]:
        return [
            {
                "name": definition.name,
                "description": definition.description,
                "argumentSchema": definition.argument_schema,
            }
            for definition in self._definitions.values()
        ]

    def get_prompt(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        definition = self._definitions.get(name)
        if definition is None:
            raise KeyError(f"Prompt no encontrado: {name}")

        self._validate_arguments(name, arguments, definition.argument_schema)

        if name == "research_brief":
            notebook_id = str(arguments["notebook_id"])
            notebook = self.repo.get(notebook_id)
            return {
                "name": name,
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un asistente de investigación riguroso y claro.",
                    },
                    {
                        "role": "user",
                        "content": (
                            "Genera un brief en español con: objetivo, hipótesis,"
                            " metodología sugerida, riesgos y próximos pasos. "
                            f"Contexto: título='{notebook.title}', secciones={notebook.sections}."
                        ),
                    },
                ],
            }

        notebook_id = str(arguments["notebook_id"])
        days = int(arguments.get("days", 7))
        notebook = self.repo.get(notebook_id)
        return {
            "name": name,
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un tutor experto en aprendizaje activo.",
                },
                {
                    "role": "user",
                    "content": (
                        f"Diseña un plan de estudio de {days} días basado en el cuaderno "
                        f"'{notebook.title}'. Incluye metas diarias, repaso espaciado y autoevaluaciones."
                    ),
                },
            ],
        }

    def _validate_arguments(self, name: str, arguments: dict[str, Any], schema: dict[str, Any]) -> None:
        if not isinstance(arguments, dict):
            raise PromptValidationError(f"{name}: argumentos inválidos, se esperaba object")

        required = schema.get("required", [])
        properties = schema.get("properties", {})

        for key in required:
            if key not in arguments:
                raise PromptValidationError(f"{name}: falta argumento requerido '{key}'")

        for key, value in arguments.items():
            if key not in properties:
                raise PromptValidationError(f"{name}: argumento no permitido '{key}'")
            prop = properties[key]
            expected_type = prop.get("type")
            if expected_type == "string" and not isinstance(value, str):
                raise PromptValidationError(f"{name}: '{key}' debe ser string")
            if expected_type == "integer":
                if not isinstance(value, int) or isinstance(value, bool):
                    raise PromptValidationError(f"{name}: '{key}' debe ser integer")
                minimum = prop.get("minimum")
                maximum = prop.get("maximum")
                if minimum is not None and value < minimum:
                    raise PromptValidationError(f"{name}: '{key}' debe ser >= {minimum}")
                if maximum is not None and value > maximum:
                    raise PromptValidationError(f"{name}: '{key}' debe ser <= {maximum}")
