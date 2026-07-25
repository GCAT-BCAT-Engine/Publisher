# Publisher Visibility and Authority Boundary

## Governing rule

Visibility and authority are independent state dimensions.

A publicly accessible artifact may be inspected, listed, discussed, or reviewed without gaining publication, attribution, endorsement, compatibility, interoperability, or external-association authority.

## Publisher decision model

Publisher consumes a machine-readable envelope containing:

```text
visibility_state
process_state
claim_authority
publication_authority
attribution_authority
public_association_authority
endorsement
compatibility
interoperability
external_references
requested_publication_action
```

The validator permits `INSPECT` and `LIST` as non-consequential visibility operations. It requires explicit authority for:

```text
PUBLISH -> publication_authority
ATTRIBUTE -> attribution_authority
ASSOCIATE_EXTERNAL -> public_association_authority
```

`PUBLICLY_VISIBLE` cannot be used as `authority_source`.

## Review-only posture

A `REVIEW_ONLY` artifact must declare every authority field `false` and every external claim field `NONE`. Any conflicting declaration fails closed.

Review acknowledgement, understanding, or feedback does not become endorsement, attribution permission, external association, compatibility validation, or interoperability validation.

## External references

External frameworks or participants may be represented as:

```text
REFERENCE_ONLY
REVIEW_REQUESTED
AUTHORIZED_ASSOCIATION
```

`AUTHORIZED_ASSOCIATION` requires explicit `public_association_authority`. A name appearing in a publicly visible file does not create that authority.

## Deterministic evidence

The validator canonicalizes each input envelope and produces `envelope_sha256`. A supplied hash is independently recomputed; mismatches are rejected.

## Commands

```bash
python tools/check_publication_authority_envelope.py \
  data/publication-authority-review-example.json

python -m unittest tests.test_publication_authority_envelope -v
```

## Boundary

Publisher validates and records publication handling posture. It does not create source authority, delegation, admissibility, standing, endorsement, attribution consent, compatibility, interoperability, or external-association permission.
