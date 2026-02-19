from __future__ import annotations

from .repository import NotebookRepository


class StudyService:
    """Herramientas iniciales de estudio sobre contenido del cuaderno."""

    def __init__(self, repo: NotebookRepository) -> None:
        self.repo = repo

    def generate_quiz(self, notebook_id: str, difficulty: str = "media", limit: int = 5) -> dict:
        notebook = self.repo.get(notebook_id)
        questions: list[dict] = []

        for idx, section in enumerate(notebook.sections[:limit]):
            options = [
                f"Definición de {section}",
                f"Riesgo asociado a {section}",
                f"Aplicación de {section}",
                f"Ninguna de las anteriores",
            ]
            questions.append(
                {
                    "id": idx + 1,
                    "type": "multiple_choice",
                    "question": f"¿Qué describe mejor el tema '{section}'?",
                    "options": options,
                    "answer_index": 0,
                    "justification": f"El cuaderno presenta '{section}' como tópico principal.",
                }
            )

        return {
            "notebook_id": notebook_id,
            "difficulty": difficulty,
            "questions": questions,
            "total": len(questions),
        }

    def interactive_mindmap(self, notebook_id: str) -> dict:
        notebook = self.repo.get(notebook_id)
        nodes = []
        for idx, section in enumerate(notebook.sections):
            nodes.append(
                {
                    "id": f"topic-{idx + 1}",
                    "label": section,
                    "expandable": True,
                    "flashcard": f"Explica con tus palabras: {section}",
                }
            )

        links = [
            {
                "from": nodes[idx]["id"],
                "to": nodes[idx + 1]["id"],
                "type": "next",
            }
            for idx in range(max(len(nodes) - 1, 0))
        ]

        return {"notebook_id": notebook_id, "nodes": nodes, "links": links}
