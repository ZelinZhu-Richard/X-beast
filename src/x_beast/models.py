from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .utils import utc_now


@dataclass(slots=True)
class Idea:
    """Legacy compatibility model for older idea-based helpers and scripts."""

    idea_id: str
    title: str
    angle: str
    audience: str = "AI builders on X"
    evidence: list[str] = field(default_factory=list)
    format_hint: str = "post"
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "Idea":
        """Build an Idea from a legacy dict-like record."""

        evidence = record.get("evidence", [])
        if isinstance(evidence, str):
            evidence = [evidence] if evidence else []
        return cls(
            idea_id=str(record.get("idea_id", record.get("brief_id", ""))),
            title=str(record.get("title", record.get("topic", ""))),
            angle=str(record.get("angle", record.get("raw_opinion", ""))),
            audience=str(record.get("audience", record.get("intended_audience", "AI builders on X"))),
            evidence=[str(item) for item in evidence],
            format_hint=str(record.get("format_hint", record.get("desired_format", "post"))),
            created_at=str(record.get("created_at", utc_now())),
        )

    def to_record(self) -> dict[str, Any]:
        """Serialize the legacy idea record."""

        return {
            "idea_id": self.idea_id,
            "title": self.title,
            "angle": self.angle,
            "audience": self.audience,
            "evidence": list(self.evidence),
            "format_hint": self.format_hint,
            "created_at": self.created_at,
        }


@dataclass(slots=True)
class DailyBrief:
    """Structured markdown brief consumed by the daily pipeline runner."""

    brief_id: str
    source_path: str
    date: str
    topic: str
    why_this_matters_now: str
    intended_audience: str
    source_notes: list[str]
    raw_opinion: str
    desired_format: str
    constraints: list[str]
    optional_cta: str | None = None
    created_at: str = field(default_factory=utc_now)

    def to_record(self) -> dict[str, Any]:
        """Serialize the brief with legacy aliases for downstream compatibility."""

        return {
            "brief_id": self.brief_id,
            "source_path": self.source_path,
            "date": self.date,
            "topic": self.topic,
            "why_this_matters_now": self.why_this_matters_now,
            "intended_audience": self.intended_audience,
            "source_notes": list(self.source_notes),
            "raw_opinion": self.raw_opinion,
            "desired_format": self.desired_format,
            "constraints": list(self.constraints),
            "optional_cta": self.optional_cta,
            "created_at": self.created_at,
            "idea_id": self.brief_id,
            "title": self.topic,
            "angle": self.raw_opinion,
            "audience": self.intended_audience,
            "evidence": list(self.source_notes),
            "format_hint": self.desired_format,
        }


@dataclass(slots=True)
class ScoreResult:
    """Editorial score output for a brief or legacy idea record."""

    brief_id: str
    topic: str
    novelty: int
    proof_source_strength: int
    audience_fit: int
    business_relevance: int
    clarity_potential: int
    discussion_potential: int
    total: int
    recommendation: str

    @property
    def idea_id(self) -> str:
        """Legacy alias used by older scripts."""

        return self.brief_id

    @property
    def title(self) -> str:
        """Legacy alias used by older scripts."""

        return self.topic

    def to_record(self) -> dict[str, Any]:
        """Serialize the score result with legacy aliases."""

        return {
            "brief_id": self.brief_id,
            "topic": self.topic,
            "novelty": self.novelty,
            "proof_source_strength": self.proof_source_strength,
            "audience_fit": self.audience_fit,
            "business_relevance": self.business_relevance,
            "clarity_potential": self.clarity_potential,
            "discussion_potential": self.discussion_potential,
            "total": self.total,
            "recommendation": self.recommendation,
            "idea_id": self.brief_id,
            "title": self.topic,
        }


@dataclass(slots=True)
class HookCandidate:
    """Structured hook candidate."""

    hook_id: str
    style: str
    text: str
    rationale: str

    def to_record(self) -> dict[str, Any]:
        """Serialize the hook candidate."""

        return {
            "hook_id": self.hook_id,
            "style": self.style,
            "text": self.text,
            "rationale": self.rationale,
        }


@dataclass(slots=True)
class DraftCandidate:
    """Structured draft candidate."""

    draft_id: str
    style: str
    text: str
    notes: str

    def to_record(self) -> dict[str, Any]:
        """Serialize the draft candidate."""

        return {
            "draft_id": self.draft_id,
            "style": self.style,
            "text": self.text,
            "notes": self.notes,
        }


@dataclass(slots=True)
class DraftPackage:
    """Draft package for the new brief-first flow with legacy field support."""

    package_id: str = ""
    brief_id: str = ""
    topic: str = ""
    score: ScoreResult | dict[str, Any] | None = None
    hooks: list[HookCandidate] = field(default_factory=list)
    drafts: list[DraftCandidate] = field(default_factory=list)
    selected_hook_id: str = ""
    selected_draft_id: str = ""
    selected_draft_text: str = ""
    reviewers: list[str] = field(default_factory=list)
    optional_cta: str | None = None
    status: str = ""
    created_at: str = field(default_factory=utc_now)
    idea_id: str = ""
    title: str = ""
    hook_options: list[str] = field(default_factory=list)
    selected_hook: str = ""
    body: str = ""
    cta: str = ""
    format_hint: str = "post"

    def __post_init__(self) -> None:
        """Backfill new or legacy fields so both interfaces remain usable."""

        if not self.brief_id and self.idea_id:
            self.brief_id = self.idea_id
        if not self.idea_id and self.brief_id:
            self.idea_id = self.brief_id

        if not self.topic and self.title:
            self.topic = self.title
        if not self.title and self.topic:
            self.title = self.topic

        if not self.hooks and self.hook_options:
            self.hooks = [
                HookCandidate(
                    hook_id=f"legacy-hook-{index}",
                    style="legacy",
                    text=text,
                    rationale="Legacy hook imported from an older draft package.",
                )
                for index, text in enumerate(self.hook_options, start=1)
            ]
        if not self.hook_options and self.hooks:
            self.hook_options = [hook.text for hook in self.hooks]

        if not self.selected_hook and self.selected_hook_id and self.hooks:
            match = next((hook for hook in self.hooks if hook.hook_id == self.selected_hook_id), None)
            if match is not None:
                self.selected_hook = match.text
        if not self.selected_hook_id and self.selected_hook:
            match = next((hook for hook in self.hooks if hook.text == self.selected_hook), None)
            if match is not None:
                self.selected_hook_id = match.hook_id

        if not self.selected_draft_text and self.body:
            self.selected_draft_text = self.body
        if not self.body and self.selected_draft_text:
            self.body = self.selected_draft_text

        if self.optional_cta in {None, ""} and self.cta:
            self.optional_cta = self.cta
        if not self.cta and self.optional_cta:
            self.cta = self.optional_cta

        if not self.status:
            self.status = "draft-package"

    def to_record(self) -> dict[str, Any]:
        """Serialize the draft package with legacy aliases."""

        score_record = self.score.to_record() if isinstance(self.score, ScoreResult) else self.score
        return {
            "package_id": self.package_id,
            "brief_id": self.brief_id,
            "topic": self.topic,
            "score": score_record,
            "hooks": [hook.to_record() for hook in self.hooks],
            "drafts": [draft.to_record() for draft in self.drafts],
            "selected_hook_id": self.selected_hook_id,
            "selected_draft_id": self.selected_draft_id,
            "selected_draft_text": self.selected_draft_text,
            "reviewers": list(self.reviewers),
            "optional_cta": self.optional_cta,
            "status": self.status,
            "created_at": self.created_at,
            "idea_id": self.idea_id,
            "title": self.title,
            "hook_options": list(self.hook_options),
            "selected_hook": self.selected_hook,
            "body": self.body,
            "cta": self.cta,
            "format_hint": self.format_hint,
        }


@dataclass(slots=True)
class ReviewPlaceholder:
    """Pending reviewer placeholder created before any model or human review exists."""

    review_id: str
    package_id: str
    brief_id: str
    reviewer: str
    status: str
    blockers: list[str]
    recommended: list[str]
    optional: list[str]
    comments: list[str]
    created_at: str = field(default_factory=utc_now)

    def to_record(self) -> dict[str, Any]:
        """Serialize the review placeholder."""

        return {
            "review_id": self.review_id,
            "package_id": self.package_id,
            "brief_id": self.brief_id,
            "reviewer": self.reviewer,
            "status": self.status,
            "blockers": list(self.blockers),
            "recommended": list(self.recommended),
            "optional": list(self.optional),
            "comments": list(self.comments),
            "created_at": self.created_at,
        }


@dataclass(slots=True)
class ReviewDecision:
    """Thin compatibility summary used by older scripts and tests."""

    brief_id: str
    package_id: str
    routes: list[str]
    decision: str
    issues: list[str]
    confidence: str
    created_at: str = field(default_factory=utc_now)

    @property
    def idea_id(self) -> str:
        """Legacy alias used by older code paths."""

        return self.brief_id

    def to_record(self) -> dict[str, Any]:
        """Serialize the review decision."""

        return {
            "brief_id": self.brief_id,
            "package_id": self.package_id,
            "routes": list(self.routes),
            "decision": self.decision,
            "issues": list(self.issues),
            "confidence": self.confidence,
            "created_at": self.created_at,
            "idea_id": self.brief_id,
        }


@dataclass(slots=True)
class PublishedPackage:
    """Packaged placeholder for a draft that is ready for human review."""

    package_id: str
    brief_id: str
    topic: str
    selected_hook_id: str
    selected_draft_id: str
    final_text: str
    review_ids: list[str]
    status: str
    ready_for_publish: bool
    created_at: str = field(default_factory=utc_now)

    def to_record(self) -> dict[str, Any]:
        """Serialize the published package placeholder."""

        return {
            "package_id": self.package_id,
            "brief_id": self.brief_id,
            "topic": self.topic,
            "selected_hook_id": self.selected_hook_id,
            "selected_draft_id": self.selected_draft_id,
            "final_text": self.final_text,
            "review_ids": list(self.review_ids),
            "status": self.status,
            "ready_for_publish": self.ready_for_publish,
            "created_at": self.created_at,
        }
