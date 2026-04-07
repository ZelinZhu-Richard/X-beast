# ADR 001: Repo Structure

## Context

The original repository concentrated the operating knowledge in a small set of markdown files, which made execution workable but left the repo thin on process, code scaffolding, and persistent artifacts.

## Decision

Adopt a layered structure:

- `docs/` for human operating context
- `knowledge/` for reusable strategy and source material
- `pipeline/` for stage-by-stage execution rules
- `templates/` and `examples/` for repeatable outputs
- `data/` for working artifacts
- `src/` and `scripts/` for lightweight automation
- `tests/` for the minimal safety net

## Consequences

### Positive

- easier onboarding
- cleaner separation between source research and operational use
- easier automation without hiding the process

### Tradeoffs

- more files to maintain
- stronger need for naming discipline

The tradeoff is acceptable because this repo is meant to be operated, not merely read.
