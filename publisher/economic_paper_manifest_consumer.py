"""Native Publisher source consumer for exact SDK economic paper manifests.

This module validates the manifest binding independently inside Publisher. It does
not execute Interlock/InTr, query Master Records, authorize mutation, or publish.
"""
from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from typing import Any, Mapping

TASK_ID = "ECOSYSTEM-ECONOMIC-WHITEPAPER-GATED-ROADMAP-001"
TARGET_REPOSITORY = "GCAT-BCAT-Engine/Publisher"
CANDIDATE_SCHEMA = "stegverse.publisher.paper-publication-candidate/v1"
INTAKE_SCHEMA = "stegverse.publisher.paper-manifest-intake/v1"
MANIFEST_PROFILE = "stegverse.ingress-manifest.v1"
PUBLISHER_PACKAGE_PROFILE = "stegverse.publisher.evidence-report-package/v1"\nRESEARCH_REVIEW_POLICY_MODE = "RESEARCH_PUBLICATION_WITH_DISCLOSED_UNVERIFIED_EXTERNAL_REVIEW"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")


class EconomicPaperManifestError(ValueError):
    pass


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EconomicPaperManifestError(label + "_required")
    return value.strip()


def _source_git_blob_sha(raw: bytes) -> str:
    header = b"blob " + str(len(raw)).encode("ascii") + bytes([0])
    return hashlib.sha1(header + raw).hexdigest()


def _validate_paper_candidate(value: Mapping[str, Any], source_text: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise EconomicPaperManifestError("paper_candidate_required")
    c = deepcopy(dict(value))
    required = {
        "schema","goal_task_id","target_repository","target_path","source_commit_sha",
        "source_sha256","source_git_blob_sha","editorial_owner_approved",
        "review_report_sha256","publication_executed","authority_effect",
    }
    if set(c) != required:
        raise EconomicPaperManifestError("paper_candidate_fields_mismatch")
    if c["schema"] != CANDIDATE_SCHEMA or c["goal_task_id"] != TASK_ID:
        raise EconomicPaperManifestError("paper_candidate_identity_mismatch")
    if c["target_repository"] != TARGET_REPOSITORY:
        raise EconomicPaperManifestError("paper_target_repository_mismatch")
    path = _text(c["target_path"], "paper_target_path")
    if not path.startswith("papers/") or path.endswith("/") or ".." in path or "\\" in path:
        raise EconomicPaperManifestError("paper_target_path_invalid")
    if c["editorial_owner_approved"] is not True:
        raise EconomicPaperManifestError("editorial_owner_approval_required")
    if c["publication_executed"] is not False or c["authority_effect"] != "NONE":
        raise EconomicPaperManifestError("candidate_authority_or_publication_claim_forbidden")
    commit = c["source_commit_sha"]
    digest = c["source_sha256"]
    blob = c["source_git_blob_sha"]
    if not isinstance(commit,str) or not _COMMIT.fullmatch(commit):
        raise EconomicPaperManifestError("source_commit_invalid")
    if not isinstance(digest,str) or not _DIGEST.fullmatch(digest):
        raise EconomicPaperManifestError("source_sha256_invalid")
    if not isinstance(blob,str) or not _COMMIT.fullmatch(blob):
        raise EconomicPaperManifestError("source_blob_invalid")
    raw = source_text.encode("utf-8")
    if hashlib.sha256(raw).hexdigest() != digest:
        raise EconomicPaperManifestError("exact_source_sha256_mismatch")
    if _source_git_blob_sha(raw) != blob:
        raise EconomicPaperManifestError("exact_source_git_blob_mismatch")
    if "review_report_sha256" in c:
        reviews = c["review_report_sha256"]
        if not isinstance(reviews, Mapping) or set(reviews) != {"economics","legal"}:
            raise EconomicPaperManifestError("review_digest_set_required")
        if not all(isinstance(reviews[k],str) and _DIGEST.fullmatch(reviews[k]) for k in reviews):
            raise EconomicPaperManifestError("review_digest_invalid")
    else:
        policy = c["review_policy"]
        required_policy = {
            "mode","policy_ref","external_review_claimed","owner_attested_convergence",
            "economics_report_sha256","legal_report_sha256",
        }
        if not isinstance(policy, Mapping) or set(policy) != required_policy:
            raise EconomicPaperManifestError("review_policy_disposition_invalid")
        if policy["mode"] != RESEARCH_REVIEW_POLICY_MODE:
            raise EconomicPaperManifestError("review_policy_mode_invalid")
        if policy["external_review_claimed"] is not False or policy["owner_attested_convergence"] is not True:
            raise EconomicPaperManifestError("review_policy_claim_boundary_invalid")
        _text(policy["policy_ref"], "review_policy_ref")
        if policy["economics_report_sha256"] is not None or policy["legal_report_sha256"] is not None:
            raise EconomicPaperManifestError("unverified_review_hashes_must_be_null")
    return c


def _review_binding(c: Mapping[str, Any]) -> dict[str, Any]:
    if "review_report_sha256" in c:
        return {"mode":"EXTERNAL_REPORTS","report_sha256":dict(c["review_report_sha256"])}
    return {"mode":c["review_policy"]["mode"], **dict(c["review_policy"])}


def _expected_action(c: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "actor_class": "publisher_paper_publication_candidate",
        "action": "request_governed_paper_publication",
        "target": f"{TARGET_REPOSITORY}:{c['target_path']}",
        "scope": "publisher_paper_publication",
        "parameters": {
            "goal_task_id": TASK_ID,
            "source_commit_sha": c["source_commit_sha"],
            "source_sha256": c["source_sha256"],
            "source_git_blob_sha": c["source_git_blob_sha"],
            "target_repository": TARGET_REPOSITORY,
            "target_path": c["target_path"],
            "review_evidence": _review_binding(c),
            "publication_executed": False,
            "external_side_effect_requested": True,
        },
    }


def validate_sdk_paper_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, Mapping):
        raise EconomicPaperManifestError("sdk_manifest_required")
    m = deepcopy(dict(manifest))
    if m.get("manifest_profile") != MANIFEST_PROFILE or str(m.get("manifest_profile_version")) != "1":
        raise EconomicPaperManifestError("sdk_manifest_profile_mismatch")
    if m.get("source_framework") != "publisher_approved_paper_source":
        raise EconomicPaperManifestError("sdk_source_framework_mismatch")
    processing = m.get("processing")
    if not isinstance(processing, Mapping) or processing.get("capability") != "governance":
        raise EconomicPaperManifestError("sdk_governance_processing_required")
    payload = m.get("payload")
    if not isinstance(payload, Mapping) or set(payload) != {"candidate","source_text_utf8"}:
        raise EconomicPaperManifestError("sdk_paper_payload_invalid")
    source_text = payload.get("source_text_utf8")
    if not isinstance(source_text, str):
        raise EconomicPaperManifestError("sdk_exact_source_text_required")
    c = _validate_paper_candidate(payload.get("candidate"), source_text)
    hashes = m.get("hashes")
    if not isinstance(hashes, Mapping):
        raise EconomicPaperManifestError("sdk_manifest_hashes_required")
    if hashes.get("payload_sha256") != _sha256(payload):
        raise EconomicPaperManifestError("sdk_payload_hash_mismatch")
    expected = _expected_action(c)
    if m.get("candidate") != expected or hashes.get("candidate_sha256") != _sha256(expected):
        raise EconomicPaperManifestError("sdk_governance_candidate_binding_mismatch")
    ext = m.get("extensions")
    if not isinstance(ext, Mapping):
        raise EconomicPaperManifestError("sdk_extensions_required")
    req = ext.get("stegverse_governance_request")
    if not isinstance(req, Mapping) or req.get("candidate") != expected:
        raise EconomicPaperManifestError("sdk_governance_request_binding_mismatch")
    if req.get("permission_present") is not False:
        raise EconomicPaperManifestError("caller_may_not_self_grant_publication_permission")
    posture = ext.get("security_posture_request")
    if not isinstance(posture, Mapping):
        raise EconomicPaperManifestError("security_posture_request_required")
    if posture.get("task_id") != TASK_ID or posture.get("authority_effect") != "NONE_REQUEST_INPUT_ONLY":
        raise EconomicPaperManifestError("security_posture_task_or_authority_mismatch")
    completion = m.get("completion")
    if not isinstance(completion, Mapping):
        raise EconomicPaperManifestError("sdk_completion_required")
    pub = completion.get("publisher")
    eg = completion.get("egress")
    if not isinstance(pub, Mapping) or pub.get("stage") != "PUBLISHER" or pub.get("required") is not True:
        raise EconomicPaperManifestError("publisher_stage_required")
    if pub.get("package_profile") != PUBLISHER_PACKAGE_PROFILE:
        raise EconomicPaperManifestError("publisher_package_profile_mismatch")
    if not isinstance(eg, Mapping) or eg.get("transport") != "INTERLOCK_INTR":
        raise EconomicPaperManifestError("interlock_intr_transport_required")
    if eg.get("far_side_transition_required") is not True or eg.get("destination_profile") != TARGET_REPOSITORY:
        raise EconomicPaperManifestError("publisher_destination_binding_mismatch")
    return m


def consume_sdk_paper_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Produce a deterministic Publisher intake record; never a runtime verdict."""
    m = validate_sdk_paper_manifest(manifest)
    c = m["payload"]["candidate"]
    return {
        "schema": INTAKE_SCHEMA,
        "state": "SOURCE_BOUND_MANIFEST_ACCEPTED",
        "goal_task_id": TASK_ID,
        "target_repository": TARGET_REPOSITORY,
        "target_path": c["target_path"],
        "source_commit_sha": c["source_commit_sha"],
        "source_sha256": c["source_sha256"],
        "source_git_blob_sha": c["source_git_blob_sha"],
        "review_evidence": _review_binding(c),
        "manifest_sha256": _sha256(m),
        "next_runtime_binding": "stegverse.manifest_state_transition_runtime.execute_manifest",
        "transition_authority": "INTERLOCK_INTR",
        "credential_authority": "TV/TVC",
        "custody_authority": "MASTER_RECORDS",
        "runtime_invoked": False,
        "authentic_intr_disposition_observed": False,
        "master_records_closure_observed": False,
        "publication_authorized": False,
        "release_authorized": False,
        "mutation_authorized": False,
        "authority_effect": "NONE_SOURCE_INTAKE_ONLY",
    }
