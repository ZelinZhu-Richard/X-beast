from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from x_beast.drafting import generate_hook_options
from x_beast.storage import load_jsonl


def main() -> int:
    ideas = load_jsonl(ROOT / "data" / "ideas" / "ideas.jsonl")
    if not ideas:
        print("No ideas available for hook generation.")
        return 0

    hooks = generate_hook_options(ideas[0])
    for index, hook in enumerate(hooks, start=1):
        print(f"{index}. {hook}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
