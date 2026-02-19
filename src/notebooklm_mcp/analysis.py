from __future__ import annotations

from dataclasses import dataclass

from .repository import NotebookRepository


_NEGATION_WORDS = {"no", "nunca", "jamás", "sin"}
_TONE_LEXICON = {
    "promocional": {"increíble", "revolucionario", "único", "imperdible", "garantizado"},
    "critico": {"riesgo", "falla", "problema", "limitación", "debilidad"},
    "neutral": {"define", "describe", "explica", "analiza", "presenta"},
}


@dataclass(slots=True)
class Claim:
    subject: str
    text: str
    is_negative: bool


class AnalysisService:
    """Análisis inicial de contenido para notebooks usando heurísticas ligeras."""

    def __init__(self, repo: NotebookRepository) -> None:
        self.repo = repo

    def find_contradictions(self, notebook_id: str) -> dict:
        notebook = self.repo.get(notebook_id)
        claims = [self._extract_claim(section) for section in notebook.sections if section.strip()]
        claims = [claim for claim in claims if claim is not None]

        by_subject: dict[str, list[Claim]] = {}
        for claim in claims:
            by_subject.setdefault(claim.subject, []).append(claim)

        contradictions: list[dict] = []
        for subject, subject_claims in by_subject.items():
            has_positive = any(not claim.is_negative for claim in subject_claims)
            has_negative = any(claim.is_negative for claim in subject_claims)
            if has_positive and has_negative:
                contradictions.append(
                    {
                        "subject": subject,
                        "confidence": 0.65,
                        "evidence": [claim.text for claim in subject_claims],
                    }
                )

        missing_information = self._detect_missing_sections(notebook.sections)
        return {
            "notebook_id": notebook_id,
            "contradictions": contradictions,
            "missing_information": missing_information,
        }

    def suggest_questions(self, notebook_id: str, limit: int = 5) -> dict:
        notebook = self.repo.get(notebook_id)
        topics = [section.strip() for section in notebook.sections if section.strip()]
        questions: list[dict] = []

        for topic in topics:
            questions.append({"question": f"¿Qué evidencia respalda '{topic}'?", "priority": "alta"})
            questions.append({"question": f"¿Qué riesgos o límites tiene '{topic}'?", "priority": "media"})

        if not questions:
            questions.append(
                {
                    "question": "¿Cuál es la hipótesis principal y cómo se validará?",
                    "priority": "alta",
                }
            )

        return {"notebook_id": notebook_id, "questions": questions[:limit]}

    def analyze_tone(self, notebook_id: str) -> dict:
        notebook = self.repo.get(notebook_id)
        combined = " ".join(notebook.sections).lower()
        scores = {tone: self._count_hits(combined, words) for tone, words in _TONE_LEXICON.items()}
        primary_tone = max(scores, key=scores.get) if any(scores.values()) else "neutral"

        return {
            "notebook_id": notebook_id,
            "primary_tone": primary_tone,
            "scores": scores,
            "summary": self._tone_summary(primary_tone),
        }

    def _extract_claim(self, text: str) -> Claim | None:
        clean = text.strip()
        if not clean:
            return None

        words = clean.lower().split()
        is_negative = any(word in _NEGATION_WORDS for word in words)
        content_words = [word for word in words if word not in _NEGATION_WORDS]
        basis = content_words or words
        subject = " ".join(basis[:3]) if len(basis) >= 3 else " ".join(basis)
        return Claim(subject=subject, text=clean, is_negative=is_negative)

    def _detect_missing_sections(self, sections: list[str]) -> list[str]:
        normalized = {section.strip().lower() for section in sections}
        missing: list[str] = []
        expected = ["objetivo", "hipótesis", "metodología", "conclusiones"]
        for section in expected:
            if not any(section in existing for existing in normalized):
                missing.append(section)
        return missing

    def _count_hits(self, text: str, words: set[str]) -> int:
        return sum(text.count(word) for word in words)

    def _tone_summary(self, tone: str) -> str:
        if tone == "promocional":
            return "Predomina lenguaje persuasivo/promocional."
        if tone == "critico":
            return "Predomina lenguaje de evaluación crítica y riesgos."
        return "Predomina lenguaje descriptivo/neutral."
