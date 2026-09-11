# General Evidence Report Pipeline

Status: IMPLEMENTATION CANDIDATE

## Purpose

Publisher provides one reusable, non-authorizing function for turning a structured evidence package into evaluator-facing artifacts. The function is intentionally domain-neutral: MIR, ELAN, SDK evaluations, formalism tests, product demonstrations, and future evidence-backed programs provide data packages; Publisher provides validation and rendering.

The canonical package schema is:

`stegverse.publisher.evidence-report-package/v1`

The command-line surface is:

```bash
python tools/render_evidence_report.py package.json --output-dir /tmp/evidence-report
```

The implementation emits requested Markdown, HTML, PDF, DOCX, and JSON artifacts together with `artifact-manifest.json` and `rendering-receipt.json`.

## Separation of responsibilities

The source/test system owns authentic inputs and evidence. Publisher does not create execution evidence, replay evidence, reconstruction evidence, screenshots, checkpoint pins, or governance decisions.

Publisher validates the supplied package, organizes the evaluator narrative, renders output formats, hashes generated artifacts, and records a rendering receipt.

Rendering produces `GENERATED_VALIDATED_NOT_PUBLISHED`. It grants no publication, release, execution, governance, credential, custody, licensing, or deployment authority.

## General report structure

The package supports:

1. abstract;
2. objective and scope;
3. frozen parameters;
4. primary execution and result;
5. replay and result;
6. reconstruction and result;
7. screenshot walkthrough;
8. conclusion;
9. Appendix A — evidence ledger;
10. Appendix B — function/SDK overview and usage instructions;
11. Appendix C — roadmap and future development.

The same structure is reusable for MIR and ELAN without adding project-specific logic to Publisher.

## Completion semantics

A package may be rendered while `DRAFT` or `IN_PROGRESS`; unexecuted stages remain explicit.

A package marked `COMPLETE` fails closed unless primary execution, replay, and reconstruction are all `EXECUTED` and carry evidence references, and at least one screenshot artifact is retained. An executed stage without evidence references is rejected.

This protects the distinction between a presentation draft and a completed evidence-backed test report.

## Screenshot classes

Screenshots are explicitly classified as:

- `PRE_RUN_FROZEN_EVIDENCE`
- `RUNTIME_EVIDENCE`
- `PRESENTATION_CAPTURE`

Presentation captures may explain the workflow but do not become retroactive test evidence.

## Browser roadmap

The renderer is intentionally package-driven so a browser surface can later submit the same package and receive the same canonical artifacts. Browser access must remain semantic parity with the programmatic function, not a second Publisher implementation with relaxed evidence or authority rules.

Target browser functions include package/manifest construction, evidence-field registration, screenshot attachment and digest display, draft preview, result/replay/reconstruction sections, artifact export, and receipt inspection.

## First consumers

- MIR × StegVerse SDK/evidence test presentation — first concrete package.
- ELAN — intended second concrete package using the same general function when source materials are supplied.

Neither consumer changes the generic schema or Publisher authority boundary merely because its evidence vocabulary differs.
