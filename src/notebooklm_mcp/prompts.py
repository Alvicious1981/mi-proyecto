from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .repository import NotebookRepository


@dataclass(frozen=True, slots=True)
class PromptDefinition:
    name: str
    description: str
    arguments: tuple[str, ...]


class PromptService:
    """Prompts MCP básicos para guiar flujos de investigación y estudio."""

    def __init__(self, repo: NotebookRepository) -> None:
        self.repo = repo

    def list_prompts(self) -> list[dict[str, Any]]:
        prompts = [
            PromptDefinition(
                name="research_brief",
                description="Genera un brief de investigación con objetivos, hipótesis y riesgos.",
                arguments=("notebook_id",),
            ),
            PromptDefinition(
                name="study_plan",
                description="Crea un plan de estudio accionable a partir del cuaderno.",
                arguments=("notebook_id", "days"),
            ),
        ]
        return [
            {"name": p.name, "description": p.description, "arguments": list(p.arguments)}
            for p in prompts
        ]

    def get_prompt(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
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

        if name == "study_plan":
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

        raise KeyError(f"Prompt no encontrado: {name}")
