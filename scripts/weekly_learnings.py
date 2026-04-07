from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from x_beast.analytics import build_weekly_learning, render_weekly_learning
from x_beast.storage import load_jsonl


def main() -> int:
    posts = load_jsonl(ROOT / "data" / "analytics" / "performance_log.jsonl")
    reviews = load_jsonl(ROOT / "data" / "reviews" / "reviews.jsonl")
    summary = build_weekly_learning(posts, reviews)
    print(render_weekly_learning(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
