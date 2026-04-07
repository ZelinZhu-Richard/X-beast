# Agent Roles

## Role Map

| Role | Responsibility | Primary Inputs | Exit Criteria |
|------|----------------|----------------|---------------|
| `x-mentor-lead` | Owns orchestration and final recommendation | idea context, pipeline stage, latest reviews | clear next action and final recommendation |
| `karpathy-reviewer` | Checks technical accuracy and substance | technical claims, demos, benchmarks, model/tool references | claims are precise and defensible |
| `business-reviewer` | Checks audience value, positioning, and monetization relevance | audience, promise, CTA, business goal | draft has a concrete payoff and strategic fit |
| `voice-guard` | Checks tone, clarity, and brand consistency | final draft and hook set | output sounds like the brand and not generic AI copy |

## Routing Guidance

### Default

Every draft should pass through:

- `x-mentor-lead`
- `voice-guard`

### Add `karpathy-reviewer` when

- the post mentions model performance
- a technical tutorial is involved
- benchmark numbers or implementation claims are present

### Add `business-reviewer` when

- the post sells a product, service, or lead magnet
- the post is about positioning, growth, or monetization
- the CTA asks for conversion, not just engagement

## Review Contract

Each role should return:

1. pass / revise
2. top 3 issues
3. exact recommended changes
4. confidence level

The lead reviewer resolves disagreements. If two reviewers disagree on direction, the lead reviewer should preserve accuracy first, then business clarity, then stylistic polish.
