#!/usr/bin/env python3
import json
from pathlib import Path

p = Path('data/tcl-propagation-receipt.json')
data = json.loads(p.read_text())
assert data['source_repository'] == 'StegVerse-Labs/T-CL'
assert data['destination_repository'] == 'GCAT-BCAT-Engine/Publisher'
assert data['destination_handoff_checked'] == 'PUBLISHER_MIRROR_HANDOFF.md'
assert data['intake_record'] == 'data/tcl-propagation-intake.json'
assert data['manual_task_required'] is False
b = data['publisher_boundary']
assert b['routing_surface_only'] is True
assert b['no_semantic_redefinition'] is True
assert b['no_release_certification_claim'] is True
assert b['no_downstream_completion_claim'] is True
assert b['no_measured_savings_claim'] is True
print(str(p) + ': pass')
