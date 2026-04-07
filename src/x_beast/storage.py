from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json
from pathlib import Path
from typing import Any, Iterable

from .models import DailyBrief
from .utils import (
    BriefValidationError,
    coerce_brief_values,
    ensure_parent,
    infer_brief_id,
    parse_labeled_markdown_bullets,
)


class BriefFileError(OSError):
    """Raised when a markdown brief cannot be opened or read."""


def _normalize_record(record: Any) -> dict[str, Any]:
    """Serialize a record into a JSONL-ready mapping."""

    if hasattr(record, "to_record"):
        return record.to_record()
    if is_dataclass(record):
        return asdict(record)
    if isinstance(record, dict):
        return record
    raise TypeError(f"Unsupported record type: {type(record)!r}")


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load JSONL records from disk, returning an empty list for missing files."""

    file_path = Path(path)
    if not file_path.exists():
        return []

    records: list[dict[str, Any]] = []
    with file_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def write_jsonl(path: str | Path, records: Iterable[Any]) -> Path:
    """Write a collection of records to a JSONL file."""

    file_path = ensure_parent(path)
    normalized = [_normalize_record(record) for record in records]
    with file_path.open("w", encoding="utf-8") as handle:
        for record in normalized:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return file_path


def append_jsonl(path: str | Path, record: Any) -> Path:
    """Append a single JSON record to a JSONL file."""

    file_path = ensure_parent(path)
    normalized = _normalize_record(record)
    with file_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(normalized, ensure_ascii=False) + "\n")
    return file_path


def load_daily_brief(path: str | Path) -> DailyBrief:
    """Load and validate one markdown daily brief from disk."""

    brief_path = Path(path)
    if not brief_path.exists():
        raise BriefFileError(f"Brief file does not exist: {brief_path}")
    if not brief_path.is_file():
        raise BriefFileError(f"Brief path is not a file: {brief_path}")

    try:
        raw_markdown = brief_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BriefFileError(f"Could not read brief file: {brief_path}") from exc

    parsed = parse_labeled_markdown_bullets(raw_markdown)
    values = coerce_brief_values(parsed)

    brief = DailyBrief(
        brief_id="",
        source_path=str(brief_path.resolve()),
        date=str(values["date"]),
        topic=str(values["topic"]),
        why_this_matters_now=str(values["why_this_matters_now"]),
        intended_audience=str(values["intended_audience"]),
        source_notes=[str(item) for item in values["source_notes"]],
        raw_opinion=str(values["raw_opinion"]),
        desired_format=str(values["desired_format"]),
        constraints=[str(item) for item in values["constraints"]],
        optional_cta=(str(values["optional_cta"]) if values["optional_cta"] is not None else None),
    )
    brief.brief_id = infer_brief_id(brief)
    if not brief.brief_id:
        raise BriefValidationError("Brief ID could not be inferred from the markdown brief.")
    return brief
