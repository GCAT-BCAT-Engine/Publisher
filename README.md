# StegVerse Publisher

A lightweight, static-site paper publishing system for the StegVerse ecosystem. No backend required. Papers are declared in a YAML manifest, rendered by vanilla JS, and served from any static host (CloudFlare Pages, GitHub Pages, etc.).

## Architecture

```
publisher/
├── papers.html              # Listing page (filterable grid)
├── publisher.css            # Shared styles
├── publisher.js             # Frontend controller
├── papers.json              # Generated from manifest (runtime data)
├── papers_manifest.yml      # Source of truth (human-editable)
├── papers/
│   └── sv-cost-reduction-2026.html   # Individual paper pages
└── README.md
```

## How It Works

1. **Add a paper** to `papers_manifest.yml`
2. **Generate** `papers.json` (one-time or CI step)
3. **Create** the individual paper HTML page in `papers/`
4. **Deploy** — everything is static

## papers_manifest.yml Format

```yaml
papers:
  - id: unique-paper-id
    title: "Paper Title"
    subtitle: "Optional subtitle"
    authors:
      - name: Author Name
        affiliation: Institution
        orcid: 0000-0000-0000-0000
    date: "2026-05-02"
    version: "1.0.0"
    status: published          # published | draft | under_review
    category: cost_optimization
    tags: [tag1, tag2]
    abstract: "..."
    doi: null                  # or "10.xxxx/xxxxx"
    pdf_url: null              # or "./papers/paper.pdf"
    html_url: "./papers/paper.html"
    source_repo: "Org/Repo"
    license: "CC-BY-4.0"
    peer_review: false
    citations: 0
    downloads: 0
    featured: true             # one featured paper shown at top
```

## Categories

- `cost_optimization`
- `formal_methods`
- `philosophy_of_computation`
- `architecture`
- `governance`
- `experimental`

## Generating papers.json

```bash
# Requires Python + PyYAML
python -c "
import yaml, json
with open('papers_manifest.yml') as f:
    data = yaml.safe_load(f)
with open('papers.json', 'w') as f:
    json.dump(data['papers'], f, indent=2)
"
```

Or use the GitHub Action (see `.github/workflows/generate-papers.yml`).

## Site Paper Display Policy

The StegVerse Site should display current papers and governance case studies from Publisher-controlled records, not from a separate Site editorial copy.

Policy and update protocol are defined in:

```text
docs/site-paper-display-policy.md
```

Site display updates should follow this order:

```text
1. Update Publisher source record.
2. Validate Publisher record.
3. Generate or refresh Publisher runtime data.
4. Dispatch Site mirror workflow.
5. Verify Site links resolve to Publisher-owned paths.
6. Produce Site evidence artifact.
7. Close Publisher activation only from fresh ordered Publisher/Site evidence artifacts.
```

## Site Mirror Dispatch

Publisher can dispatch the Site mirror workflow after Publisher validation passes.

The Publisher dispatch workflow is displayed as:

```text
github/workflows/dispatch-site-mirror.yml
```

In the repository, the actual path is `.github/workflows/dispatch-site-mirror.yml`.

Operational details are defined in:

```text
docs/site-mirror-dispatch-protocol.md
```

The current Publisher-side continuation handoff is:

```text
docs/PUBLISHER_MIRROR_HANDOFF.md
```

The current Publisher-side closure evidence packet is:

```text
docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md
```

The current pending closure status is:

```text
docs/PUBLISHER_PENDING_CLOSURE_STATUS.md
```

The current self-managed completion record is:

```text
docs/PUBLISHER_SELF_MANAGED_COMPLETION.md
```

The pending closure status is not activation evidence. It records that Publisher receipt, Site evidence, and closure have not been recorded in that status surface.

Dry run remains available with:

```text
dry_run: true
```

Dry run validates Publisher records and dispatch configuration without requiring a token or triggering Site. It is an optional diagnostic fallback, not the activation boundary.

The Publisher repo secret required for live dispatch is:

```text
SITE_MIRROR_DISPATCH_TOKEN
```

## Release Gate

Publisher-to-Site release status is governed by:

```text
docs/release-gate-checklist.md
```

A Site display should not be marked current until Publisher source validity, dispatch readiness, Site mirror validity, public display verification, governance case posture checks, closure evidence verification, and self-managed completion validation all pass.

## Activation Status

Current repo activation status is tracked in:

```text
docs/activation-status.md
```

The current activation boundary is fresh ordered evidence production: Publisher receipt artifact, Site evidence artifact, freshness/order verification, closure receipt, verification tracker activation, and activation status update to `activated`.

The pending probe is not an activation receipt. The pending closure status is also not an activation receipt. The self-managed completion document is also not an activation receipt.

## Validation

Run the complete Publisher activation validation sequence with:

```bash
python tools/check_publisher_activation.py
```

The activation runner executes:

```text
python tools/check_site_mirror_dispatch.py
python tools/check_release_gate.py
python tools/check_publisher_mirror_handoff.py
python tools/check_mirror_ecosystem_management_handoff.py
python tools/check_publisher_closure_evidence_production.py
python tools/check_publisher_self_managed_completion.py
```

Self-managed completion means the repository can continue with repo-resident workflows, validators, handoffs, pending-status runtime updates, receipt-boundary preservation, and closure receipt logic. Live activation still requires the fresh Publisher receipt artifact, fresh Site evidence artifact, and closure receipt commit.

## Governance Case Scaffolding

Publisher can create a four-file emergency AI restriction case family from templates:

```bash
python tools/create_emergency_ai_case_scaffold.py CASE-YYYY-MM-SLUG \
  --title "Emergency AI Restriction Case Title" \
  --event-date EVENT-YYYY-MM-DD \
  --observed-date OBSERVED-YYYY-MM-DD
```

This generates:

```text
cases/<CASE-ID>.md
governance/cases/<CASE-ID>.case.json
governance/cases/<CASE-ID>.sources.json
governance/receipts/<CASE-ID>.receipt.json
```

Existing files are preserved by default. Use `--force` only when overwrite is intended.

Publisher also carries machine-readable governance case objects for public case studies.

Emergency AI restriction case objects are stored in:

```text
governance/cases/*.case.json
```
