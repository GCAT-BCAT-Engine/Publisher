# Publisher Closure Evidence Production

## Purpose

This packet defines the current Publisher-side activation goal after the Site repository reached repository-managed continuation completion.

Publisher is now responsible for producing or observing the fresh ordered evidence pair that can close Publisher-to-Site mirror activation.

## Current Goal

```text
Goal: Publisher closure evidence production
Repository: GCAT-BCAT-Engine/Publisher
Target repository: StegVerse-Labs/Site
Source path: papers
Target path: papers
Publisher state: ready_for_fresh_ordered_automated_closure
Site state: repository_managed_continuation_complete
Activation state: pending_fresh_ordered_artifacts
```

## Pending Status Surface

```text
docs/PUBLISHER_PENDING_CLOSURE_STATUS.md
```

The pending status surface records the current missing-evidence boundary without claiming activation:

```text
status: waiting_for_fresh_ordered_artifact_pair
publisher_receipt_recorded_here: false
site_evidence_recorded_here: false
closure_recorded_here: false
pending_probe_only: true
```

## Evidence Pair Required For Closure

Publisher activation remains blocked until both artifact classes exist, are fresh, and are ordered within the configured grace window:

```text
publisher_artifact_prefix: publisher-site-verification-receipt
site_artifact_prefix: site-mirror-evidence
MAX_ARTIFACT_AGE_HOURS: 48
ORDER_GRACE_MINUTES: 5
closure_script: tools/close_site_mirror_activation.py
closure_workflow: github/workflows/close-site-mirror-activation.yml
```

## Non-Activation Rule

This packet does not claim activation.

The pending probe remains a pending-evidence record only:

```text
docs/mirror-activation-closures/publisher-site-mirror-pending.json
non_claim: This pending probe is not an activation receipt.
```

Activation may only be claimed after `tools/close_site_mirror_activation.py` writes a closure receipt matching:

```text
docs/mirror-activation-closures/publisher-site-mirror-closure-<timestamp>.json
schema: stegverse.publisher.site_mirror.closure.v1
activation_state: activated
```

## Publisher Closure Responsibilities

```text
1. Run Publisher activation validation before dispatch completion.
2. Produce a live Publisher verification receipt artifact only after a successful dispatch path.
3. Wait for or nudge the Site mirror workflow to produce the Site evidence artifact.
4. Run the closure workflow on dispatch completion, schedule, push, or workflow dispatch.
5. Reject missing, stale, out-of-order, or evidence-incomplete artifact pairs.
6. Write a pending probe when evidence is missing or not closure-ready.
7. Keep docs/PUBLISHER_PENDING_CLOSURE_STATUS.md as a pending boundary while evidence is missing.
8. Write a closure receipt only when evidence is fresh, ordered, and valid.
9. Update verification tracker and activation status only from the closure receipt path.
```

## Site Completion Dependency

The Site side is treated as repository-managed continuation complete for the purpose of Publisher's next build goal.

The relevant Site handoffs are:

```text
StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md
StegVerse-Labs/Site/docs/SITE_MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md
StegVerse-Labs/Site/docs/SITE_SELF_MANAGED_COMPLETION.md
StegVerse-Labs/Site/docs/TRANSITION_DISCOVERY_STATUS.md
StegVerse-Labs/Site/data/transition-discovery-status-v1.json
```

Publisher must still require live Site evidence artifact production. Site repository-managed continuation completion is not the same as mirror activation.

## Done Definition

Publisher closure evidence production is done when one of these outcomes is recorded:

```text
A. Activated closure:
   - Fresh Publisher verification receipt artifact exists.
   - Fresh Site evidence artifact exists.
   - Artifacts are ordered within ORDER_GRACE_MINUTES.
   - Closure receipt exists.
   - Verification tracker is activated.
   - Activation status is activated.

B. Self-managed pending closure:
   - This packet exists.
   - docs/PUBLISHER_PENDING_CLOSURE_STATUS.md exists.
   - The close activation workflow checks this packet.
   - The close activation workflow watches this packet.
   - The management handoff names this packet.
   - The pending probe records the current missing-evidence boundary.
```

## Archive Readiness

This packet is sufficient for a future Publisher-side session or ecosystem-management process to continue closure evidence production without prior chat context.
