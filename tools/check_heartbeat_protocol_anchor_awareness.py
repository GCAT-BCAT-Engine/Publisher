#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'data'/'heartbeat-protocol-anchor-awareness.json'
def main():
 d=json.loads(STATE.read_text())
 expected={'state':'COMPLETE_SOURCE_AUDIT','anchor_epoch':32,'anchor_time_utc':'2026-08-23T19:00:00.000Z','period_ms':10,'reference_rate_hz':100,'progression_dependency':'OSCILLATOR_ONLY','continuous_reference_stream':True,'new_reference_every_10ms':True,'continuous_process_required':False,'resident_sampler_required_for_progression':False,'observation_is_causal':False,'live_009_state':'COMPLETED','live_009_transition':'INDEPENDENT_HEARTBEAT_LIVE_PROOF_VERIFIED','publisher_transition_is_protocol_epoch':False,'workflow_cadence_is_heartbeat_cadence':False,'heartbeat_grants_publication_authority':False,'heartbeat_grants_execution_authority':False,'heartbeat_timing_authority':False,'authority_effect':'NONE','credential_authority':'TV/TVC'}
 bad=[k for k,v in expected.items() if d.get(k)!=v]
 if bad:
  print('PUBLISHER_HB32_AWARENESS_FAIL:'+','.join(bad)); return 1
 print('PUBLISHER_HB32_AWARENESS_PASS continuous_10ms=true authority_effect=NONE'); return 0
if __name__=='__main__': raise SystemExit(main())
