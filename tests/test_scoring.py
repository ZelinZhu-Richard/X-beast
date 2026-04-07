from x_beast.scoring import score_idea


def test_specific_idea_scores_higher_than_generic_idea() -> None:
    specific = {
        "idea_id": "idea-1",
        "title": "I tested 7 AI review loops on the same workflow in 48 hours",
        "angle": "A concrete breakdown of where the speed gain came from.",
        "audience": "AI builders on X",
        "evidence": ["same workflow", "48 hours", "7 tools"],
        "format_hint": "post",
    }
    generic = {
        "idea_id": "idea-2",
        "title": "Thoughts on AI",
        "angle": "General reflections on the future.",
        "audience": "general audience",
        "evidence": [],
        "format_hint": "thread",
    }

    assert score_idea(specific).total > score_idea(generic).total


def test_high_scoring_idea_gets_run_now_or_backlog_recommendation() -> None:
    result = score_idea(
        {
            "idea_id": "idea-3",
            "title": "We shipped a review router for X posts and cut bad benchmark claims by 80%",
            "angle": "A practical breakdown of the workflow.",
            "audience": "AI founders on X",
            "evidence": ["80%", "real workflow"],
            "format_hint": "post",
        }
    )

    assert result.recommendation in {"run-now", "strong-backlog"}
