from __future__ import annotations

from .models import DraftPackage, Idea


def generate_hook_options(record: Idea | dict[str, object]) -> list[str]:
    idea = record if isinstance(record, Idea) else Idea.from_record(record)
    evidence_anchor = idea.evidence[0] if idea.evidence else idea.angle

    hooks = [
        f"I built a system around one annoying X problem: {idea.title.lower()}. {evidence_anchor}",
        f"Most posts about {idea.title.lower()} miss the hard part. Here is the part that actually changes results.",
        f"I tested {idea.title.lower()} in a real workflow. The surprising part was not the tool. It was the review loop.",
    ]
    return hooks


def build_draft_package(record: Idea | dict[str, object]) -> DraftPackage:
    idea = record if isinstance(record, Idea) else Idea.from_record(record)
    hook_options = generate_hook_options(idea)
    selected_hook = hook_options[0]

    evidence_lines = idea.evidence[:3] or [idea.angle]
    bullets = "\n".join(f"- {line}" for line in evidence_lines)
    body = (
        f"{idea.angle}\n\n"
        f"What makes this worth reading:\n{bullets}\n\n"
        "If you care about repeatable content systems, the bottleneck is usually not ideation. "
        "It is the quality gate between a decent idea and a publishable post."
    )
    cta = "Follow for more X operating notes, review patterns, and AI-builder playbooks."

    return DraftPackage(
        idea_id=idea.idea_id,
        title=idea.title,
        hook_options=hook_options,
        selected_hook=selected_hook,
        body=body,
        cta=cta,
        format_hint=idea.format_hint,
    )
