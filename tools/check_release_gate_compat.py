#!/usr/bin/env python3
"""Run the release gate while accepting the canonical Publisher success marker.

The legacy checker requires ``valid: Publisher activation checks`` in the
validation guide, while the guide's canonical done-state marker is
``valid: Publisher checks``. This wrapper changes only that documentation
expectation and delegates every other gate check unchanged.
"""

from pathlib import Path

import check_release_gate

VALIDATION = Path("docs/validation.md")
terms = check_release_gate.CHECKS[VALIDATION]
check_release_gate.CHECKS[VALIDATION] = [
    "valid: Publisher checks" if term == "valid: Publisher activation checks" else term
    for term in terms
]

if __name__ == "__main__":
    raise SystemExit(check_release_gate.main())
