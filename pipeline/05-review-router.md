# 05 Review Router

## Goal

Route each draft through the right reviewers, classify comments correctly, and resolve conflicts using one explicit hierarchy.

## Default Review Route

Every draft goes to:

- `x-mentor-lead`
- `voice-guard`

Add reviewers only when the draft needs them:

- Add `karpathy-reviewer` when the draft makes technical claims, tool comparisons, workflow claims, benchmark references, model commentary, or reliability claims.
- Add `business-reviewer` when the draft makes a business argument, product judgment, operator recommendation, market claim, or audience-education promise.

## Comment Classes

- `BLOCKER`: must be fixed before the draft can be approved.
- `RECOMMENDED`: should be fixed unless doing so would weaken a higher-priority concern.
- `OPTIONAL`: polish only. Safe to ignore if time is tight.

## Mandatory Blockers By Reviewer

### `karpathy-reviewer`

- factual error
- unsupported quantitative claim
- misleading comparison
- false implication of causality
- missing qualifier that changes the truth of the post

### `business-reviewer`

- wrong audience
- unclear practical payoff
- strategy mismatch
- CTA and promise mismatch

### `x-mentor-lead`

- wrong angle for the brief
- wrong post shape for X
- unresolved blocker conflict between reviewers

### `voice-guard`

Only block when bloated, generic, or hypey language materially damages trust.

## Review Hierarchy

Resolve every conflict in this order:

1. truth
2. usefulness
3. voice
4. engagement polish

## Conflict Rules

- When technical accuracy conflicts with engagement, technical accuracy wins.
- When usefulness conflicts with elegance, usefulness wins.
- When brand voice conflicts with detail density, keep the detail if it is required for truth or usefulness, then tighten the phrasing around it.
- `voice-guard` may compress necessary detail but may not remove truth-preserving qualifiers.
- `x-mentor-lead` resolves conflicts only within this hierarchy and may not overrule a higher-tier blocker.

## Final Decision Rule

- A draft cannot pass with any unresolved `BLOCKER`.
- `RECOMMENDED` comments should usually be fixed, but can be declined if they weaken truth, usefulness, or required precision.
- `OPTIONAL` comments never decide the outcome.

If there is a disagreement, resolve it by asking:

1. Which version is truer?
2. Which version is more useful to the intended audience?
3. Which version keeps the voice sharp without deleting necessary meaning?
4. Which version is more engaging after the first three answers are settled?
