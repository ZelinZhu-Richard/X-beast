# ADR 002: Human In The Loop

## Context

The system drafts and reviews content, but publishing on X is high leverage and easy to get wrong. A fully autonomous loop would optimize for throughput before reliability.

## Decision

Keep a human approval gate before:

- final copy lock
- publishing
- interpretation of weekly learnings that change strategy

## Consequences

- lower throughput in the short term
- higher trust in the outputs
- easier diagnosis when quality drifts

This repo is explicitly optimized for decision quality over automation theater.
