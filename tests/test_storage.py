from pathlib import Path

from x_beast.storage import append_jsonl, load_jsonl, write_jsonl


def test_write_and_load_jsonl_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "ideas.jsonl"
    records = [{"idea_id": "1"}, {"idea_id": "2"}]

    write_jsonl(path, records)

    assert load_jsonl(path) == records


def test_append_jsonl_adds_single_record(tmp_path: Path) -> None:
    path = tmp_path / "reviews.jsonl"

    append_jsonl(path, {"decision": "pass"})
    append_jsonl(path, {"decision": "revise"})

    assert [record["decision"] for record in load_jsonl(path)] == ["pass", "revise"]
