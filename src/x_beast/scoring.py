from __future__ import annotations

from typing import Any

from .models import DailyBrief, Idea, ScoreResult
from .utils import clamp, normalize_whitespace

NOVELTY_HINTS = {
    "contrarian",
    "different",
    "gap",
    "instead",
    "moat",
    "not",
    "overrated",
    "underestimated",
    "wrong",
}
PROOF_HINTS = {"i ", "we ", "tested", "built", "used", "observed", "notes", "workflow"}
BUSINESS_HINTS = {
    "audience",
    "business",
    "buyer",
    "customer",
    "evaluation",
    "founder",
    "market",
    "operator",
    "pricing",
    "product",
    "revenue",
    "roi",
    "rollout",
    "team",
}
DISCUSSION_HINTS = {
    "disagree",
    "debate",
    "discussion",
    "hot take",
    "why",
    "wrong",
    "should",
    "tradeoff",
}


def _extract_brief_like_record(record: DailyBrief | Idea | dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """Normalize new or legacy inputs into one scoring view."""

    if isinstance(record, DailyBrief):
        return (
            {
                "brief_id": record.brief_id,
                "topic": record.topic,
                "why_this_matters_now": record.why_this_matters_now,
                "intended_audience": record.intended_audience,
                "source_notes": list(record.source_notes),
                "raw_opinion": record.raw_opinion,
                "desired_format": record.desired_format,
                "constraints": list(record.constraints),
            },
            False,
        )

    legacy = record if isinstance(record, Idea) else Idea.from_record(record)
    return (
        {
            "brief_id": legacy.idea_id,
            "topic": legacy.title,
            "why_this_matters_now": legacy.angle,
            "intended_audience": legacy.audience,
            "source_notes": list(legacy.evidence),
            "raw_opinion": legacy.angle,
            "desired_format": legacy.format_hint,
            "constraints": [],
        },
        True,
    )


def _text_blob(data: dict[str, Any]) -> str:
    """Combine relevant fields into one lowercase blob for heuristic scoring."""

    joined = " ".join(
        [
            str(data.get("topic", "")),
            str(data.get("why_this_matters_now", "")),
            str(data.get("intended_audience", "")),
            str(data.get("raw_opinion", "")),
            str(data.get("desired_format", "")),
            " ".join(str(item) for item in data.get("source_notes", [])),
            " ".join(str(item) for item in data.get("constraints", [])),
        ]
    )
    return normalize_whitespace(joined).lower()


def _contains_digit(text: str) -> bool:
    """Return True when the text contains at least one numeric character."""

    return any(character.isdigit() for character in text)


def _novelty_score(data: dict[str, Any], blob: str) -> int:
    """Score how distinct and non-generic the idea appears."""

    score = 4
    if any(keyword in blob for keyword in NOVELTY_HINTS):
        score += 2
    if len(set(blob.split())) >= 14:
        score += 2
    if _contains_digit(blob):
        score += 1
    if "future of ai" in blob or blob.startswith("thoughts on"):
        score -= 2
    return clamp(score, low=1, high=10)


def _proof_score(data: dict[str, Any], blob: str) -> int:
    """Score how grounded the brief is in observed or sourced material."""

    notes = data.get("source_notes", [])
    score = 3
    if notes:
        score += 2
    if len(notes) >= 2:
        score += 2
    if any(keyword in blob for keyword in PROOF_HINTS):
        score += 2
    if _contains_digit(blob):
        score += 1
    return clamp(score, low=1, high=10)


def _audience_fit_score(data: dict[str, Any], blob: str) -> int:
    """Score how clearly the idea maps to a target reader and platform context."""

    audience = str(data.get("intended_audience", "")).lower()
    score = 3
    if audience and audience != "general audience":
        score += 2
    if any(keyword in audience for keyword in {"ai", "builder", "founder", "operator", "x", "twitter"}):
        score += 3
    if any(keyword in blob for keyword in {"x", "twitter", "post", "thread"}):
        score += 1
    return clamp(score, low=1, high=10)


def _business_relevance_score(data: dict[str, Any], blob: str) -> int:
    """Score how much the idea informs a business or operator decision."""

    score = 3
    if any(keyword in blob for keyword in BUSINESS_HINTS):
        score += 4
    if any(keyword in blob for keyword in {"practical", "decision", "evaluate", "workflow"}):
        score += 2
    if "general reflections" in blob:
        score -= 2
    return clamp(score, low=1, high=10)


def _clarity_potential_score(data: dict[str, Any], blob: str) -> int:
    """Score how likely the idea is to be expressed cleanly in one post."""

    topic_words = len(str(data.get("topic", "")).split())
    score = 5
    if topic_words >= 5:
        score += 1
    if topic_words >= 10:
        score += 1
    if len(str(data.get("raw_opinion", "")).split()) <= 25:
        score += 1
    if str(data.get("desired_format", "")).lower() == "single post":
        score += 1
    if "deep dive" in blob:
        score -= 2
    return clamp(score, low=1, high=10)


def _discussion_potential_score(blob: str) -> int:
    """Score how likely the idea is to trigger useful discussion on X."""

    score = 4
    if any(keyword in blob for keyword in DISCUSSION_HINTS):
        score += 2
    if any(keyword in blob for keyword in {"not", "better", "worse", "overrated", "should"}):
        score += 2
    if _contains_digit(blob):
        score += 1
    return clamp(score, low=1, high=10)


def _recommendation(total: int, legacy: bool) -> str:
    """Map total score to a recommendation label."""

    if legacy:
        if total >= 50:
            return "run-now"
        if total >= 40:
            return "strong-backlog"
        if total >= 30:
            return "revise"
        return "archive"

    if total >= 50:
        return "draft-today"
    if total >= 40:
        return "strong-backlog"
    if total >= 30:
        return "revise-angle"
    return "do-not-draft"


def score_idea(record: DailyBrief | Idea | dict[str, Any]) -> ScoreResult:
    """Score a markdown brief or a legacy idea record using deterministic heuristics.

    This function is intentionally a stub. It keeps the interface clean now and leaves
    obvious TODO seams for model-based scoring later.
    """

    # TODO: Replace rule-based scoring with a model evaluator that reads the brief,
    # rubric, and source notes directly.
    data, legacy = _extract_brief_like_record(record)
    blob = _text_blob(data)

    novelty = _novelty_score(data, blob)
    proof_source_strength = _proof_score(data, blob)
    audience_fit = _audience_fit_score(data, blob)
    business_relevance = _business_relevance_score(data, blob)
    clarity_potential = _clarity_potential_score(data, blob)
    discussion_potential = _discussion_potential_score(blob)
    total = (
        novelty
        + proof_source_strength
        + audience_fit
        + business_relevance
        + clarity_potential
        + discussion_potential
    )

    return ScoreResult(
        brief_id=str(data.get("brief_id", "")),
        topic=str(data.get("topic", "")),
        novelty=novelty,
        proof_source_strength=proof_source_strength,
        audience_fit=audience_fit,
        business_relevance=business_relevance,
        clarity_potential=clarity_potential,
        discussion_potential=discussion_potential,
        total=total,
        recommendation=_recommendation(total, legacy=legacy),
    )
