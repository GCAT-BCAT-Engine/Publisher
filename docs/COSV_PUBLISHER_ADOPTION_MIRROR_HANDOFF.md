# Publisher COSV Adoption Mirror Handoff

Updated: 2026-08-31
Repository: GCAT-BCAT-Engine/Publisher
Repository authority: docs/PUBLISHER_MIRROR_HANDOFF.md
Canonical profile: StegVerse-Labs/.github/management/COSV_PROFILE_V1.json
Authority effect: NONE

## Current machine projections

The Publisher orchestration state declares two dependency-blocked machine tasks that are safe to project read-only:

```text
PUBLISHER-0001-HIL-PROPAGATION 60000000104000
PUBLISHER-0001-CLOSURE         60000000101000
```

The HIL/Site-propagation task's blocker count is derived from the four explicit blocked_by entries in data/publisher-orchestration-state.json. The closure task has one aggregate release condition: fresh ordered Publisher receipt plus Site evidence plus validated closure receipt.

These vectors do not modify the scheduled Site observer, closure workflows, publication state, release state, custody, admissibility, or Guardian authority.

Installed:

```text
data/cosv/task-vector-index.json
data/cosv/task-vectors/PUBLISHER-0001-HIL-PROPAGATION.json
data/cosv/task-vectors/PUBLISHER-0001-CLOSURE.json
scripts/check_cosv_task_projection.py
tests/test_cosv_task_projection.py
```

## Adoption boundary

```text
machine-blocked propagation tasks projected: 2
machine-blocked propagation gap: 0
GCAT capacity draft task projected: false (separate active owner)
repository-wide active task audit complete: false
repository VECTOR_PRESENT claimed: false
```

Next machine work is to preserve the scheduled importer/closure owners, observe genuine Site readiness and closure evidence, then update COSV from repository-native state transitions. The unrelated GCAT capacity draft remains owned by its existing claim and is not modified by this lane.
