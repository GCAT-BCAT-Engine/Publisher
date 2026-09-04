# Canonical Resident Carrier Awareness Mirror Handoff

Repository: `GCAT-BCAT-Engine/Publisher`  
Parent authority: `PUBLISHER_MIRROR_HANDOFF.md`  
Upstream source: `StegVerse-Labs/.github@b1f2bb3e33a1f93850811f0a751b2055519ab4dd`  
Upstream contract: `control/canonical-resident-carrier-contract.json`  
Authority effect: `NONE_AWARENESS_ONLY`

## Canonical architecture

Publisher recognizes StegVerse-001, StegVerse-002, and SV-011 as consumers of one shared resident substrate:

```text
HB32 independent oscillator reference
-> HB-derived exact-byte InTr carrier (non-authorizing)
-> one StegVerse-Labs/.github WorkerCoordinator
-> canonical resident request dispatcher
-> task-specific fail-closed consumer and evidence
```

Publisher must not describe any of those entities as owning a second heartbeat, scheduler, WorkerCoordinator, credential lane, claim/fence path, or independent resident runtime unless a later canonical source explicitly supersedes the upstream contract.

## Runtime-state publication boundary

Architecture/source awareness is current. Runtime activation remains task-specific:
- SV001 terminal execution must not be rerun merely for carrier proof;
- SV002 activation requires its authentic `terminal_round_trip_observed=true` evidence;
- SV-011 Phase 5 requires the authentic same-execution ALLOW/DENY evidence chain.

Publisher may publish runtime-status advancement only from authentic canonical evidence. GitHub merge/CI is not runtime proof.

Credential authority remains `TV/TVC`. GitHub token runtime authority remains `NONE`.
