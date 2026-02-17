# mi-proyecto

Implementación inicial de una aplicación MCP para NotebookLM.

## Estado actual

Se inició el desarrollo de:

- **Gestión de Cuadernos** (`create`, `merge`, `cleanup`, `search`, `apply_template`, `history`).
- **Análisis de Contenido (base)**:
  - detección de contradicciones e información faltante,
  - sugerencias automáticas de preguntas clave,
  - análisis de tono básico.
- **Investigación y Fuentes (base)**:
  - búsqueda con citas estructuradas (`title`, `url`, `accessed_at`, `snippet`, `relevance`),
  - traducción básica ES/EN basada en glosario.
- **Creación de Material (base)**:
  - paquete audiovisual inicial,
  - vista previa dinámica,
  - mapa mental base,
  - exportación de resumen (`md`, `txt`, `json`).
- **Herramientas de Estudio (base)**:
  - generación de quiz,
  - mapa mental interactivo.
- Registro de herramientas MCP para los dominios `notebook.*`, `analysis.*`, `research.*`, `material.*` y `study.*`.
- Validación de entrada por `inputSchema` con errores claros de contrato antes de ejecutar handlers.
- Descriptor/handshake base para compatibilidad de descubrimiento con Agent Managers.
- Soporte de listado/lectura de recursos MCP (`list_resources`, `read_resource`).
- Soporte de prompts MCP (`list_prompts`, `get_prompt`) para flujos guiados de investigación/estudio, con validación de argumentos.
- Pruebas unitarias para validar los flujos base.

## Estructura

- `src/notebooklm_mcp/models.py`: modelos de dominio (`Notebook`, `ChangeLog`).
- `src/notebooklm_mcp/repository.py`: repositorio en memoria.
- `src/notebooklm_mcp/services.py`: lógica de negocio para cuadernos.
- `src/notebooklm_mcp/analysis.py`: análisis de contradicciones, preguntas y tono.
- `src/notebooklm_mcp/research.py`: búsqueda con citas y traducción de fuentes.
- `src/notebooklm_mcp/material.py`: creación de material y exportación de resúmenes.
- `src/notebooklm_mcp/study.py`: generación de quizzes y mapas interactivos.
- `src/notebooklm_mcp/mcp_server.py`: herramientas MCP registradas, handshake y descriptor.
- `src/notebooklm_mcp/validation.py`: validación de argumentos contra schemas de tools MCP.
- `src/notebooklm_mcp/resources.py`: recursos MCP estáticos y dinámicos por cuaderno.
- `src/notebooklm_mcp/prompts.py`: prompts MCP predefinidos para research/study plan.
- `tests/test_notebook_service.py`: pruebas de comportamiento.

## Ejecutar pruebas

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Exportar descriptor MCP

```bash
PYTHONPATH=src python scripts/export_descriptor.py
```

El descriptor se genera en `artifacts/mcp-descriptor.json`.
