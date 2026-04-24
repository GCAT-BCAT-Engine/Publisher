# Publisher Integration Specification

## Document Info
| | |
|---|---|
| **Version** | 1.0.0 |
| **Date** | 2026-04-22 |
| **Author** | AaCT-E Contributors |
| **Status** | Draft |

---

## 1. Purpose

This specification defines how the **AaCT-E/demo** repository integrates with **GCAT-BCAT-Engine/Publisher** to support:

- **Paper submission tracking** — which papers reference which demo artifacts
- **Social media presence** — automated posting of verification milestones
- **Release coordination** — synchronized tagging between theory and demo
- **Trace archival** — long-term storage of evidence traces for reproducibility

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PUBLISHER INTEGRATION PIPELINE                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│  │   AaCT-E     │    │   Publisher  │    │   Social     │         │
│  │   /demo      │───▶│   /Publisher │───▶│   Media      │         │
│  │              │    │              │    │   (X, LinkedIn│         │
│  │  CI emits    │    │  Ingests     │    │   , Blog)    │         │
│  │  status.json │    │  status.json │    │              │         │
│  └──────────────┘    └──────────────┘    └──────────────┘         │
│         │                   │                                        │
│         │                   ▼                                        │
│         │            ┌──────────────┐                               │
│         │            │   StegDB     │                               │
│         │            │   Monitor    │                               │
│         │            └──────────────┘                               │
│         │                                                            │
│         ▼                                                            │
│  ┌──────────────┐                                                   │
│  │   GitHub     │                                                   │
│  │   Releases   │                                                   │
│  │   + Tags     │                                                   │
│  └──────────────┘                                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Integration Points

### 3.1 CI → Publisher (Status Ingestion)

**Trigger:** Every successful CI run on `AaCT-E/demo`

**Mechanism:**
1. CI workflow (`verify.yml`) runs `stegdb_hooks/emit_status.py`
2. Produces `stegdb_hooks/last_status.json`
3. Publisher repo polls or receives webhook with this artifact

**Status Schema (v1.0.0):**
```json
{
  "schema_version": "1.0.0",
  "repo": "AaCT-E/demo",
  "run_id": "github-actions-run-id",
  "commit_sha": "abc123...",
  "status": "success",
  "timestamp_utc": "2026-04-22T20:00:00Z",
  "traces": [
    {
      "scenario": "unsafe_merge",
      "decision": "DENY",
      "proposal_min_separation_nm": 1.198,
      "recovery_reachable": true,
      "file": "unsafe_merge_trace.json",
      "sha256_prefix": "0c9f3d84..."
    }
  ],
  "ecosystem": {
    "org": "AaCT-E",
    "upstream": "GCAT-BCAT-Engine",
    "sibling_repos": [
      "GCAT-BCAT-Engine/Publisher",
      "StegVerse-Labs/StegDB",
      "StegVerse-Labs/SDK"
    ]
  }
}
```

### 3.2 Publisher → Social Media (Milestone Posts)

**Trigger:** Significant events

| Event | Post Content | Platform |
|-------|-------------|----------|
| First `Verification PASSED` | "AaCT-E demo achieves zero-dependency verification" | X, LinkedIn |
| Tag `v0.1.0` | "Phase I evidence artifact released — commit-time safety enforcement" | Blog, X |
| Paper submission | "GCAT/BCAT formalism now backed by executable demo" | LinkedIn, Blog |
| Daily CI (100th run) | "100 consecutive verification passes — deterministic safety evidence" | X |

**Format:**
```
🛡️ AaCT-E Update

Scenario: unsafe_merge
Decision: DENY (unsafe action blocked)
Recovery: TURN_LEFT_30 reachable at 4.11 nm

→ Zero dependencies. One command. Verifiable safety.

#AviationSafety #AI #GCAT #BCAT #SBIR
```

### 3.3 Release Coordination

**Synchronized Tagging:**

| Event | AaCT-E/demo Action | Publisher Action |
|-------|-------------------|------------------|
| Paper v1.0 accepted | Tag `v0.1.0-paper1` | Tag `v1.0.0` |
| Demo expanded to 3D | Tag `v0.2.0` | Update paper to v1.1 |
| SBIR Phase I award | Tag `v0.1.0-sbir` | Publish press release |

**Changelog Format:**
```markdown
## [0.1.0] - 2026-04-22
### Added
- Initial commit-time safety enforcement demo
- Two scenarios: unsafe_merge (DENY), safe_hold (ALLOW)
- StegDB monitoring hooks
- Publisher integration spec

### Linked Papers
- GCAT/BCAT Foundation (Publisher v1.0.0)
```

### 3.4 Trace Archival

**Long-term Storage:**
- CI artifacts retained for 90 days (GitHub default)
- Publisher repo archives "milestone traces" in `archives/traces/`
- Each archived trace includes:
  - Original JSON trace
  - Commit SHA
  - CI run ID
  - Paper version it supported

**Directory Structure in Publisher:**
```
Publisher/
  archives/
    traces/
      2026-04-22_aacte-v0.1.0/
        unsafe_merge_trace.json
        safe_hold_trace.json
        manifest.json  # links to commit, paper version, demo version
```

---

## 4. Implementation Checklist

### Publisher Repo Changes

- [ ] Add `ingest_aacte_status.py` — parses `last_status.json`, updates dashboard
- [ ] Add `social_media_scheduler.py` — queues posts based on milestone rules
- [ ] Add `archive_traces.py` — copies milestone traces to `archives/traces/`
- [ ] Add `.github/workflows/publisher-sync.yml` — pulls from AaCT-E CI artifacts
- [ ] Update `README.md` with ecosystem diagram including AaCT-E

### AaCT-E/demo Changes

- [ ] Ensure `emit_status.py` schema matches Publisher expectations
- [ ] Add `publisher.webhook_url` to `aacte.architecture.json` (when available)
- [ ] Tag `v0.1.0` on first stable release
- [ ] Verify CI artifact upload includes `last_status.json`

### Cross-Repo Coordination

- [ ] Define webhook endpoint or polling interval
- [ ] Agree on tag naming convention
- [ ] Set up shared secret for webhook authentication
- [ ] Document social media account credentials (secure storage)

---

## 5. Social Media Strategy

### Platforms & Cadence

| Platform | Frequency | Content Type |
|----------|-----------|--------------|
| X (Twitter) | 2-3x/week | Milestones, quick stats, thread summaries |
| LinkedIn | 1x/week | Longer-form updates, paper announcements |
| Blog (GitHub Pages) | 1x/month | Deep dives, methodology explanations |

### Content Templates

**Verification Milestone:**
```
✅ AaCT-E Demo Verification #{run_number}

{scenario_count} scenarios | {decision_summary}
All assertions passed. Zero dependencies.

Full trace: {artifact_link}
```

**Paper Linkage:**
```
📄 New Paper: "{paper_title}"

Backed by executable evidence:
→ git clone https://github.com/AaCT-E/demo
→ python verify_demo.py

Theory + Code = Reproducible Safety
```

**SBIR Update:**
```
🚀 SBIR Phase I Update

AaCT-E demo now supports:
- {feature_list}

Next: {roadmap_item}

#SBIR #Aviation #AI #Safety
```

---

## 6. Monitoring & Alerts

### StegDB Integration

- **Health Check:** Daily CI run → StegDB ingest → Dashboard update
- **Failure Alert:** If `verify_demo.py` fails, notify:
  - Publisher maintainers
  - Social media scheduler (pause auto-posts)
  - StegDB anomaly detector

### Publisher Dashboard Metrics

| Metric | Source | Update Frequency |
|--------|--------|------------------|
| Consecutive passes | CI history | Real-time |
| Trace count | Artifact storage | Daily |
| Paper citations | Citation index | Weekly |
| Social engagement | Platform APIs | Weekly |

---

## 7. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-22 | Initial spec — CI→Publisher→Social pipeline |

---

## 8. References

- [AaCT-E/demo README](https://github.com/AaCT-E/demo/blob/main/README.md)
- [AaCT-E Architecture Manifest](https://github.com/AaCT-E/demo/blob/main/aacte.architecture.json)
- [StegDB Hooks](https://github.com/AaCT-E/demo/blob/main/stegdb_hooks/README.md)
- [GCAT-BCAT-Engine/Publisher](https://github.com/GCAT-BCAT-Engine/Publisher)
