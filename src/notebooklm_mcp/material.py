from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha1

from .repository import NotebookRepository


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MaterialService:
    """Generación inicial de materiales desde notebooks."""

    def __init__(self, repo: NotebookRepository) -> None:
        self.repo = repo

    def generate_audiovisual_pack(self, notebook_id: str, style: str = "minimal") -> dict:
        notebook = self.repo.get(notebook_id)
        sections = [s for s in notebook.sections if s.strip()]
        scenes = [
            {
                "scene": idx + 1,
                "title": section,
                "narration": f"En esta parte se desarrolla: {section}.",
                "visual_prompt": f"{style} style, glassmorphism card, topic: {section}",
            }
            for idx, section in enumerate(sections[:8])
        ]

        return {
            "notebook_id": notebook_id,
            "style": style,
            "created_at": _utc_now(),
            "scenes": scenes,
            "total_scenes": len(scenes),
        }

    def preview(self, notebook_id: str, mode: str = "slides") -> dict:
        notebook = self.repo.get(notebook_id)
        blocks = [
            {
                "index": idx + 1,
                "headline": section,
                "bullet": f"Punto clave sobre {section.lower()}",
            }
            for idx, section in enumerate(notebook.sections[:10])
        ]
        return {"notebook_id": notebook_id, "mode": mode, "blocks": blocks}

    def generate_mindmap(self, notebook_id: str) -> dict:
        notebook = self.repo.get(notebook_id)
        root_id = f"node-{sha1(notebook.title.encode()).hexdigest()[:8]}"
        nodes = [{"id": root_id, "label": notebook.title, "type": "root"}]
        edges: list[dict] = []

        for idx, section in enumerate(notebook.sections):
            node_id = f"node-{idx + 1}"
            nodes.append({"id": node_id, "label": section, "type": "topic"})
            edges.append({"from": root_id, "to": node_id, "relation": "contains"})

        return {"notebook_id": notebook_id, "nodes": nodes, "edges": edges}

    def export_summary(self, notebook_id: str, format: str = "md") -> dict:
        notebook = self.repo.get(notebook_id)
        supported = {"md", "txt", "json"}
        if format not in supported:
            raise ValueError(f"Formato no soportado: {format}")

        if format == "md":
            content = self._as_markdown(notebook.title, notebook.sections)
        elif format == "txt":
            content = self._as_text(notebook.title, notebook.sections)
        else:
            content = {"title": notebook.title, "sections": notebook.sections}

        return {
            "notebook_id": notebook_id,
            "format": format,
            "generated_at": _utc_now(),
            "content": content,
        }

    def _as_markdown(self, title: str, sections: list[str]) -> str:
        lines = [f"# {title}", ""]
        lines.extend(f"- {section}" for section in sections)
        return "\n".join(lines)

    def _as_text(self, title: str, sections: list[str]) -> str:
        lines = [title, "=" * len(title), ""]
        lines.extend(f"* {section}" for section in sections)
        return "\n".join(lines)
