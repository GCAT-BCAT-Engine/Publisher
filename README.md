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
4. Update Site display surface.
5. Verify Site links resolve to Publisher-owned paths.
6. Commit Site update with Publisher source reference.
```

## Site Mirror Dispatch

Publisher can dispatch the Site mirror workflow after Publisher validation passes.

The Publisher dispatch workflow is:

```text
github/workflows/dispatch-site-mirror.yml
```

In the repository, the actual path is `.github/workflows/dispatch-site-mirror.yml`.

Operational details are defined in:

```text
docs/site-mirror-dispatch-protocol.md
```

Before installing or relying on dispatch credentials, run the workflow manually with:

```text
dry_run: true
```

Dry run validates Publisher records and dispatch configuration without requiring a token or triggering Site.

The Publisher repo secret required for live dispatch is:

```text
SITE_MIRROR_DISPATCH_TOKEN
```

## Release Gate

Publisher-to-Site release status is governed by:

```text
docs/release-gate-checklist.md
```

A Site display should not be marked current until Publisher source validity, dispatch readiness, Site mirror validity, public display verification, and governance case posture checks all pass.

## Activation Status

Current repo activation status is tracked in:

```text
docs/activation-status.md
```

The current activation boundary is manual dry-run execution, dry-run receipt capture, live dispatch, Site mirror completion, live-dispatch receipt capture, and verification tracker update to `activated`.

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

## Validation

Publisher also carries machine-readable governance case objects for public case studies.

Emergency AI restriction case objects are stored in:

```text
governance/cases/*.case.json
```

They are validated against:

```text
governance/schemas/emergency-ai-restriction.case.schema.json
```

Run the full local activation validation sequence with:

```bash
python -m pip install -r requirements.txt
python tools/check_publisher_activation.py
```

The activation runner executes:

```bash
python tools/check_emergency_ai_templates.py
python tools/validate_emergency_ai_cases.py
python tools/check_site_mirror_dispatch.py
python tools/check_release_gate.py
```

The GitHub Actions workflow path is shown here without its leading dot:

```text
github/workflows/validate-emergency-ai-cases.yml
```

In the repository, the actual path is `.github/workflows/validate-emergency-ai-cases.yml`.

For details, see:

```text
docs/validation.md
docs/site-paper-display-policy.md
docs/site-mirror-dispatch-protocol.md
docs/release-gate-checklist.md
docs/activation-status.md
docs/iphone-dry-run-runbook.md
docs/verification-run-receipt.template.json
templates/README.md
governance/README.md
```

## Integration with StegVerse Site

The Publisher lives as a subdirectory of the main site:

```
Site/
├── index.html
├── demo.html
├── assets/
│   └── css/
│       └── demo-styles.css
└── publisher/          # ← this directory
    ├── papers.html
    ├── publisher.css
    ├── publisher.js
    ├── papers.json
    ├── papers_manifest.yml
    └── papers/
        └── *.html
```

Navigation links between pages use relative paths:
- Home → `https://stegverse.org`
- Demo → `https://stegverse.org/demo.html`
- Papers → `https://stegverse.org/publisher/papers.html`

## Design Principles

1. **No build step required** — vanilla JS, no frameworks
2. **No backend required** — static JSON feed
3. **Commit-time admissibility** — every paper has a version, status, and audit trail
4. **Semantic boundary enforcement** — rejected optimizations are preserved as negative results
5. **CC-BY-4.0 default** — all papers open access unless otherwise noted

## Roadmap

- [ ] Auto-generate `papers.json` via GitHub Action on manifest push
- [ ] PDF generation pipeline (pandoc + LaTeX)
- [ ] DOI registration integration
- [ ] Citation counter (via API or manual)
- [ ] Peer review workflow (GitHub Issues → review threads)
- [ ] RSS/Atom feed for new papers
- [ ] OpenGraph meta tags for social sharing

## License

Publisher system: MIT
Papers content: CC-BY-4.0 (unless otherwise noted)
