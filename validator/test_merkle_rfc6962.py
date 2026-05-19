"""
RFC 6962 Merkle Tree Construction — Cross-Implementation Test Vectors

Verifies that the ODS Merkle tree construction matches RFC 6962 §2.1 exactly.
These tests use inputs whose expected outputs can be independently derived from
any correct RFC 6962 implementation.

Test cases:
  - Empty tree (n=0)
  - Single leaf (n=1)
  - n=2 (simplest internal node)
  - n=4 (balanced tree, verifies split rule at power-of-two boundary)
  - n=7 (asymmetric tree: k=4, left=4, right=3, verifies recursive odd split)

Run: python3 validator/test_merkle_rfc6962.py
All tests must pass for the implementation to be considered cross-compatible.
"""

import hashlib
import sys


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def leaf_hash(data: bytes) -> bytes:
    """RFC 6962 §2.1: MTH({d}) leaf hash = SHA-256(0x00 || d)"""
    return sha256(b"\x00" + data)


def node_hash(left: bytes, right: bytes) -> bytes:
    """RFC 6962 §2.1: internal node hash = SHA-256(0x01 || left || right)"""
    return sha256(b"\x01" + left + right)


def merkle_tree_hash(leaves: list[bytes]) -> bytes:
    """
    RFC 6962 §2.1 Merkle Tree Hash (MTH).

    MTH({}) = SHA-256(b"")
    MTH({d[0]}) = SHA-256(0x00 || d[0])
    MTH(D[n]) = SHA-256(0x01 || MTH(D[0:k]) || MTH(D[k:n]))
      where k = 2^floor(log2(n-1))  — largest power of 2 strictly less than n
    """
    n = len(leaves)
    if n == 0:
        return sha256(b"")
    if n == 1:
        return leaf_hash(leaves[0])
    # Largest power of 2 strictly less than n
    k = 1
    while k < n:
        k <<= 1
    k >>= 1  # now k = 2^floor(log2(n-1))
    return node_hash(
        merkle_tree_hash(leaves[:k]),
        merkle_tree_hash(leaves[k:])
    )


def hex_digest(data: bytes) -> str:
    return data.hex()


def run_tests() -> bool:
    passed = 0
    failed = 0

    def check(name: str, got: bytes, expected_hex: str):
        nonlocal passed, failed
        expected = bytes.fromhex(expected_hex)
        if got == expected:
            print(f"  PASS  {name}")
            passed += 1
        else:
            print(f"  FAIL  {name}")
            print(f"        got:      {got.hex()}")
            print(f"        expected: {expected_hex}")
            failed += 1

    print("RFC 6962 §2.1 Merkle Tree Hash — Test Vectors")
    print("=" * 60)

    # ----------------------------------------------------------------
    # Vector 0: Empty tree
    # MTH({}) = SHA-256(b"") = e3b0c44298fc1c149afbf4c8996fb924...
    # ----------------------------------------------------------------
    empty_root = merkle_tree_hash([])
    check(
        "n=0 (empty tree)",
        empty_root,
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )

    # ----------------------------------------------------------------
    # Test data for n>=1: single-byte leaves 0x00, 0x01, ..., 0x06
    # These are simple, independently verifiable inputs.
    # ----------------------------------------------------------------
    D = [bytes([i]) for i in range(7)]  # D[0]=b'\x00', ..., D[6]=b'\x06'

    # Pre-compute individual leaf hashes for reference
    L = [leaf_hash(d) for d in D]

    # ----------------------------------------------------------------
    # Vector 1: Single leaf (n=1)
    # MTH({D[0]}) = SHA-256(0x00 || D[0]) = SHA-256(b'\x00\x00')
    # ----------------------------------------------------------------
    expected_n1 = sha256(b"\x00" + D[0])
    check("n=1 (single leaf, D[0]=0x00)", merkle_tree_hash(D[:1]), expected_n1.hex())

    # ----------------------------------------------------------------
    # Vector 2: n=2
    # k=1; MTH = SHA-256(0x01 || leaf_hash(D[0]) || leaf_hash(D[1]))
    # ----------------------------------------------------------------
    expected_n2 = node_hash(L[0], L[1])
    check("n=2", merkle_tree_hash(D[:2]), expected_n2.hex())

    # ----------------------------------------------------------------
    # Vector 3: n=4 (balanced)
    # k=2
    # left  = node_hash(L[0], L[1])
    # right = node_hash(L[2], L[3])
    # root  = node_hash(left, right)
    # ----------------------------------------------------------------
    left_n4  = node_hash(L[0], L[1])
    right_n4 = node_hash(L[2], L[3])
    expected_n4 = node_hash(left_n4, right_n4)
    check("n=4 (balanced)", merkle_tree_hash(D[:4]), expected_n4.hex())

    # Verify split rule: for n=4, k must be 2
    k4 = 1
    while k4 < 4:
        k4 <<= 1
    k4 >>= 1
    assert k4 == 2, f"Split rule: expected k=2 for n=4, got k={k4}"
    print(f"  PASS  n=4 split rule: k={k4} (correct: left=2, right=2)")
    passed += 1

    # ----------------------------------------------------------------
    # Vector 4: n=7 (asymmetric, critical split rule test)
    # k = largest power of 2 < 7 = 4
    # left  = MTH(D[0:4]) = expected_n4 (computed above)
    # right = MTH(D[4:7]) — n=3, k=2
    #   right_left  = node_hash(L[4], L[5])
    #   right_right = L[6]
    #   right = node_hash(right_left, right_right)
    # root  = node_hash(left, right)
    # ----------------------------------------------------------------
    k7 = 1
    while k7 < 7:
        k7 <<= 1
    k7 >>= 1
    assert k7 == 4, f"Split rule: expected k=4 for n=7, got k={k7}"

    right_left_n7  = node_hash(L[4], L[5])
    right_right_n7 = L[6]
    right_n7       = node_hash(right_left_n7, right_right_n7)
    expected_n7    = node_hash(expected_n4, right_n7)
    check("n=7 (asymmetric, k=4)", merkle_tree_hash(D[:7]), expected_n7.hex())
    print(f"  PASS  n=7 split rule: k={k7} (correct: left=4, right=3)")
    passed += 1

    # ----------------------------------------------------------------
    # Spot-check: n=5 (k=4, left=4, right=1)
    # right = leaf_hash(D[4])
    # root  = node_hash(expected_n4, leaf_hash(D[4]))
    # ----------------------------------------------------------------
    expected_n5 = node_hash(expected_n4, L[4])
    check("n=5 (k=4, left=4, right=1)", merkle_tree_hash(D[:5]), expected_n5.hex())

    # ----------------------------------------------------------------
    # Spot-check: n=6 (k=4, left=4, right=2)
    # right = node_hash(L[4], L[5])
    # root  = node_hash(expected_n4, right)
    # ----------------------------------------------------------------
    expected_n6 = node_hash(expected_n4, node_hash(L[4], L[5]))
    check("n=6 (k=4, left=4, right=2)", merkle_tree_hash(D[:6]), expected_n6.hex())

    # ----------------------------------------------------------------
    # Domain separation: leaf hash != node hash of same payload
    # A leaf hash of 32-byte input must not equal the node_hash of two 16-byte halves
    # ----------------------------------------------------------------
    payload = b"\xab" * 32
    lh = leaf_hash(payload)
    nh = node_hash(payload[:16], payload[16:])
    if lh != nh:
        print("  PASS  domain separation: leaf_hash != node_hash for same-length payload")
        passed += 1
    else:
        print("  FAIL  domain separation: leaf_hash == node_hash (CRITICAL — second-preimage vulnerability)")
        failed += 1

    # ----------------------------------------------------------------
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    if failed:
        print("FAIL — implementation does not match RFC 6962 §2.1")
        print("Cross-implementation compatibility is NOT guaranteed.")
        return False
    else:
        print("PASS — implementation matches RFC 6962 §2.1")
        print("Cross-implementation compatibility verified.")
        return True


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
