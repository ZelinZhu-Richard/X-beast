# System Overview

## Purpose

X-BEAST is a knowledge-first content operating system for X/Twitter. It is designed to turn raw ideas, market signals, and account feedback into:

- scored ideas
- draft hooks and posts
- routed reviews
- weekly learnings that improve the next cycle

The repository is intentionally split into human-readable knowledge assets and a small Python execution layer. The knowledge is the product; the code exists to keep the workflow repeatable.

## Core Layers

### 1. Knowledge Layer

`knowledge/x-mentor-core/` stores the distilled strategy, heuristics, and source research.

- `research/` is the source-of-truth archive
- the root markdown files are the operational references loaded during execution

`knowledge/personas/` defines reviewer roles.

`knowledge/rubrics/` defines scoring and review standards.

## 2. Pipeline Layer

`pipeline/` breaks the operating loop into explicit stages:

1. intake
2. score
3. hook generation
4. drafting
5. review routing
6. final polish
7. publish check
8. postmortem

Each stage should produce a concrete artifact that can be audited later.

## 3. Execution Layer

`src/x_beast/` contains lightweight utilities for storage, scoring, drafting, routing, review, and analytics.

`scripts/` wraps those modules into commands that operate on files in `data/`.

This layer is intentionally simple:

- standard library only
- JSONL as the default storage format
- markdown templates for human output

## 4. Data Layer

`data/` stores the working state of the system.

- `ideas/` captures raw and scored ideas
- `drafts/` stores in-progress content packages
- `reviews/` stores reviewer decisions
- `published/` stores accepted output metadata
- `analytics/` stores outcome logs

## Operating Principles

### Human in the Loop

X-BEAST is an assistive system, not an autonomous publisher. Humans approve:

- what gets drafted
- what gets published
- what counts as a lesson learned

### Knowledge Before Automation

When behavior looks wrong, fix the rubric, template, or persona instructions before adding code complexity.

### Evidence Over Vibes

Ideas, hooks, and reviews should cite:

- concrete observations
- credible experience
- measurable outcomes

## Recommended Flow

1. Capture ideas in `data/ideas/ideas.jsonl`.
2. Score and prioritize them.
3. Generate 3 hook directions.
4. Produce one draft package.
5. Route it through the relevant reviewers.
6. Approve manually.
7. Log published results.
8. Run a weekly learnings pass.
