from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from .models import DailyBrief, DraftCandidate, HookCandidate


BRIEF_FIELD_LABELS = {
    "Date": "date",
    "Topic": "topic",
    "Why This Matters Now": "why_this_matters_now",
    "Intended Audience": "intended_audience",
    "Source Notes": "source_notes",
    "Raw Opinion": "raw_opinion",
    "Desired Format": "desired_format",
    "Constraints": "constraints",
    "Optional CTA": "optional_cta",
}

REQUIRED_BRIEF_FIELDS = {
    "date",
    "topic",
    "why_this_matters_now",
    "intended_audience",
    "source_notes",
    "raw_opinion",
    "desired_format",
    "constraints",
}


class BriefValidationError(ValueError):
    """Raised when a markdown brief cannot be parsed into the expected schema."""


def utc_now() -> str:
    """Return an ISO-8601 timestamp in UTC without microseconds."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_parent(path: str | Path) -> Path:
    """Create the parent directory for a file path and return the Path."""

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    return file_path


def clamp(value: int, low: int = 1, high: int = 5) -> int:
    """Clamp an integer to the supplied inclusive bounds."""

    return max(low, min(high, value))


def slugify(text: str) -> str:
    """Convert arbitrary text into a filesystem-friendly slug."""

    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return cleaned or "item"


def normalize_whitespace(text: str) -> str:
    """Collapse repeated whitespace while preserving intentional word boundaries."""

    return re.sub(r"\s+", " ", text).strip()


def split_note_lines(lines: Iterable[str]) -> list[str]:
    """Normalize multiline markdown bullets into a compact string list."""

    items: list[str] = []
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        if cleaned.startswith("- "):
            cleaned = cleaned[2:].strip()
        items.append(normalize_whitespace(cleaned))
    return items


def make_stable_id(prefix: str, topic: str, date: str, timestamp: str | None = None) -> str:
    """Create a readable ID using topic, date, and a timestamp suffix."""

    suffix = timestamp or datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}-{date}-{slugify(topic)}-{suffix}"


def parse_labeled_markdown_bullets(markdown: str) -> dict[str, list[str]]:
    """Parse the brief's top-level labeled bullets and their continuation lines."""

    parsed: dict[str, list[str]] = {key: [] for key in BRIEF_FIELD_LABELS.values()}
    current_key: str | None = None

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        top_level_match = re.match(r"^-\s*([^:]+):\s*(.*)$", stripped)
        if top_level_match:
            label = normalize_whitespace(top_level_match.group(1))
            value = top_level_match.group(2).strip()
            current_key = BRIEF_FIELD_LABELS.get(label)
            if current_key is None:
                current_key = None
                continue
            if value:
                parsed[current_key].append(value)
            continue

        if current_key is not None and (line.startswith("  ") or line.startswith("\t")):
            parsed[current_key].append(stripped)
            continue

        if current_key is not None and stripped.startswith("- "):
            parsed[current_key].append(stripped)

    return parsed


def coerce_brief_values(parsed: dict[str, list[str]]) -> dict[str, object]:
    """Convert parsed markdown bullet values into normalized brief fields."""

    values: dict[str, object] = {}
    missing: list[str] = []

    for field_name in BRIEF_FIELD_LABELS.values():
        raw_values = parsed.get(field_name, [])
        if field_name in {"source_notes", "constraints"}:
            normalized = split_note_lines(raw_values)
            values[field_name] = normalized
            if field_name in REQUIRED_BRIEF_FIELDS and not normalized:
                missing.append(field_name)
            continue

        normalized_text = normalize_whitespace(" ".join(raw_values))
        if field_name == "optional_cta":
            values[field_name] = normalized_text or None
            continue

        values[field_name] = normalized_text
        if field_name in REQUIRED_BRIEF_FIELDS and not normalized_text:
            missing.append(field_name)

    if missing:
        raise BriefValidationError(
            "Missing required brief field(s): " + ", ".join(sorted(missing))
        )
    return values


def infer_brief_id(brief: "DailyBrief") -> str:
    """Create a stable brief ID after fields have been validated."""

    return make_stable_id("brief", brief.topic, brief.date)


def generate_hook_candidates(brief: "DailyBrief") -> list["HookCandidate"]:
    """Generate three deterministic hook candidates from the brief."""

    from .models import HookCandidate

    proof_anchor = brief.source_notes[0] if brief.source_notes else brief.why_this_matters_now
    short_topic = normalize_whitespace(brief.topic)
    normalized_opinion = normalize_whitespace(brief.raw_opinion)

    # TODO: Replace these templates with model-generated hook exploration.
    return [
        HookCandidate(
            hook_id=make_stable_id("hook", f"{short_topic}-credibility-anchor", brief.date),
            style="credibility-anchor",
            text=f"After testing this in a real workflow, I stopped treating {short_topic.lower()} as the main signal.",
            rationale=f"Leads with firsthand evidence and keeps the claim narrow. Anchor: {proof_anchor}",
        ),
        HookCandidate(
            hook_id=make_stable_id("hook", f"{short_topic}-curiosity-gap", brief.date),
            style="curiosity-gap",
            text=f"The most misleading part of {short_topic.lower()} is that the hard part usually comes later.",
            rationale="Creates tension by implying the obvious evaluation moment is the wrong one.",
        ),
        HookCandidate(
            hook_id=make_stable_id("hook", f"{short_topic}-contrarian-business", brief.date),
            style="contrarian-business",
            text=f"{normalized_opinion} That changes how teams should evaluate tools, not just how they talk about them.",
            rationale="Connects a contrarian point of view to an operator-level business takeaway.",
        ),
    ]


def generate_draft_candidates(
    brief: "DailyBrief",
    hooks: list["HookCandidate"],
) -> list["DraftCandidate"]:
    """Generate two deterministic draft candidates from the brief."""

    from .models import DraftCandidate

    selected_hook = next((hook for hook in hooks if hook.style == "credibility-anchor"), hooks[0])
    source_anchor = brief.source_notes[0] if brief.source_notes else brief.why_this_matters_now
    constraint_anchor = brief.constraints[0] if brief.constraints else "Keep the claim bounded and defensible."
    cta_text = f"\n\n{brief.optional_cta}" if brief.optional_cta else ""

    # TODO: Replace these templates with model-generated draft variants.
    sharp_text = (
        f"{selected_hook.text}\n\n"
        f"{normalize_whitespace(brief.raw_opinion)}\n\n"
        f"The first pass is usually the easiest moment to overvalue.\n\n"
        f"{source_anchor}{cta_text}"
    )
    precise_text = (
        f"{selected_hook.text}\n\n"
        f"{normalize_whitespace(brief.why_this_matters_now)}\n\n"
        f"Use the tool on revision-heavy work, not just the first output.\n\n"
        f"{constraint_anchor}{cta_text}"
    )

    return [
        DraftCandidate(
            draft_id=make_stable_id("draft", f"{brief.topic}-sharp-opinionated", brief.date),
            style="sharp-opinionated",
            text=sharp_text,
            notes="Sharper tone, stronger opinion, higher heat.",
        ),
        DraftCandidate(
            draft_id=make_stable_id("draft", f"{brief.topic}-precise-useful", brief.date),
            style="precise-useful",
            text=precise_text,
            notes="More defensible and more aligned with the human-in-the-loop review standard.",
        ),
    ]


def build_final_text(
    selected_hook: "HookCandidate",
    selected_draft: "DraftCandidate",
    optional_cta: str | None,
) -> str:
    """Build the packaged final text from the selected hook and draft."""

    body = selected_draft.text.strip()
    if body.startswith(selected_hook.text):
        return body
    combined = f"{selected_hook.text}\n\n{body}"
    if optional_cta and optional_cta not in combined:
        return f"{combined}\n\n{optional_cta}"
    return combined


def format_terminal_summary(
    topic: str,
    brief_id: str,
    score_total: int,
    recommendation: str,
    selected_hook_style: str,
    selected_draft_style: str,
    reviewers: list[str],
    package_status: str,
    written_paths: list[Path],
) -> str:
    """Render a compact, readable end-of-run summary for the terminal."""

    path_lines = "\n".join(f"- {path}" for path in written_paths)
    reviewer_list = ", ".join(reviewers) if reviewers else "none"
    return (
        "X-BEAST Daily Pipeline Summary\n"
        f"Topic: {topic}\n"
        f"Brief ID: {brief_id}\n"
        f"Score: {score_total}/60 ({recommendation})\n"
        f"Selected hook: {selected_hook_style}\n"
        f"Selected draft: {selected_draft_style}\n"
        f"Reviewers: {reviewer_list}\n"
        f"Package status: {package_status}\n"
        "Wrote logs:\n"
        f"{path_lines}"
    )
