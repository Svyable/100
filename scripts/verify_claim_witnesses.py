#!/usr/bin/env python3
"""Independent extractability audit for the M071/M073 2026 claim witnesses.

M073: reconstruct the pinned 35-vertex / 66-edge bipartite pattern H from the
OpenAI comparator faces table, verify it two ways, and run exact Sidorenko
checks on every small host already covered by the lab probe. The manuscript's
host G remains existence-only; this script does not invent one.

M071: record that the published Lean comparator only asserts an existential
family of graphs (arbitrarily large m with alpha <= 2). No finite adjacency
list is supplied for a non-Lean checker. Reporting that gap is the audit
result, not acceptance of the claim.

Neither check upgrades claim_needs_review to resolved.
"""
from __future__ import annotations

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from probes.graphs import census, to_adjacency  # noqa: E402
from probes.homomorphisms import bipartite, count_from_side, sidorenko_holds  # noqa: E402

FACES = ROOT / "data/reference/sidorenko_faces.json"
REPORT = ROOT / "data/claim_witness_replay.json"

SOURCE_COMMIT = "4eaee87548250b2682affda7d05d947c05554bae"
SIDORENKO_COMPARATOR_SHA256 = (
    "489688f5c4eb60c6dd8cfe0ef69663aaf11e795d6252e9626972764a50187de9"
)
HADWIGER_COMPARATOR_SHA256 = (
    "83f9f9c49f49d4abc35c8d1b7247ccab5de9c9ef909c45acabc16875e306b898"
)
SCOPE_157_SHA256 = "67c9ebeee4d8afcc735c40f2b9b3e018cd713270dad245777d061db491228fe1"
SCOPE_161_SHA256 = "a1da28a997a9a27cad57f0862cd18e7502aa3129730d3bc7fd7a45fde14d3b1d"


class WitnessError(ValueError):
    pass


def digest(obj) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return sha256(payload).hexdigest()


def load_faces() -> dict:
    data = json.loads(FACES.read_text(encoding="utf-8"))
    if data.get("source_sha256") != SIDORENKO_COMPARATOR_SHA256:
        raise WitnessError("pinned Sidorenko comparator digest drifted")
    if data.get("source_commit") != SOURCE_COMMIT:
        raise WitnessError("Sidorenko faces pin must stay on the claim-review commit")
    faces = [tuple(sorted(face)) for face in data["faces"]]
    if len(faces) != 22:
        raise WitnessError(f"expected 22 faces, got {len(faces)}")
    if any(len(face) != 3 for face in faces):
        raise WitnessError("every face must be a 3-set")
    if len(set(faces)) != 22:
        raise WitnessError("faces must be distinct")
    return data | {"faces_tuples": faces}


def reconstruct_pattern(faces: list[tuple[int, ...]]) -> dict:
    """Path A: incidence edges from the face list."""
    points = sorted({p for face in faces for p in face})
    if points != list(range(13)):
        raise WitnessError(f"points must be exactly Fin 13, got {points}")
    edges = sorted((p, j) for j, face in enumerate(faces) for p in face)
    if len(edges) != 66:
        raise WitnessError(f"expected 66 edges, got {len(edges)}")
    if len(set(edges)) != 66:
        raise WitnessError("incidence edges must be unique")
    H = bipartite(13, 22, edges)
    return {
        "points": points,
        "face_count": len(faces),
        "edges": edges,
        "edge_count": len(edges),
        "pattern": H,
        "point_degrees": [sum(1 for a, _ in edges if a == p) for p in points],
        "face_degrees": [sum(1 for _, b in edges if b == j) for j in range(len(faces))],
    }


def recount_by_degrees(faces: list[tuple[int, ...]]) -> dict:
    """Path B: edge count from point and face degree sums, without building edge pairs."""
    point_deg = [0] * 13
    for face in faces:
        for p in face:
            point_deg[p] += 1
        if len(face) != 3:
            raise WitnessError("face degree recount saw a non-triple")
    face_deg = [3] * len(faces)
    if sum(point_deg) != sum(face_deg):
        raise WitnessError("handshaking lemma failed for the incidence graph")
    return {
        "point_degrees": point_deg,
        "face_degrees": face_deg,
        "edge_count": sum(point_deg),
    }


def pattern_connected(edges: list[tuple[int, int]], a_size: int = 13, b_size: int = 22) -> bool:
    """BFS connectivity of the undirected incidence graph."""
    adj = {("A", i): [] for i in range(a_size)}
    adj.update({("B", j): [] for j in range(b_size)})
    for a, b in edges:
        adj[("A", a)].append(("B", b))
        adj[("B", b)].append(("A", a))
    start = ("A", 0)
    seen = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        for nxt in adj[node]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return len(seen) == a_size + b_size


def sidorenko_tiny_hosts(H: dict, max_host: int = 2) -> dict:
    """Exact Sidorenko checks only on hosts tiny enough for a 35-vertex pattern.

    Enumerating maps of the 13-point side costs n^13. The lab Sidorenko probe
    uses a 10-vertex open case; the claimed 35-vertex H is out of range for the
    same brute-force census. n <= 2 is enough to exercise both homomorphism
    recounts and the inequality on empty and edged hosts without pretending to
    search for the unpublished finite counterexample host.
    """
    if max_host > 2:
        raise WitnessError("tiny-host sanity for this H is capped at n<=2")
    e_h = len(H["edges"])
    v_h = H["A"] + H["B"]
    hosts = []
    holds = True
    for n in range(1, max_host + 1):
        for code in census(n):
            adj = to_adjacency(n, code)
            e_g = sum(bin(row).count("1") for row in adj) // 2
            from_a = count_from_side(H, n, adj, "A")
            from_b = count_from_side(H, n, adj, "B")
            if from_a != from_b:
                raise WitnessError(f"homomorphism recount mismatch on host n={n} code={code}")
            ok = sidorenko_holds(from_a, n, e_g, e_h, v_h)
            holds &= ok
            hosts.append({"n": n, "code": code, "hom": from_a, "edges": e_g, "holds": ok})
    return {
        "max_host": max_host,
        "host_count": len(hosts),
        "holds_on_all_hosts": holds,
        "hosts_digest": digest(hosts),
        "note": (
            "Brute-force host search stops at n=2 because n^13 map enumeration for "
            "the claimed pattern is infeasible; this is an encoding sanity check, "
            "not a search for the missing finite counterexample host."
        ),
    }


def audit_sidorenko() -> dict:
    pin = load_faces()
    faces = pin["faces_tuples"]
    path_a = reconstruct_pattern(faces)
    path_b = recount_by_degrees(faces)
    if path_a["edge_count"] != path_b["edge_count"]:
        raise WitnessError("independent edge counts disagree")
    if path_a["point_degrees"] != path_b["point_degrees"]:
        raise WitnessError("independent point degrees disagree")
    if path_a["face_degrees"] != path_b["face_degrees"]:
        raise WitnessError("independent face degrees disagree")
    if not pattern_connected(path_a["edges"]):
        raise WitnessError("claimed pattern H is disconnected")
    if any(d != 3 for d in path_a["face_degrees"]):
        raise WitnessError("every face must contribute exactly three edges")
    small = sidorenko_tiny_hosts(path_a["pattern"])
    if not small["holds_on_all_hosts"]:
        raise WitnessError(
            "Sidorenko already fails on a tiny host; that would be a finite witness, "
            "but none of the published claims use such a host"
        )
    # Tamper control: flipping one point in the first face must change the digest.
    tampered = [list(face) for face in faces]
    tampered[0][0] = 2 if tampered[0][0] != 2 else 5
    tampered_faces = [tuple(sorted(face)) for face in tampered]
    if digest(tampered_faces) == digest([list(f) for f in faces]):
        raise WitnessError("tamper control failed to change the face digest")
    return {
        "problem_id": "M073",
        "status": "pattern_reconstructed_host_missing",
        "source_commit": SOURCE_COMMIT,
        "comparator_path": "lean/ComparatorChallenges/SidorenkoCounterexample.lean",
        "comparator_sha256": SIDORENKO_COMPARATOR_SHA256,
        "scope_note_sha256": SCOPE_161_SHA256,
        "vertices": 35,
        "edges": 66,
        "bipartite_parts": [13, 22],
        "connected": True,
        "point_degrees": path_a["point_degrees"],
        "face_degrees": path_a["face_degrees"],
        "faces_digest": digest([list(f) for f in faces]),
        "edges_digest": digest(path_a["edges"]),
        "small_host_sanity": small,
        "explicit_host_published": False,
        "gap": (
            "The comparator and RandomHost development prove existence of some finite "
            "simple host G with t(H,G) < t(K2,G)^66 via a random-edge sampling argument. "
            "No explicit adjacency list, graph6 string, or concrete order n is published "
            "for independent non-Lean replay."
        ),
    }


def audit_hadwiger() -> dict:
    return {
        "problem_id": "M071",
        "status": "no_explicit_finite_graph",
        "source_commit": SOURCE_COMMIT,
        "comparator_path": "lean/ComparatorChallenges/HadwigerCounterexample.lean",
        "comparator_sha256": HADWIGER_COMPARATOR_SHA256,
        "scope_note_sha256": SCOPE_157_SHA256,
        "claimed_quantifiers": (
            "For every M there exists m >= max(M,5) and a SimpleGraph on Fin m with "
            "independence number at most 2, connectedMatchingNumber < m/100, "
            "hadwigerNumber < 26m/75 + 2/3 < m/2 <= chromaticNumber."
        ),
        "construction_notes": (
            "The upstream ParameterExistence seed uses birthG = 10^9+1. The formal "
            "development yields an existential/asymptotic family, not a listed finite "
            "adjacency matrix. EdouardBonnet/hadwiger-counterexample reports a local "
            "kernel replay of the vendored construction; that is still Lean proof-object "
            "checking, not an independent finite-graph certificate."
        ),
        "explicit_graph_published": False,
        "explicit_hadwiger_number_published": False,
        "gap": (
            "No finite graph G with an independently checkable adjacency list, chromatic "
            "lower bound certificate, and clique-minor upper bound certificate is "
            "available outside the Lean development. Comparator acceptance alone cannot "
            "discharge the repository's witness-replay gate."
        ),
    }


def build_report() -> dict:
    sidorenko = audit_sidorenko()
    hadwiger = audit_hadwiger()
    body = {
        "schema_version": 1,
        "audited_on": "2026-10-31",
        "issue_url": "https://github.com/Svyable/100/issues/13",
        "interpretation": (
            "Finite-witness extractability audit for the top dispatch-queue claim "
            "replays. Reconstructing H or recording a missing explicit G/graph is not "
            "independent acceptance of either 2026 manuscript."
        ),
        "source_revision": {
            "repository": "openai/math",
            "commit": SOURCE_COMMIT,
        },
        "reviews": [hadwiger, sidorenko],
    }
    body["report_sha256"] = digest({k: v for k, v in body.items() if k != "report_sha256"})
    return body


def write_report(path: Path = REPORT) -> dict:
    report = build_report()
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def check_report(path: Path = REPORT) -> dict:
    if not path.is_file():
        raise WitnessError(f"missing frozen report {path}")
    frozen = json.loads(path.read_text(encoding="utf-8"))
    fresh = build_report()
    # Compare without depending on key order of the stored file.
    frozen_hash = frozen.get("report_sha256")
    expected = digest({k: v for k, v in frozen.items() if k != "report_sha256"})
    if frozen_hash != expected:
        raise WitnessError("stored report_sha256 does not match stored body")
    if frozen != fresh:
        raise WitnessError("claim-witness report drifted from recomputation")
    return frozen


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="rewrite the frozen JSON report")
    parser.add_argument("--check", action="store_true", help="recompute and compare to the frozen report")
    args = parser.parse_args(argv)
    if args.emit:
        report = write_report()
        print(json.dumps({"wrote": str(REPORT), "report_sha256": report["report_sha256"]}, indent=2))
        return 0
    if args.check:
        report = check_report()
        print(json.dumps({
            "ok": True,
            "report_sha256": report["report_sha256"],
            "m071": report["reviews"][0]["status"],
            "m073": report["reviews"][1]["status"],
        }, indent=2))
        return 0
    report = build_report()
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except WitnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
