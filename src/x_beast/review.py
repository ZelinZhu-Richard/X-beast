from __future__ import annotations

from typing import Any

from .models import DraftPackage, ReviewDecision, ReviewPlaceholder
from .routing import route_review
from .utils import make_stable_id


def build_review_placeholders(package: DraftPackage | dict[str, Any]) -> list[ReviewPlaceholder]:
    """Create pending review placeholder records for the routed reviewers."""

    if isinstance(package, DraftPackage):
        package_id = package.package_id
        brief_id = package.brief_id
        topic = package.topic or package.title
        routes = package.reviewers or route_review(package)
    else:
        package_id = str(package.get("package_id", ""))
        brief_id = str(package.get("brief_id", package.get("idea_id", "")))
        topic = str(package.get("topic", package.get("title", "")))
        routes = list(package.get("reviewers", [])) or route_review(package)

    placeholders: list[ReviewPlaceholder] = []
    for reviewer in routes:
        # TODO: Replace these human-review placeholders with model or hybrid review calls.
        placeholders.append(
            ReviewPlaceholder(
                review_id=make_stable_id("review", f"{topic}-{reviewer}", brief_id or "undated"),
                package_id=package_id,
                brief_id=brief_id,
                reviewer=reviewer,
                status="pending-human-review",
                blockers=[],
                recommended=[],
                optional=[],
                comments=[],
            )
        )
    return placeholders


def review_draft(draft: DraftPackage | dict[str, Any]) -> ReviewDecision:
    """Return a thin compatibility summary for old scripts and imports."""

    if isinstance(draft, DraftPackage):
        brief_id = draft.brief_id or draft.idea_id
        package_id = draft.package_id or draft.brief_id
    else:
        brief_id = str(draft.get("brief_id", draft.get("idea_id", "")))
        package_id = str(draft.get("package_id", brief_id))

    routes = route_review(draft)

    # TODO: Replace the stub decision with reviewer-specific model calls and aggregation.
    return ReviewDecision(
        brief_id=brief_id,
        package_id=package_id,
        routes=routes,
        decision="needs-human-review",
        issues=[],
        confidence="stub",
    )
