# Especificación de Producto (spec.md)
## Proyecto: MCP para NotebookLM

**Versión:** 1.0 (borrador inicial)  
**Fecha:** 2026-02-16  
**Idioma:** ES  
**Estado:** Listo para fase de arquitectura e implementación

---

## 1) Resumen ejecutivo

Esta especificación define una aplicación **MCP (Model Context Protocol)** orientada a potenciar NotebookLM con capacidades avanzadas de investigación, análisis, generación de materiales y estudio. El objetivo es centralizar flujos de trabajo académicos/profesionales en una experiencia minimalista, intuitiva y moderna, con foco en seguridad, trazabilidad y escalabilidad.

El servidor MCP expondrá herramientas para:
- gestión integral de cuadernos,
- análisis profundo de contenido,
- generación de materiales de aprendizaje,
- estudio activo (tests y mapas interactivos),
- y soporte de búsqueda con citas verificables.

Además, el diseño UI contemplará glasmorfismo para paneles laterales y popups, paleta suave, alto contraste legible y una experiencia consistente para escritorio.

---

## 2) Objetivos y no-objetivos

### 2.1 Objetivos
1. Entregar una base funcional MCP para NotebookLM con herramientas agrupadas por dominios de uso.
2. Ofrecer resultados trazables (historial, citas, fuentes y auditoría de cambios).
3. Garantizar seguridad y privacidad de datos sensibles (fuentes, notas, resultados de análisis).
4. Definir arquitectura extensible para crecimiento por módulos.
5. Validar compatibilidad funcional con **Agent Manager de Antigravity**.

### 2.2 No-objetivos (MVP)
- No reemplazar NotebookLM ni su UI principal.
- No construir una suite de edición multimedia profesional.
- No soportar todos los idiomas en profundidad desde el día 1 (se prioriza ES/EN).

---

## 3) Alcance funcional

## 3.1 Gestión de Cuadernos

### F1. Crear nuevos cuadernos
- Crear cuaderno con metadatos: título, descripción, etiquetas, idioma.
- Configurar plantilla inicial (investigación académica, producto, legal, técnico).
- Retornar ID único y timestamp.

### F2. Fusionar cuadernos existentes
- Fusionar dos o más cuadernos en uno nuevo o en uno destino.
- Resolver conflictos por estrategia: `prioridad_reciente`, `prioridad_origen`, `manual`.
- Registrar árbol de procedencia de contenidos.

### F3. Depurar cuadernos
- Detección de duplicados semánticos y literales.
- Limpieza de secciones vacías/obsoletas.
- Reindexado de referencias internas.

### F4. Búsqueda rápida dentro de cuadernos
- Búsqueda por keyword, semántica y filtros (fecha, fuente, etiqueta).
- Snippets con resaltado de coincidencias.
- Soporte para orden por relevancia y recencia.

### F5. Plantillas predefinidas para investigación
- Biblioteca de plantillas versionadas.
- Variables parametrizables por plantilla (objetivo, hipótesis, alcance, etc.).
- Posibilidad de personalizar y guardar variantes.

### F6. Historial de cambios
- Timeline por cuaderno: crear, editar, fusionar, depurar, exportar.
- Diff resumido por sección.
- Opcional: reversión de cambios (fase posterior al MVP).

## 3.2 Análisis de Contenido

### F7. Detección de contradicciones o información faltante
- Comparación de afirmaciones entre fuentes.
- Marcado de contradicciones con evidencia y nivel de confianza.
- Detección de huecos temáticos respecto al objetivo del cuaderno.

### F8. Sugerencias automáticas de temas y preguntas clave
- Generación de preguntas abiertas/cerradas según el contexto.
- Priorización por impacto en la investigación.
- Recomendaciones de próximos pasos.

### F9. Análisis del tono de fuentes
- Clasificación de tono (neutral, persuasivo, crítico, promocional, etc.).
- Señales de sesgo y lenguaje cargado.
- Resumen explicativo por documento.

### F10. Búsqueda de información adicional en internet (con citas)
- Recuperación de fuentes externas relevantes.
- Entrega de citas estructuradas: título, URL, fecha de acceso, extracto.
- Señalización de confiabilidad básica (dominio, actualidad, consistencia).

### F11. Traducción de fuentes
- Traducción ES↔EN (extensible a más idiomas).
- Preservación de contexto técnico y términos clave.
- Alineación segmento original/traducido para trazabilidad.

## 3.3 Creación de Material

### F12. Generación de material audiovisual
- Storyboard o guion breve a partir de resumen del cuaderno.
- Activos iniciales: texto narrativo, lista de escenas, prompts para visuales.
- Exportable a herramientas externas (fase inicial sin render nativo pesado).

### F13. Vista previa dinámica del material
- Preview de estructura de presentación/video.
- Simulación de secuencia de diapositivas o bloques narrativos.
- Revisión rápida con feedback iterativo.

### F14. Mapas mentales que conecten ideas principales
- Extracción de nodos principales/secundarios.
- Enlaces con tipo de relación (causalidad, dependencia, contraste).
- Exportación a JSON de grafo.

### F15. Exportación de resúmenes a formatos de presentación
- Exportación a `.pptx`, `.md` y `.pdf` (cuando esté disponible en backend).
- Plantillas visuales simples y corporativas.
- Inclusión de notas del presentador y bibliografía.

## 3.4 Herramientas de Estudio

### F16. Tests automáticos basados en contenido
- Generación de preguntas tipo opción múltiple, verdadero/falso, respuesta corta.
- Dificultad configurable (baja/media/alta).
- Clave de respuestas y justificación por pregunta.

### F17. Mapas mentales interactivos
- Navegación expandir/colapsar nodos.
- Filtro por categorías o fuentes.
- Modo “repaso” con tarjetas vinculadas a nodos.

---

## 4) Requisitos de experiencia (UX/UI)

1. **Diseño minimalista e intuitivo**
   - Navegación por tareas principales (Cuadernos, Análisis, Material, Estudio).
   - Menos clics para acciones frecuentes.

2. **Colores suaves**
   - Paleta base pastel/desaturada.
   - Contraste AA mínimo para texto.

3. **Glasmorfismo**
   - Aplicar en panel lateral y modales/popup.
   - Fondo translúcido + blur + bordes suaves + sombras ligeras.
   - Mantener rendimiento en equipos medios (fallback sin blur).

4. **Accesibilidad**
   - Navegación por teclado.
   - Textos alternativos en elementos visuales.
   - Soporte modo oscuro.

---

## 5) Requisitos no funcionales

## 5.1 Seguridad y Privacidad

### Autenticación y autorización
- Entorno privado (single-user) dentro de Antigravity Agent Manager.
- Sin capa de autenticación de usuarios final en MVP (se asume sesión privada del entorno).
- Autorización mínima local: rol `owner` único para operaciones administrativas.

### Protección de datos
- Cifrado en tránsito (TLS 1.2+) y en reposo (AES-256 o equivalente del proveedor).
- Separación de datos por workspace/proyecto.
- Registro de auditoría para acciones críticas.

### Privacidad
- Política explícita de retención y borrado.
- Soporte para exportación/borrado de datos de usuario.
- Minimización de datos y enmascaramiento de PII en logs.

### Gestión de secretos
- Variables de entorno + secret manager.
- Rotación periódica de claves/API keys.

## 5.2 Escalabilidad y Mantenimiento
- Arquitectura modular por dominio funcional (notebooks, analysis, study, export).
- API estable con versionado semántico (`v1`, `v1.1`...).
- Colas asíncronas para tareas largas (análisis, exportación, generación).
- Observabilidad: logs estructurados, métricas, trazas.
- Estrategia de testing: unitarias, integración, contrato MCP.
- Documentación técnica viva (ADRs + changelog).

## 5.3 Compatibilidad con Agent Manager de Antigravity
- Cumplimiento del protocolo MCP estándar para tools/resources/prompts.
- Descriptor del servidor compatible con descubrimiento del Agent Manager.
- Contratos de entrada/salida fuertemente tipados (JSON schema).
- Pruebas de handshake, listado de herramientas y ejecución básica.

---

## 6) Arquitectura propuesta (alto nivel)

### 6.1 Componentes
1. **MCP Server Core**
   - Registro de tools/resources.
   - Validación de schemas.
2. **Notebook Domain Service**
   - CRUD de cuadernos, merge, depuración, historial.
3. **Analysis Service**
   - Contradicciones, huecos, tono, sugerencias.
4. **Research Connector Service**
   - Búsqueda web y normalización de citas.
5. **Material Service**
   - Generación de resúmenes, guiones, mapas mentales, exportaciones.
6. **Study Service**
   - Generación de tests y mapas interactivos.
7. **Persistence Layer**
   - DB relacional + índice semántico/vectorial (si aplica).
8. **Auth & Audit Module**
   - Sesiones, permisos, bitácora.

### 6.2 Modelo de datos (resumen)
- `Notebook(id, title, description, tags, language, template_id, created_at, updated_at)`
- `Source(id, notebook_id, type, uri, content_hash, metadata)`
- `Insight(id, notebook_id, kind, confidence, payload, created_at)`
- `Citation(id, source_id, url, title, accessed_at, snippet)`
- `ChangeLog(id, notebook_id, actor, action, diff_summary, timestamp)`
- `Quiz(id, notebook_id, difficulty, items_json, answer_key_json)`

### 6.3 Herramientas MCP (propuesta inicial)
- `notebook.create`
- `notebook.merge`
- `notebook.cleanup`
- `notebook.search`
- `notebook.apply_template`
- `notebook.history`
- `analysis.find_contradictions`
- `analysis.suggest_questions`
- `analysis.tone`
- `research.web_search_with_citations`
- `research.translate_source`
- `material.generate_audiovisual_pack`
- `material.preview`
- `material.generate_mindmap`
- `material.export_summary`
- `study.generate_quiz`
- `study.interactive_mindmap`

---

## 7) Flujos clave

1. **Crear cuaderno → cargar fuentes → analizar contradicciones → generar preguntas**.
2. **Fusionar cuadernos → depurar duplicados → exportar resumen para presentación**.
3. **Traducir fuentes → analizar tono → generar test de estudio**.

---

## 8) Plan detallado (antes de codificar)

## Fase 0 — Descubrimiento y definición (1 semana)
- Validar casos de uso prioritarios (3 perfiles: estudiante, investigador, analista).
- Definir MVP exacto y criterios de aceptación.
- Confirmar restricciones de NotebookLM y Antigravity Agent Manager.

## Fase 1 — Arquitectura y contratos (1 semana)
- Diseñar contratos MCP (input/output + errores).
- Definir modelo de datos y estrategia de almacenamiento.
- Especificar seguridad (auth, permisos, auditoría, retención).

## Fase 2 — Implementación núcleo (2 semanas)
- Implementar `notebook.*` + historial.
- Implementar `analysis.*` base (contradicciones, sugerencias, tono).
- Implementar `research.*` con citas estructuradas.

## Fase 3 — Material y estudio (2 semanas)
- Implementar `material.*` (preview, mapa mental, exportación).
- Implementar `study.*` (quiz + mapa mental interactivo).

## Fase 4 — UX/UI y estilo visual (1 semana)
- Aplicar sistema visual minimalista + colores suaves.
- Implementar glasmorfismo en panel lateral y modales.
- Revisar accesibilidad y rendimiento.

## Fase 5 — QA, hardening y compatibilidad (1 semana)
- Pruebas de contratos MCP y regresión.
- Validación de seguridad (logs, PII, permisos).
- Verificación final con Agent Manager de Antigravity.

## Fase 6 — Lanzamiento incremental (continuo)
- Beta cerrada.
- Métricas de uso y calidad.
- Priorización de mejoras por feedback.

---

## 9) Lista de tareas (backlog inicial)

## 9.1 Producto y diseño
- [ ] Definir mapa de navegación principal y flujos MVP.
- [ ] Diseñar sistema visual (tokens, componentes, estados).
- [ ] Prototipar panel lateral y modales con glasmorfismo.
- [ ] Especificar criterios de accesibilidad (teclado, contraste, foco).

## 9.2 Backend MCP
- [ ] Crear esqueleto del servidor MCP y registro de herramientas.
- [ ] Definir schemas JSON para todas las tools del MVP.
- [ ] Implementar módulo `notebook` (create, merge, cleanup, search, history).
- [ ] Implementar módulo `analysis` (contradicciones, preguntas, tono).
- [ ] Implementar módulo `research` (web search con citas + traducción).
- [ ] Implementar módulo `material` (preview, mindmap, export).
- [ ] Implementar módulo `study` (quiz + mapa interactivo).

## 9.3 Datos e infraestructura
- [ ] Diseñar esquema de base de datos y migraciones.
- [ ] Implementar storage para historial y auditoría.
- [ ] Definir estrategia de indexado semántico (si aplica).
- [ ] Configurar colas para tareas asíncronas pesadas.

## 9.4 Seguridad y cumplimiento
- [ ] Mantener autorización mínima owner-only para entorno privado y documentar límites.
- [ ] Aplicar cifrado en tránsito/descanso.
- [ ] Añadir política de retención y borrado de datos.
- [ ] Implementar redacción de PII en logs.

## 9.5 QA y observabilidad
- [ ] Crear pruebas unitarias para lógica de dominio.
- [ ] Crear pruebas de integración para endpoints MCP.
- [ ] Añadir pruebas de contrato (schemas y errores).
- [ ] Configurar métricas, logs estructurados y trazas.
- [ ] Ejecutar checklist de compatibilidad con Agent Manager.

## 9.6 Documentación
- [ ] Documentar herramientas MCP y ejemplos de payload.
- [ ] Crear guía de despliegue local y producción.
- [ ] Mantener changelog y ADRs técnicos.

---

## 10) Riesgos y mitigaciones

1. **Calidad de citas web inconsistente**  
   Mitigación: validadores de fuente, ranking por confiabilidad, caché y revisión humana opcional.

2. **Costos/latencia en análisis avanzado**  
   Mitigación: colas asíncronas, resultados parciales, caching semántico.

3. **Complejidad de merge de cuadernos**  
   Mitigación: políticas configurables y vista de conflictos.

4. **Riesgo de privacidad por fuentes sensibles**  
   Mitigación: cifrado, control de acceso fino y auditoría.

---

## 11) Criterios de aceptación del MVP

- Se pueden crear, fusionar, depurar y buscar cuadernos con historial visible.
- Se detectan contradicciones básicas y se sugieren preguntas clave.
- La búsqueda web retorna citas estructuradas con URL y extracto.
- Se pueden generar tests y mapa mental básico.
- Se exporta al menos un formato de resumen (`.md` o `.pptx`).
- Seguridad mínima implementada (entorno privado + autorización owner-only + logs de auditoría).
- Compatibilidad validada en flujo básico con Agent Manager de Antigravity.

---

## 12) Referencias

- Repositorio de referencia solicitado: `jacob-bd/notebooklm-mcp-cli`.
- Nota: En este entorno no se pudo consultar en línea el repositorio por restricciones de red; la especificación se construyó con buenas prácticas MCP y los requisitos funcionales proporcionados.
