from __future__ import annotations

from dataclasses import asdict

from .models import ChangeLog, Notebook
from .repository import NotebookRepository


DEFAULT_TEMPLATES = {
    "investigacion_academica": [
        "Problema de investigación",
        "Hipótesis",
        "Metodología",
        "Resultados esperados",
    ],
    "analisis_producto": ["Objetivo", "Métricas", "Hallazgos", "Recomendaciones"],
}


class NotebookService:
    def __init__(self, repo: NotebookRepository | None = None) -> None:
        self.repo = repo or NotebookRepository()

    def create_notebook(
        self,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
        language: str = "es",
        template_id: str | None = None,
        actor: str = "system",
    ) -> dict:
        notebook = Notebook(
            title=title,
            description=description,
            tags=tags or [],
            language=language,
            template_id=template_id,
            sections=DEFAULT_TEMPLATES.get(template_id, []).copy(),
        )
        created = self.repo.add(notebook)
        self.repo.record(
            ChangeLog(
                notebook_id=created.id,
                actor=actor,
                action="notebook.create",
                diff_summary=f"Creado cuaderno '{created.title}'",
            )
        )
        return self._serialize_notebook(created)

    def merge_notebooks(
        self,
        source_ids: list[str],
        destination_title: str,
        strategy: str = "prioridad_reciente",
        actor: str = "system",
    ) -> dict:
        if len(source_ids) < 2:
            raise ValueError("Se requieren al menos 2 cuadernos para fusionar")

        sources = [self.repo.get(notebook_id) for notebook_id in source_ids]
        descriptions = "\n\n".join(filter(None, [n.description for n in sources]))
        merged_sections = self._merge_sections(sources, strategy)

        merged = Notebook(
            title=destination_title,
            description=descriptions,
            tags=sorted({tag for n in sources for tag in n.tags}),
            language=sources[0].language,
            sections=merged_sections,
        )
        created = self.repo.add(merged)
        self.repo.record(
            ChangeLog(
                notebook_id=created.id,
                actor=actor,
                action="notebook.merge",
                diff_summary=f"Fusiona {len(source_ids)} cuadernos en '{destination_title}'",
                metadata={"sources": source_ids, "strategy": strategy},
            )
        )
        return self._serialize_notebook(created)

    def cleanup_notebook(self, notebook_id: str, actor: str = "system") -> dict:
        notebook = self.repo.get(notebook_id)
        seen: set[str] = set()
        unique_sections: list[str] = []
        removed = 0
        for section in notebook.sections:
            normalized = section.strip().lower()
            if not normalized or normalized in seen:
                removed += 1
                continue
            seen.add(normalized)
            unique_sections.append(section.strip())

        notebook.sections = unique_sections
        updated = self.repo.update(notebook)
        self.repo.record(
            ChangeLog(
                notebook_id=notebook_id,
                actor=actor,
                action="notebook.cleanup",
                diff_summary=f"Depuración finalizada. Se eliminaron {removed} secciones",
            )
        )
        return self._serialize_notebook(updated)

    def search_notebooks(self, query: str, tag: str | None = None) -> list[dict]:
        q = query.strip().lower()
        results: list[dict] = []
        for notebook in self.repo.list():
            if tag and tag not in notebook.tags:
                continue
            haystack = " ".join([notebook.title, notebook.description, *notebook.sections]).lower()
            if q in haystack:
                results.append(
                    {
                        "id": notebook.id,
                        "title": notebook.title,
                        "snippet": self._build_snippet(notebook, q),
                    }
                )
        return results

    def apply_template(self, notebook_id: str, template_id: str, actor: str = "system") -> dict:
        if template_id not in DEFAULT_TEMPLATES:
            raise ValueError(f"Plantilla desconocida: {template_id}")
        notebook = self.repo.get(notebook_id)
        notebook.template_id = template_id
        notebook.sections = DEFAULT_TEMPLATES[template_id].copy()
        updated = self.repo.update(notebook)
        self.repo.record(
            ChangeLog(
                notebook_id=notebook_id,
                actor=actor,
                action="notebook.apply_template",
                diff_summary=f"Plantilla aplicada: {template_id}",
            )
        )
        return self._serialize_notebook(updated)

    def notebook_history(self, notebook_id: str) -> list[dict]:
        return [
            {
                "id": log.id,
                "action": log.action,
                "actor": log.actor,
                "diff_summary": log.diff_summary,
                "metadata": log.metadata,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in self.repo.history(notebook_id)
        ]

    def _merge_sections(self, notebooks: list[Notebook], strategy: str) -> list[str]:
        if strategy == "prioridad_origen":
            ordered = notebooks
        else:
            ordered = sorted(notebooks, key=lambda n: n.updated_at, reverse=True)

        merged: list[str] = []
        seen: set[str] = set()
        for notebook in ordered:
            for section in notebook.sections:
                normalized = section.strip().lower()
                if normalized and normalized not in seen:
                    seen.add(normalized)
                    merged.append(section.strip())
        return merged

    def _build_snippet(self, notebook: Notebook, query: str) -> str:
        text = " | ".join([notebook.title, notebook.description, *notebook.sections])
        idx = text.lower().find(query)
        if idx < 0:
            return text[:120]
        start = max(idx - 25, 0)
        end = min(idx + 80, len(text))
        return text[start:end]

    def _serialize_notebook(self, notebook: Notebook) -> dict:
        payload = asdict(notebook)
        payload["created_at"] = notebook.created_at.isoformat()
        payload["updated_at"] = notebook.updated_at.isoformat()
        return payload
