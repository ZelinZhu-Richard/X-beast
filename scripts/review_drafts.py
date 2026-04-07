from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from x_beast.review import review_draft
from x_beast.storage import append_jsonl, load_jsonl


REVIEWS_PATH = ROOT / "data" / "reviews" / "reviews.jsonl"


def main() -> int:
    drafts = load_jsonl(ROOT / "data" / "drafts" / "drafts.jsonl")
    if not drafts:
        print("No drafts available for review.")
        return 0

    review = review_draft(drafts[-1])
    append_jsonl(REVIEWS_PATH, review)
    print(f"Review decision: {review.decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
