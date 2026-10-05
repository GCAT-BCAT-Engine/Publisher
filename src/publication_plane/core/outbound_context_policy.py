"""Deterministic purpose-to-context policy for governed outbound communications.

Pure policy only: this module performs no source retrieval, transport, credential,
storage, composition, send, or authority operation.
"""

POLICY_ID = "publisher-outbound-context-v1"

_PURPOSE_CATEGORIES = {
    "reply to an existing communication": (
        "RELATIONSHIP_HISTORY",
        "CORRESPONDENCE_HISTORY",
        "WORKSTREAM_STATE",
        "PRIOR_COMMITMENTS",
        "PURPOSE_REQUIRED_SOURCE_ARTIFACTS",
    ),
}


def required_categories(purpose: str, policy_id: str = POLICY_ID) -> tuple[str, ...]:
    if policy_id != POLICY_ID:
        raise ValueError("FAIL_CLOSED: UNKNOWN_CONTEXT_POLICY")
    try:
        return _PURPOSE_CATEGORIES[purpose]
    except KeyError as exc:
        raise ValueError("FAIL_CLOSED: UNKNOWN_OUTBOUND_PURPOSE") from exc


def validate_context_resolution(context_resolution: dict) -> str:
    """Validate policy binding and exact-once required-category coverage."""
    policy_id = context_resolution.get("policy_id")
    purpose = context_resolution.get("purpose")
    expected = required_categories(purpose, policy_id)

    entries = context_resolution.get("required_categories")
    if not isinstance(entries, list):
        raise ValueError("FAIL_CLOSED: REQUIRED_CONTEXT_CATEGORIES_MISSING")

    observed = [entry.get("category") for entry in entries if isinstance(entry, dict)]
    if len(observed) != len(entries):
        raise ValueError("FAIL_CLOSED: REQUIRED_CONTEXT_CATEGORY_MALFORMED")
    if len(observed) != len(set(observed)):
        raise ValueError("FAIL_CLOSED: REQUIRED_CONTEXT_CATEGORY_DUPLICATE")

    expected_set = set(expected)
    observed_set = set(observed)
    if expected_set - observed_set:
        raise ValueError("FAIL_CLOSED: REQUIRED_CONTEXT_CATEGORY_INCOMPLETE")
    if observed_set - expected_set:
        raise ValueError("FAIL_CLOSED: UNSELECTED_CONTEXT_CATEGORY_PRESENT")
    return "ALLOW"
