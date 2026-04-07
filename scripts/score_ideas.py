from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from x_beast.scoring import score_idea
from x_beast.storage import load_jsonl


def main() -> int:
    ideas = load_jsonl(ROOT / "data" / "ideas" / "ideas.jsonl")
    if not ideas:
        print("No ideas to score.")
        return 0

    scored = sorted((score_idea(idea) for idea in ideas), key=lambda item: item.total, reverse=True)
    for result in scored:
        print(f"{result.idea_id}\t{result.total}\t{result.recommendation}\t{result.title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
