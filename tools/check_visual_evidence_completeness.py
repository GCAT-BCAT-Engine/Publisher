#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
contract = json.loads((root / 'data/publisher-visual-evidence-contract.json').read_text())
revision = json.loads((root / 'data/elan-cumulative-publication-visual-revision.json').read_text())

assert contract['schema'] == 'stegverse.publisher-visual-evidence-contract/v1'
assert contract['rule']['experimental_or_evaluator_publication_requires_explicit_visual_evidence_disposition'] is True
assert contract['rule']['when_pertinent']['visual_evidence_required'] is True
assert contract['rule']['when_not_pertinent']['explicit_reason_required'] is True
assert 'POST_RUN_RECONSTRUCTED_EVIDENCE_VIEW' in contract['provenance_classes']

visual = revision['visual_evidence']
assert visual['run1_count'] == 6
assert visual['run2_count'] == 14
assert visual['run2_classification'] == 'POST_RUN_RECONSTRUCTED_EVIDENCE_VIEW'
assert len(visual['run2_ordered_files']) == 14
assert len(set(visual['run2_ordered_files'])) == 14
assert visual['run2_ordered_files'][0] == '01_run2_source_input.png'
assert visual['run2_ordered_files'][-1] == '14_run2_controlled_comparison.png'
assert 'not contemporaneous historical screenshots' in visual['run2_provenance_note']

qa = revision['qa']
assert qa['docx_page_count'] == qa['pdf_page_count'] == 21
assert qa['docx_visual_review'] == 'PASS'
assert qa['pdf_visual_review'] == 'PASS'
assert qa['observed_blank_pages'] == 0
assert qa['observed_clipping_or_overlap'] is False
assert revision['lifecycle'] == 'GENERATED_VALIDATED_NOT_PUBLISHED'
assert revision['authority_effect'] == 'NONE'

for key, value in revision['artifacts'].items():
    if key.endswith('_sha256'):
        assert isinstance(value, str) and len(value) == 64

print('PASS: Publisher visual evidence completeness contract and ELAN visual revision evidence are internally consistent')
