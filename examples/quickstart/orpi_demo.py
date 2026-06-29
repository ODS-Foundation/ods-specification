#!/usr/bin/env python3
"""
ORPI / Open Decision Standard — runnable reference demo (no dependencies).

What this shows in ~60 seconds:
  An AI agent makes a high-risk decision (a credit-scoring rejection).
  We record it as a verifiable ODS DECISION record — who decided, under what
  authority, with what rationale and outcome — hash-chained and anchored in a
  Merkle checkpoint. We generate an inclusion proof a third party can verify
  WITHOUT trusting us. Then we tamper with a stored record and watch the proof
  break — which is exactly what turns a log into evidence.

Why it matters: EU AI Act Article 12 requires high-risk AI systems to record
events over their lifecycle. It does not say "tamper-evident" — but a log that
can be silently altered has no evidentiary value. ODS is the format that makes
the record provable, not just present.

Run:  python orpi_demo.py
Stdlib only (hashlib, json, datetime). Python 3.8+.

Note: this is a teaching reference. Canonicalization here is a compact
sorted-key JSON (close to RFC 8785 / JCS); the full standard pins RFC 8785 and
RFC 6962 exactly. The cryptographic shape — hash-chain + Merkle inclusion — is
the real thing.
"""

import hashlib
import json
from datetime import datetime, timezone


# ----------------------------------------------------------------------------
# Cryptographic primitives
# ----------------------------------------------------------------------------

def canonical(obj) -> bytes:
    """Deterministic, canonical JSON bytes (sorted keys, compact). JCS-style."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def record_hash(record: dict) -> str:
    """Hash of a record's canonical form, excluding integrity fields."""
    core = {k: v for k, v in record.items()
            if k not in ("record_hash", "prev_hash", "sequence_number")}
    return sha256_hex(canonical(core))


# RFC 6962-style Merkle tree (domain-separated leaf/node hashing)
def _leaf(data: bytes) -> bytes:
    return hashlib.sha256(b"\x00" + data).digest()


def _node(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def merkle_root(leaves: list[bytes]) -> bytes:
    if not leaves:
        return hashlib.sha256(b"").digest()
    layer = [_leaf(x) for x in leaves]
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            if i + 1 < len(layer):
                nxt.append(_node(layer[i], layer[i + 1]))
            else:
                nxt.append(layer[i])  # odd node promoted
        layer = nxt
    return layer[0]


def inclusion_proof(leaves: list[bytes], index: int) -> list[str]:
    """Audit path (hex) proving leaves[index] is in the tree."""
    layer = [_leaf(x) for x in leaves]
    idx = index
    path = []
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            if i + 1 < len(layer):
                if i == idx or i + 1 == idx:
                    sib = layer[i + 1] if i == idx else layer[i]
                    path.append(sib.hex())
                nxt.append(_node(layer[i], layer[i + 1]))
            else:
                nxt.append(layer[i])
        idx //= 2
        layer = nxt
    return path


def verify_inclusion(leaf_data: bytes, index: int, size: int,
                     audit_path: list[str], root_hex: str) -> bool:
    """Recompute the root from a leaf + audit path. No trust in the producer."""
    h = _leaf(leaf_data)
    idx, last = index, size - 1
    for sib_hex in audit_path:
        sib = bytes.fromhex(sib_hex)
        if idx % 2 == 0 and idx != last:
            h = _node(h, sib)
        else:
            h = _node(sib, h)
        idx //= 2
        last //= 2
    return h.hex() == root_hex


# ----------------------------------------------------------------------------
# Minimal append-only ledger of ODS records
# ----------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Ledger:
    """Append-only, hash-chained store. Mutation is detectable by design."""

    def __init__(self):
        self.records: list[dict] = []

    def submit(self, record: dict) -> dict:
        prev = self.records[-1]["record_hash"] if self.records else "GENESIS"
        record = dict(record)
        record["sequence_number"] = len(self.records)
        record["prev_hash"] = prev
        record["record_hash"] = record_hash(record)
        self.records.append(record)
        return record

    def merkle_checkpoint(self) -> dict:
        leaves = [bytes.fromhex(r["record_hash"]) for r in self.records]
        root = merkle_root(leaves).hex()
        return {
            "_schema_version": "2.1.0",
            "record_type": "CHECKPOINT",
            "timestamp_utc": _now(),
            "tree_size": len(self.records),
            "merkle_root": root,
            "sequence_range": [0, len(self.records) - 1],
        }

    def proof_for(self, seq: int, checkpoint: dict):
        leaves = [bytes.fromhex(r["record_hash"]) for r in self.records]
        return inclusion_proof(leaves, seq)


# ----------------------------------------------------------------------------
# ODS record constructors (the part inference logs never capture)
# ----------------------------------------------------------------------------

def decision(record_id, model_version, policy_hash, rationale,
             action_type, profile, **fields) -> dict:
    return {
        "_schema_version": "2.1.0",
        "record_type": "DECISION",
        "record_id": record_id,
        "timestamp_utc": _now(),
        "profile": profile,
        "identity": {"model_version": model_version, "policy_hash": policy_hash},
        "cognition": {"rationale": rationale, **fields.get("cognition", {})},
        "action": {"action_type": action_type, **fields.get("action", {})},
        "governance": {
            "audit_trail": [{"event": "DECISION_CREATED",
                             "actor": fields.get("actor", "scoring-agent"),
                             "timestamp_utc": _now()}],
            "compliance": fields.get("compliance", {}),
        },
    }


def outcome(record_id, parent_id, status, profile, **outcomes) -> dict:
    return {
        "_schema_version": "2.1.0",
        "record_type": "OUTCOME",
        "record_id": record_id,
        "timestamp_utc": _now(),
        "parent_id": parent_id,
        "profile": profile,
        "outcome_status": status,
        "outcomes": outcomes,
    }


# ----------------------------------------------------------------------------
# The Article 12 scenario
# ----------------------------------------------------------------------------

def line(c="-"):
    print(c * 74)


def demo():
    print("\nORPI — verifiable decision records for EU AI Act Article 12")
    line("=")
    print("Scenario: an AI agent rejects a consumer loan application (high-risk,")
    print("Annex III credit scoring). Six months later a regulator asks:")
    print('  "Prove what the system decided, on what basis, and that this record')
    print('   has not been altered since."')
    print("Your inference logs cannot answer that. Here is what can.\n")

    led = Ledger()

    # 1) The decision — captured as authority + rationale + action, not tokens.
    d = led.submit(decision(
        record_id="loan-2026-04-19-0098",
        model_version="credit-scorer-3.2.1",
        policy_hash=sha256_hex(b"lending-policy-v7.4-EU"),
        rationale="DTI 0.58 exceeds 0.45 ceiling; thin file; 2 recent delinquencies.",
        action_type="REJECT",
        profile="ODS-Finance/v1",
        action={"score": 0.31, "threshold": 0.50, "decision": "REJECT"},
        actor="credit-scoring-agent@bank.eu",
        compliance={"risk_limit_checks": ["DTI_CEILING", "ADVERSE_ACTION_NOTICE"],
                    "policy_violations": []},
    ))
    print("[1] DECISION recorded")
    print(f"    record_id : {d['record_id']}")
    print(f"    authority : policy_hash {d['identity']['policy_hash'][:16]}… (which rules governed)")
    print(f"    rationale : {d['cognition']['rationale']}")
    print(f"    action    : {d['action']['decision']} (score {d['action']['score']} < {d['action']['threshold']})")
    print(f"    seq #{d['sequence_number']}  record_hash {d['record_hash'][:16]}…  prev {d['prev_hash'][:8]}…")

    # 2) The realized outcome, linked to the decision (append-only).
    o = led.submit(outcome(
        record_id="loan-2026-04-19-0098-outcome",
        parent_id="loan-2026-04-19-0098",
        status="FINAL",
        profile="ODS-Finance/v1",
        applicant_notified=True,
        adverse_action_notice_sent="2026-04-19",
        appeal_filed=False,
    ))
    print("\n[2] OUTCOME recorded (linked to the decision, append-only)")
    print(f"    parent_id : {o['parent_id']}")
    print(f"    seq #{o['sequence_number']}  prev_hash {o['prev_hash'][:16]}… (chained to the decision above)")

    # 3) Anchor everything in a Merkle checkpoint.
    cp = led.merkle_checkpoint()
    print("\n[3] CHECKPOINT — Merkle root over all records (the anchor a regulator keeps)")
    print(f"    tree_size   : {cp['tree_size']}")
    print(f"    merkle_root : {cp['merkle_root']}")

    # 4) Inclusion proof — a third party verifies WITHOUT trusting us.
    proof = led.proof_for(0, cp)
    leaf = bytes.fromhex(led.records[0]["record_hash"])
    ok = verify_inclusion(leaf, 0, cp["tree_size"], proof, cp["merkle_root"])
    print("\n[4] INCLUSION PROOF for the decision record")
    print(f"    audit_path  : {len(proof)} node(s)")
    print(f"    verifies against the checkpoint root: {ok}  <- provable, not asserted")

    # 5) Tamper — the whole point.
    line()
    print("[5] Now someone quietly edits the stored decision: REJECT -> APPROVE")
    led.records[0]["action"]["decision"] = "APPROVE"
    led.records[0]["action"]["score"] = 0.77
    recomputed = record_hash(led.records[0])
    stored = led.records[0]["record_hash"]
    print(f"    stored record_hash    : {stored[:32]}…")
    print(f"    recomputed from bytes : {recomputed[:32]}…")
    print(f"    integrity check       : {'PASS' if recomputed == stored else 'FAIL — tampering detected'}")

    leaf_t = bytes.fromhex(recomputed)
    ok_t = verify_inclusion(leaf_t, 0, cp["tree_size"], proof, cp["merkle_root"])
    print(f"    inclusion proof now   : {'verifies' if ok_t else 'FAILS against the regulator-held root'}")
    line("=")
    print("The edit is mathematically visible. The record is evidence, not a story")
    print("the system tells about itself. That is the gap ODS fills for Article 12.\n")


if __name__ == "__main__":
    demo()
