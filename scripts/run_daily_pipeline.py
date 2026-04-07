from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from x_beast.models import DraftPackage, PublishedPackage
from x_beast.review import build_review_placeholders
from x_beast.routing import route_review
from x_beast.scoring import score_idea
from x_beast.storage import BriefFileError, append_jsonl, load_daily_brief
from x_beast.utils import (
    BriefValidationError,
    build_final_text,
    format_terminal_summary,
    generate_draft_candidates,
    generate_hook_candidates,
    make_stable_id,
)


IDEAS_PATH = ROOT / "data" / "ideas" / "ideas.jsonl"
DRAFTS_PATH = ROOT / "data" / "drafts" / "drafts.jsonl"
REVIEWS_PATH = ROOT / "data" / "reviews" / "reviews.jsonl"
PUBLISHED_PATH = ROOT / "data" / "published" / "published_posts.jsonl"


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments for the daily runner."""

    parser = argparse.ArgumentParser(
        description="Run the minimal X-BEAST daily pipeline for one markdown brief.",
    )
    parser.add_argument(
        "brief_path",
        help="Path to the markdown brief file to process.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Execute the brief-first daily pipeline runner."""

    args = parse_args(sys.argv[1:] if argv is None else argv)

    try:
        brief = load_daily_brief(args.brief_path)
        score = score_idea(brief)
        hooks = generate_hook_candidates(brief)
        drafts = generate_draft_candidates(brief, hooks)

        selected_hook = next((hook for hook in hooks if hook.style == "credibility-anchor"), hooks[0])
        selected_draft = next((draft for draft in drafts if draft.style == "precise-useful"), drafts[0])
        selected_text = build_final_text(selected_hook, selected_draft, brief.optional_cta)

        # TODO: Replace this deterministic selection with model-based hook and draft ranking.
        package = DraftPackage(
            package_id=make_stable_id("package", brief.topic, brief.date),
            brief_id=brief.brief_id,
            topic=brief.topic,
            score=score,
            hooks=hooks,
            drafts=drafts,
            selected_hook_id=selected_hook.hook_id,
            selected_draft_id=selected_draft.draft_id,
            selected_draft_text=selected_text,
            reviewers=[],
            optional_cta=brief.optional_cta,
            status="ready-for-human-review",
            idea_id=brief.brief_id,
            title=brief.topic,
            hook_options=[hook.text for hook in hooks],
            selected_hook=selected_hook.text,
            body=selected_text,
            cta=brief.optional_cta or "",
            format_hint=brief.desired_format,
        )
        package.reviewers = route_review(package)

        review_placeholders = build_review_placeholders(package)
        published = PublishedPackage(
            package_id=package.package_id,
            brief_id=brief.brief_id,
            topic=brief.topic,
            selected_hook_id=selected_hook.hook_id,
            selected_draft_id=selected_draft.draft_id,
            final_text=selected_text,
            review_ids=[placeholder.review_id for placeholder in review_placeholders],
            status="ready-for-human-review",
            ready_for_publish=False,
        )

        idea_record = brief.to_record()
        idea_record["score"] = score.to_record()
        idea_record["status"] = score.recommendation

        records_to_write = {
            IDEAS_PATH: [idea_record],
            DRAFTS_PATH: [package],
            REVIEWS_PATH: review_placeholders,
            PUBLISHED_PATH: [published],
        }

        for path, records in records_to_write.items():
            for record in records:
                append_jsonl(path, record)

        summary = format_terminal_summary(
            topic=brief.topic,
            brief_id=brief.brief_id,
            score_total=score.total,
            recommendation=score.recommendation,
            selected_hook_style=selected_hook.style,
            selected_draft_style=selected_draft.style,
            reviewers=package.reviewers,
            package_status=published.status,
            written_paths=list(records_to_write.keys()),
        )
        print(summary)
        return 0
    except (BriefFileError, BriefValidationError) as exc:
        print(f"Brief error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"Pipeline failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
