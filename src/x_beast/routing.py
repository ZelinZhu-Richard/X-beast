from __future__ import annotations

from typing import Any

from .models import DraftPackage

TECH_KEYWORDS = {
    "agent",
    "ai",
    "api",
    "benchmark",
    "code",
    "coding",
    "eval",
    "evaluation",
    "latency",
    "model",
    "prompt",
    "reliability",
    "revision",
    "spec",
    "tool",
    "workflow",
}
BUSINESS_KEYWORDS = {
    "audience",
    "business",
    "buyer",
    "conversion",
    "cta",
    "customer",
    "evaluation",
    "founder",
    "market",
    "monetization",
    "operator",
    "pricing",
    "product",
    "revenue",
    "roi",
    "rollout",
    "team",
}


def _extract_draft_text(draft: DraftPackage | dict[str, Any]) -> str:
    """Collect the text surfaces relevant for reviewer routing."""

    if isinstance(draft, DraftPackage):
        parts = [
            draft.topic or draft.title,
            draft.selected_hook,
            draft.selected_draft_text or draft.body,
            draft.optional_cta or draft.cta or "",
        ]
        return " ".join(part for part in parts if part).lower()

    parts = [
        str(draft.get("topic", draft.get("title", ""))),
        str(draft.get("selected_hook", "")),
        str(draft.get("selected_draft_text", draft.get("body", ""))),
        str(draft.get("optional_cta", draft.get("cta", ""))),
        str(draft.get("intended_audience", draft.get("audience", ""))),
        str(draft.get("raw_opinion", draft.get("angle", ""))),
    ]
    return " ".join(part for part in parts if part).lower()


def route_review(draft: DraftPackage | dict[str, Any]) -> list[str]:
    """Route the draft to the correct reviewers in deterministic priority order."""

    text = _extract_draft_text(draft)
    routes = ["x-mentor-lead"]

    if any(keyword in text for keyword in TECH_KEYWORDS):
        routes.append("karpathy-reviewer")
    if any(keyword in text for keyword in BUSINESS_KEYWORDS):
        routes.append("business-reviewer")

    routes.append("voice-guard")
    return routes
