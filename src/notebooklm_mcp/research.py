from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True, slots=True)
class SearchDocument:
    title: str
    url: str
    snippet: str
    language: str = "es"


_DEFAULT_SEARCH_DOCS: tuple[SearchDocument, ...] = (
    SearchDocument(
        title="Model Context Protocol - Introducción",
        url="https://modelcontextprotocol.io/introduction",
        snippet="MCP estandariza cómo los modelos se conectan con herramientas y fuentes externas de forma segura.",
        language="es",
    ),
    SearchDocument(
        title="NotebookLM overview",
        url="https://support.google.com/notebooklm/answer/",
        snippet="NotebookLM permite sintetizar fuentes y generar respuestas con contexto de tus documentos.",
        language="es",
    ),
    SearchDocument(
        title="Prompting Guide for Research",
        url="https://www.promptingguide.ai/",
        snippet="Guías de prompting para descomponer problemas complejos y estructurar preguntas de investigación.",
        language="es",
    ),
    SearchDocument(
        title="MCP Specification",
        url="https://github.com/modelcontextprotocol/specification",
        snippet="La especificación de MCP define herramientas, recursos y contratos de mensajes entre cliente y servidor.",
        language="es",
    ),
)


_TRANSLATION_GLOSSARY = {
    ("es", "en"): {
        "cuaderno": "notebook",
        "investigación": "research",
        "fuentes": "sources",
        "resumen": "summary",
        "preguntas": "questions",
        "contradicciones": "contradictions",
    },
    ("en", "es"): {
        "notebook": "cuaderno",
        "research": "investigación",
        "sources": "fuentes",
        "summary": "resumen",
        "questions": "preguntas",
        "contradictions": "contradicciones",
    },
}


class ResearchService:
    """Servicio base de investigación con citas y traducción ligera."""

    def __init__(self, corpus: tuple[SearchDocument, ...] | None = None) -> None:
        self.corpus = corpus or _DEFAULT_SEARCH_DOCS

    def web_search_with_citations(self, query: str, limit: int = 5, language: str = "es") -> dict:
        tokens = self._tokenize(query)
        candidates: list[tuple[int, SearchDocument]] = []

        for doc in self.corpus:
            if language and doc.language != language:
                continue
            score = self._score(tokens, f"{doc.title} {doc.snippet}")
            if score > 0:
                candidates.append((score, doc))

        candidates.sort(key=lambda item: item[0], reverse=True)
        selected = candidates[:limit]

        citations = [
            {
                "title": doc.title,
                "url": doc.url,
                "accessed_at": _now_iso(),
                "snippet": doc.snippet,
                "relevance": score,
            }
            for score, doc in selected
        ]

        return {
            "query": query,
            "language": language,
            "results": citations,
            "total": len(citations),
        }

    def translate_source(
        self,
        text: str,
        target_language: str,
        source_language: str = "auto",
    ) -> dict:
        detected_source = self._detect_language(text) if source_language == "auto" else source_language
        translated = self._translate_text(text, detected_source, target_language)

        return {
            "source_language": detected_source,
            "target_language": target_language,
            "original_text": text,
            "translated_text": translated,
            "method": "rule_based_glossary",
        }

    def _tokenize(self, text: str) -> set[str]:
        return {tok for tok in re.findall(r"[\wáéíóúñ]+", text.lower()) if len(tok) > 2}

    def _score(self, query_tokens: set[str], text: str) -> int:
        if not query_tokens:
            return 0
        text_tokens = self._tokenize(text)
        return len(query_tokens & text_tokens)

    def _detect_language(self, text: str) -> str:
        lowered = text.lower()
        spanish_markers = {" el ", " la ", " de ", " y ", " investigación "}
        english_markers = {" the ", " and ", " of ", " research "}

        score_es = sum(marker in f" {lowered} " for marker in spanish_markers)
        score_en = sum(marker in f" {lowered} " for marker in english_markers)
        return "es" if score_es >= score_en else "en"

    def _translate_text(self, text: str, source_language: str, target_language: str) -> str:
        if source_language == target_language:
            return text

        glossary = _TRANSLATION_GLOSSARY.get((source_language, target_language))
        if glossary is None:
            return text

        output = text
        for source_term, target_term in glossary.items():
            output = re.sub(rf"\b{re.escape(source_term)}\b", target_term, output, flags=re.IGNORECASE)
        return output
