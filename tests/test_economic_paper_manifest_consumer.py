from __future__ import annotations
import hashlib
import json
import unittest

from publisher.economic_paper_manifest_consumer import (
    TASK_ID, TARGET_REPOSITORY, CANDIDATE_SCHEMA,
    EconomicPaperManifestError, consume_sdk_paper_manifest,
)

SOURCE="# exact paper fixture"
def sha(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def blob(text):
    raw=text.encode()
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
def candidate():
    return {"schema":CANDIDATE_SCHEMA,"goal_task_id":TASK_ID,"target_repository":TARGET_REPOSITORY,
      "target_path":"papers/economic.md","source_commit_sha":"1"*40,"source_sha256":hashlib.sha256(SOURCE.encode()).hexdigest(),
      "source_git_blob_sha":blob(SOURCE),"editorial_owner_approved":True,
      "review_policy":{"mode":"RESEARCH_PUBLICATION_WITH_DISCLOSED_UNVERIFIED_EXTERNAL_REVIEW","policy_ref":"GCAT-BCAT-Engine/Publisher:docs/ENTITY_ECONOMY_VOLUME_III_INDEPENDENT_REVIEW_PACKET.md#2026-09-28-owner-policy-disposition","external_review_claimed":False,"owner_attested_convergence":True,"economics_report_sha256":None,"legal_report_sha256":None},"publication_executed":False,"authority_effect":"NONE"}
def manifest():
    c=candidate()
    action={"actor_class":"publisher_paper_publication_candidate","action":"request_governed_paper_publication",
      "target":TARGET_REPOSITORY+":"+c["target_path"],"scope":"publisher_paper_publication",
      "parameters":{"goal_task_id":TASK_ID,"source_commit_sha":c["source_commit_sha"],"source_sha256":c["source_sha256"],
       "source_git_blob_sha":c["source_git_blob_sha"],"target_repository":TARGET_REPOSITORY,"target_path":c["target_path"],
       "review_evidence":{"mode":c["review_policy"]["mode"],**dict(c["review_policy"])},"publication_executed":False,"external_side_effect_requested":True}}
    payload={"candidate":c,"source_text_utf8":SOURCE}
    return {"manifest_profile":"stegverse.ingress-manifest.v1","manifest_profile_version":"1",
      "source_framework":"publisher_approved_paper_source","source_output_id":"fixture","created_at":"2026-09-28T00:00:00Z",
      "freshness":{},"payload":payload,"processing":{"capability":"governance","route_id":"canonical"},
      "declared_intent":"x","requested_consequence":"x","context_refs":[],"canonicalization_profile":"steggate.jcs.v1",
      "hashes":{"payload_sha256":sha(payload),"candidate_sha256":sha(action)},"attestation":None,
      "extensions":{"stegverse_route":{"route_id":"canonical"},"stegverse_governance_request":{"candidate":action,"permission_present":False},
        "security_posture_request":{"task_id":TASK_ID,"authority_effect":"NONE_REQUEST_INPUT_ONLY"}},
      "candidate":action,"return_projection":{"mode":"ALL","transition_classes":[]},"manifest_labels":{"mode":"NONE"},
      "completion":{"direction":"SOUTH","initiator":{"class":"publisher_paper_publication_candidate","ref":TASK_ID},
       "publisher":{"stage":"PUBLISHER","required":True,"package_profile":"stegverse.publisher.evidence-report-package/v1"},
       "egress":{"final_stegverse_transition_surface":"LLM_ADAPTER","transport":"INTERLOCK_INTR","far_side_transition_required":True,
        "destination_profile":TARGET_REPOSITORY}}}
class Tests(unittest.TestCase):
    def test_accepts_exact_sdk_binding_without_authority(self):
        r=consume_sdk_paper_manifest(manifest())
        self.assertEqual(r["state"],"SOURCE_BOUND_MANIFEST_ACCEPTED")
        self.assertFalse(r["runtime_invoked"]); self.assertFalse(r["mutation_authorized"])
        self.assertEqual(r["next_runtime_binding"],"stegverse.manifest_state_transition_runtime.execute_manifest")
    def test_tampered_source_fails(self):
        m=manifest();m["payload"]["source_text_utf8"]+="x";m["hashes"]["payload_sha256"]=sha(m["payload"])
        with self.assertRaisesRegex(EconomicPaperManifestError,"exact_source_sha256_mismatch"): consume_sdk_paper_manifest(m)
    def test_owner_policy_accepts_no_fabricated_review_hashes(self):
        r=consume_sdk_paper_manifest(manifest())
        self.assertEqual(r["review_evidence"]["mode"],"RESEARCH_PUBLICATION_WITH_DISCLOSED_UNVERIFIED_EXTERNAL_REVIEW")
        self.assertFalse(r["review_evidence"]["external_review_claimed"])
    def test_policy_cannot_claim_external_review_without_reports(self):
        m=manifest();m["payload"]["candidate"]["review_policy"]["external_review_claimed"]=True
        m["candidate"]["parameters"]["review_evidence"]["external_review_claimed"]=True
        m["extensions"]["stegverse_governance_request"]["candidate"]=m["candidate"]
        m["hashes"]["payload_sha256"]=sha(m["payload"]);m["hashes"]["candidate_sha256"]=sha(m["candidate"])
        with self.assertRaisesRegex(EconomicPaperManifestError,"claim_boundary_invalid"): consume_sdk_paper_manifest(m)
    def test_wrong_target_and_self_permission_fail(self):
        m=manifest();m["completion"]["egress"]["destination_profile"]="StegVerse-Labs/admissibility-wiki"
        with self.assertRaisesRegex(EconomicPaperManifestError,"publisher_destination_binding_mismatch"): consume_sdk_paper_manifest(m)
        m=manifest();m["extensions"]["stegverse_governance_request"]["permission_present"]=True
        with self.assertRaisesRegex(EconomicPaperManifestError,"self_grant"): consume_sdk_paper_manifest(m)
if __name__=="__main__": unittest.main()
