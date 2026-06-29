#!/usr/bin/env python3
import json
from pathlib import Path

p = Path('data/tcl-publication-route-status.json')
data = json.loads(p.read_text())
assert data['source_repository'] == 'StegVerse-Labs/T-CL'
assert data['destination_repository'] == 'GCAT-BCAT-Engine/Publisher'
assert data['intake_record'] == 'data/tcl-propagation-intake.json'
assert data['receipt_record'] == 'data/tcl-propagation-receipt.json'
assert data['manual_task_required'] is False
assert data['route_status'] == 'bounded_route_recorded_no_downstream_publication_claim'
r = data['allowed_route']
assert r['route_type'] == 'status_only_mirror_instruction'
assert r['requires_target_handoff_check'] is True
assert r['requires_target_receipt'] is True
blocked = set(data['blocked_claims'])
assert 'Publisher certifies T-CL' in blocked
assert 'Publisher redefines T-CL semantics' in blocked
assert 'Publisher claims downstream propagation complete before target receipts exist' in blocked
print(str(p) + ': pass')
