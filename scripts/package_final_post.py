from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from x_beast.storage import append_jsonl, load_jsonl
from x_beast.utils import utc_now


PUBLISHED_PATH = ROOT / "data" / "published" / "published_posts.jsonl"


def main() -> int:
    drafts = load_jsonl(ROOT / "data" / "drafts" / "drafts.jsonl")
    reviews = load_jsonl(ROOT / "data" / "reviews" / "reviews.jsonl")
    if not drafts:
        print("No drafts available to package.")
        return 0

    latest_draft = drafts[-1]
    latest_review = reviews[-1] if reviews else {}
    if latest_review.get("decision") == "revise":
        print("Latest draft still requires revision.")
        return 1

    record = {
        "idea_id": latest_draft.get("idea_id", ""),
        "title": latest_draft.get("title", ""),
        "final_post": "\n\n".join(
            [
                str(latest_draft.get("selected_hook", "")).strip(),
                str(latest_draft.get("body", "")).strip(),
                str(latest_draft.get("cta", "")).strip(),
            ]
        ).strip(),
        "packaged_at": utc_now(),
        "review_decision": latest_review.get("decision", "unreviewed"),
    }
    append_jsonl(PUBLISHED_PATH, record)
    print(f"Packaged post for idea {record['idea_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
