#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'tga-publisher-projection.json'
DOC = ROOT / 'docs' / 'TGA_TEMPORAL_GOVERNED_ANALYSIS.md'
HANDOFF = ROOT / 'docs' / 'TGA_PUBLISHER_PROJECTION_MIRROR_HANDOFF.md'


def fail(msg: str) -> None:
    raise SystemExit('TGA_PUBLISHER_PROJECTION=FAIL: ' + msg)


def main() -> int:
    for path in (DATA, DOC, HANDOFF):
        if not path.is_file(): fail(f'missing {path.relative_to(ROOT)}')
    data = json.loads(DATA.read_text(encoding='utf-8'))
    doc = DOC.read_text(encoding='utf-8')
    handoff = HANDOFF.read_text(encoding='utf-8')
    if data.get('upstream', {}).get('merge_commit') != '75a02d24cd9a413bdd268f0d831a87eb651dde6f': fail('wrong Site merge evidence')
    if data.get('upstream', {}).get('completion_marker') != 'TGA_SITE_PROJECTION=PASS': fail('missing Site completion marker')
    semantics = data.get('preserved_semantics', {})
    required_true = ['unresolved_states_preserved','provenance_preserved','exact_temporal_window_preserved','rule_context_version_preserved']
    required_false = ['canonical_representation_is_canonical_reality','encoding_precision_implies_correctness','media_custody_inferred','counterfactual_rewrites_historical_applicability']
    if not all(semantics.get(k) is True for k in required_true): fail('required preserved semantics missing')
    if not all(semantics.get(k) is False for k in required_false): fail('forbidden inference present')
    if any(data.get('authority', {}).values()): fail('authority escalation detected')
    for marker in ['Canonical representation is not canonical reality','does not create publication authority','Counterfactual application is explicitly marked']:
        if marker not in doc: fail(f'document missing marker: {marker}')
    if 'authority_effect: NONE_AWARENESS_PROJECTION_ONLY' not in handoff: fail('handoff authority boundary missing')
    print('TGA_PUBLISHER_PROJECTION=PASS')
    print('authority_effect=NONE_AWARENESS_PROJECTION_ONLY')
    print('upstream_site_projection=VALIDATED')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
