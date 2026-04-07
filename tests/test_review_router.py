from x_beast.routing import route_review


def test_technical_draft_routes_to_karpathy_reviewer() -> None:
    draft = {
        "title": "Latency is not the only benchmark that matters",
        "selected_hook": "I tested agent workflows on the same code task.",
        "body": "The benchmark story breaks once revision-heavy work enters the loop.",
        "cta": "Follow for more technical teardowns.",
    }

    routes = route_review(draft)

    assert "karpathy-reviewer" in routes
    assert routes[0] == "x-mentor-lead"


def test_business_angle_routes_to_business_reviewer() -> None:
    draft = {
        "title": "Why most founder content fails to convert",
        "selected_hook": "Your CTA is probably optimized for vanity, not revenue.",
        "body": "This is a positioning and pricing problem more than a reach problem.",
        "cta": "Subscribe if you want the full playbook.",
    }

    routes = route_review(draft)

    assert "business-reviewer" in routes
    assert "voice-guard" in routes
