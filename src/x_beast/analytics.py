from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def build_weekly_learning(
    posts: list[dict[str, Any]],
    reviews: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    reviews = reviews or []
    count = len(posts)
    avg_engagement = 0.0 if not posts else sum(float(post.get("engagement_rate", 0.0)) for post in posts) / count

    theme_totals: dict[str, list[float]] = defaultdict(list)
    for post in posts:
        theme = str(post.get("theme", "unknown"))
        theme_totals[theme].append(float(post.get("engagement_rate", 0.0)))

    best_theme = "unknown"
    if theme_totals:
        best_theme = max(
            theme_totals.items(),
            key=lambda item: sum(item[1]) / len(item[1]),
        )[0]

    top_review_issue = "none"
    issue_counter = Counter(
        issue
        for review in reviews
        for issue in review.get("issues", [])
    )
    if issue_counter:
        top_review_issue = issue_counter.most_common(1)[0][0]

    best_post_title = ""
    if posts:
        best_post_title = max(posts, key=lambda post: float(post.get("engagement_rate", 0.0))).get("title", "")

    return {
        "post_count": count,
        "average_engagement_rate": round(avg_engagement, 3),
        "best_theme": best_theme,
        "best_post_title": best_post_title,
        "top_review_issue": top_review_issue,
        "experiments": [
            f"Double down on {best_theme} if it keeps converting.",
            "Tighten hooks that overpromise relative to the body.",
            "Review weak posts for timing and CTA mismatch.",
        ],
    }


def render_weekly_learning(summary: dict[str, Any]) -> str:
    experiments = "\n".join(f"- {item}" for item in summary.get("experiments", []))
    return (
        "# Weekly Learnings\n\n"
        f"- Posts reviewed: {summary.get('post_count', 0)}\n"
        f"- Average engagement rate: {summary.get('average_engagement_rate', 0.0)}\n"
        f"- Best theme: {summary.get('best_theme', 'unknown')}\n"
        f"- Best post: {summary.get('best_post_title', '')}\n"
        f"- Top review issue: {summary.get('top_review_issue', 'none')}\n\n"
        "## Next Experiments\n\n"
        f"{experiments}\n"
    )
