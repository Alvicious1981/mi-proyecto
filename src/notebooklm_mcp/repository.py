from __future__ import annotations

from collections import defaultdict
from copy import deepcopy

from .models import ChangeLog, Notebook, utc_now


class NotebookRepository:
    """Repositorio en memoria para iniciar desarrollo del dominio Notebook."""

    def __init__(self) -> None:
        self._notebooks: dict[str, Notebook] = {}
        self._history: defaultdict[str, list[ChangeLog]] = defaultdict(list)

    def add(self, notebook: Notebook) -> Notebook:
        self._notebooks[notebook.id] = deepcopy(notebook)
        return deepcopy(notebook)

    def get(self, notebook_id: str) -> Notebook:
        notebook = self._notebooks.get(notebook_id)
        if notebook is None:
            raise KeyError(f"Notebook '{notebook_id}' no existe")
        return deepcopy(notebook)

    def list(self) -> list[Notebook]:
        return [deepcopy(n) for n in self._notebooks.values()]

    def update(self, notebook: Notebook) -> Notebook:
        if notebook.id not in self._notebooks:
            raise KeyError(f"Notebook '{notebook.id}' no existe")
        notebook.updated_at = utc_now()
        self._notebooks[notebook.id] = deepcopy(notebook)
        return deepcopy(notebook)

    def record(self, log: ChangeLog) -> ChangeLog:
        self._history[log.notebook_id].append(deepcopy(log))
        return deepcopy(log)

    def history(self, notebook_id: str) -> list[ChangeLog]:
        return [deepcopy(log) for log in self._history[notebook_id]]


    def replace_state(
        self,
        notebooks: list[Notebook],
        history: dict[str, list[ChangeLog]],
    ) -> None:
        self._notebooks = {notebook.id: deepcopy(notebook) for notebook in notebooks}
        self._history = defaultdict(list)
        for notebook_id, logs in history.items():
            self._history[notebook_id] = [deepcopy(log) for log in logs]
