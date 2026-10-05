import pytest

from src.publication_plane.core.outbound_context_policy import (
    POLICY_ID,
    required_categories,
    validate_context_resolution,
)


EXPECTED = (
    "RELATIONSHIP_HISTORY",
    "CORRESPONDENCE_HISTORY",
    "WORKSTREAM_STATE",
    "PRIOR_COMMITMENTS",
    "PURPOSE_REQUIRED_SOURCE_ARTIFACTS",
)


def resolution(categories=EXPECTED, purpose="reply to an existing communication", policy_id=POLICY_ID):
    return {
        "purpose": purpose,
        "policy_id": policy_id,
        "required_categories": [
            {"category": category, "disposition": "VERIFIED", "evidence_refs": [f"source://{i}"]}
            for i, category in enumerate(categories)
        ],
    }


def test_reply_purpose_selects_categories_deterministically():
    assert required_categories("reply to an existing communication", POLICY_ID) == EXPECTED
    assert required_categories("reply to an existing communication", POLICY_ID) == EXPECTED
    assert validate_context_resolution(resolution()) == "ALLOW"


def test_policy_id_is_bound():
    with pytest.raises(ValueError, match="UNKNOWN_CONTEXT_POLICY"):
        required_categories("reply to an existing communication", "publisher-outbound-context-v2")


def test_unknown_purpose_fails_closed():
    with pytest.raises(ValueError, match="UNKNOWN_OUTBOUND_PURPOSE"):
        validate_context_resolution(resolution(purpose="invent a new purpose"))


def test_missing_selected_category_fails_closed():
    with pytest.raises(ValueError, match="REQUIRED_CONTEXT_CATEGORY_INCOMPLETE"):
        validate_context_resolution(resolution(categories=EXPECTED[:-1]))


def test_duplicate_selected_category_fails_closed():
    categories = EXPECTED[:-1] + (EXPECTED[0],)
    with pytest.raises(ValueError, match="REQUIRED_CONTEXT_CATEGORY_DUPLICATE"):
        validate_context_resolution(resolution(categories=categories))


def test_unselected_extra_category_fails_closed():
    with pytest.raises(ValueError, match="UNSELECTED_CONTEXT_CATEGORY_PRESENT"):
        validate_context_resolution(resolution(categories=EXPECTED + ("NOT_SELECTED",)))
