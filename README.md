# StegVerse Publisher

**Cross-org publication orchestration for the StegVerse ecosystem.**

## What It Provides

| Module | Purpose |
|--------|---------|
| `core.receipt_writer` | Deterministic publication receipts |
| `core.publication_gate` | ALLOW/DENY → publish/quarantine/block |
| `core.result_snapshot` | Immutable result capture |
| `routing.release_router` | Research/demo/press routing |
| `routing.channel_manager` | Cross-org target resolution |
| `routing.notary` | Pre-transition notarization |
| `surfaces.demo_sync` | Demo artifact publishing |
| `surfaces.badge_generator` | Reproducibility badges |
| `surfaces.evidence_builder` | Claim-to-figure linking |
| `external.dataset_exporter` | Open data catalog |
| `external.review_packet` | Open review submissions |
| `external.press_summary` | Social media / press |
| `health.publication_monitor` | Pipeline health checks |

## Install

```bash
pip install stegverse-publisher
```

## Requires

- `stegverse-core-lite >= 1.0.0`
- `stegverse-core-full >= 1.0.0`
- `stegverse-core-addons >= 1.0.0`

## Quick Start

```python
from publication_plane.core.publication_gate import PublicationGate
from publication_plane.core.receipt_writer import PublicationReceiptWriter

# Evaluate gate
gate = PublicationGate()
decision = gate.evaluate(
    gate_result="ALLOW",
    confidence=0.947,
    evidence={"passes": 3},
    seed="run-001"
)

# Write receipt if permitted
if decision["action"] == "publish":
    writer = PublicationReceiptWriter(seed="run-001")
    receipt = writer.write(
        gate_result="ALLOW",
        confidence=0.947,
        evidence=decision,
        module="my_module",
        destination="GCAT-BCAT-Engine/Publisher"
    )
    print(f"Published: {receipt}")
```

## Architecture

Publisher consumes Core-Components via Protocol injection:

```
Publisher → stegverse-core-lite (receipts, hashing)
         → stegverse-core-full (governance, monitoring, notary)
         → stegverse-core-addons (LLM, analytics, cross-org, badges, press)
```

## License

Commercial — see LICENSE file.

## Ecosystem Tiers

- **Lite** — Free primitives ([core-lite](https://github.com/GCAT-BCAT-Engine/core-lite))
- **Full** — Governance suite ([core-full](https://github.com/GCAT-BCAT-Engine/core-full))
- **Add-ons** — À la carte extensions ([core-addons](https://github.com/GCAT-BCAT-Engine/core-addons))
- **Publisher** — This package: publication orchestration
