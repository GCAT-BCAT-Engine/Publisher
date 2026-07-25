#!/usr/bin/env python3
"""Fail closed if Publisher activation import regains timer or mutation fan-out."""
from pathlib import Path
import sys

WORKFLOW = Path('.github/workflows/import-ecosystem-chat-activation.yml')
IMPORTER = Path('scripts/import_ecosystem_chat_activation.py')


def fail(message: str) -> None:
    print(f'PUBLISHER_ACTIVATION_ORCHESTRATION_CONTRACT: FAIL: {message}')
    raise SystemExit(1)


def main() -> int:
    if not WORKFLOW.is_file():
        fail(f'missing {WORKFLOW}')
    if not IMPORTER.is_file():
        fail(f'missing {IMPORTER}')

    workflow = WORKFLOW.read_text(encoding='utf-8')
    on_block = workflow.split('permissions:', 1)[0]
    importer = IMPORTER.read_text(encoding='utf-8')

    if 'schedule:' in on_block:
        fail('Publisher importer must not own an hourly timer')
    for marker in (
        'workflow_dispatch:',
        'push:',
        '- main',
        'cancel-in-progress: true',
        "if: github.event_name == 'push'",
        "if: github.event_name == 'workflow_dispatch'",
        '[skip ci]',
        'Validate Publisher activation orchestration contract',
    ):
        if marker not in workflow:
            fail(f'required workflow marker absent: {marker}')
    if 'cancel-in-progress: false' in workflow:
        fail('superseded Publisher import runs must be cancelled')

    for marker in (
        'site-orchestration-terminal-custody.json',
        'stegverse.master_records.site_orchestration_terminal_custody.v1',
        'terminal_custody_sha256',
        'custody_state") != "RECORDED"',
        'reconstruction.get("state") != "PASS"',
        'exact_commit_binding',
        'stage_chain_complete',
        'supersession_clear',
        'custody_authority_boundary_invalid',
        'packet_custody_binding_mismatch',
        'state_custody_binding_mismatch',
    ):
        if marker not in importer:
            fail(f'required custody gate marker absent: {marker}')

    print('PUBLISHER_ACTIVATION_ORCHESTRATION_CONTRACT: PASS')
    print('schedule_authority=false')
    print('manual_dispatch_authority=validation_only')
    print('persistent_mutation_authority=main_push_only')
    print('terminal_custody_required=true')
    print('superseded_run_policy=cancel')
    return 0


if __name__ == '__main__':
    sys.exit(main())
