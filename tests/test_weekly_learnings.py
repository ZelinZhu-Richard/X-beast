from x_beast.analytics import build_weekly_learning


def test_weekly_learning_picks_best_theme_and_top_issue() -> None:
    posts = [
        {"title": "Post A", "theme": "build-in-public", "engagement_rate": 3.2},
        {"title": "Post B", "theme": "build-in-public", "engagement_rate": 2.8},
        {"title": "Post C", "theme": "hot-take", "engagement_rate": 1.1},
    ]
    reviews = [
        {"issues": ["weak hook", "weak hook"]},
        {"issues": ["cta mismatch"]},
    ]

    summary = build_weekly_learning(posts, reviews)

    assert summary["best_theme"] == "build-in-public"
    assert summary["top_review_issue"] == "weak hook"
    assert summary["average_engagement_rate"] == 2.367
