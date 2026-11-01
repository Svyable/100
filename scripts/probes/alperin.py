"""M048 - Alperin's weight conjecture on named groups of small order.

For each listed finite group G and each prime p dividing |G|, the probe
compares two independently computed integers:

* the number of simple FG-modules over an algebraically closed field of
  characteristic p, recovered as the number of p-regular conjugacy classes;
* the number of G-conjugacy classes of Alperin weights, recovered by summing,
  over conjugacy-class representatives of radical p-subgroups Q, the number of
  ordinary irreducible characters of N_G(Q)/Q of p-defect zero.

Both numbers are classical for these groups; a mismatch inside this range
would be a bug, not a new counterexample. The checker rebuilds every group
from its name, recomputes p-regular classes, radical subgroups and character
degrees by a second pass, and rejects any certificate that drifts.
"""
from .core import digest, require
from . import groups

PROBE = {
    "id": "alperin",
    "problem_id": "M048",
    "title": "Alperin weight counts on named groups of small order",
    "engines": ["group_characters"],
    "frontier": (
        "Known: Alperin's weight conjecture has been verified computationally for "
        "all groups of order at most 100 over prime fields (Revista Colombiana de "
        "Matemáticas 41 (2007)), and for many larger simple groups. The cases here "
        "are classical reproductions only."
    ),
    "levels": {
        "smoke": {
            "groups": ["C2", "C3", "C4", "C2xC2", "S3", "D8", "Q8", "A4", "D10"],
        },
        "deep": {
            "groups": [
                "C2", "C3", "C4", "C5", "C6", "C2xC2", "S3", "D8", "Q8",
                "A4", "D10", "D12", "S4", "A5",
            ],
        },
    },
}


def scope(params):
    names = ", ".join(params["groups"])
    return (
        f"For each named group G in {{{names}}} and every prime p dividing |G|, "
        f"the number of conjugacy classes of Alperin p-weights equals the number "
        f"of p-regular conjugacy classes."
    )


def _primes(n):
    out, p, m = [], 2, n
    while p * p <= m:
        if m % p == 0:
            out.append(p)
            while m % p == 0:
                m //= p
        p += 1
    if m > 1:
        out.append(m)
    return out


def _case(name):
    G = groups.named(name)
    order = len(G)
    cases = []
    for p in _primes(order):
        simples = groups.simple_module_count(G, p)
        weights, details = groups.alperin_weight_count(G, p)
        cases.append({
            "group": name,
            "order": order,
            "p": p,
            "simples": simples,
            "weights": weights,
            "radicals": details,
            "n_classes": len(groups.conjugacy_classes(G)),
            "abelianization": groups.abelianization_order(G),
            "degrees": groups.character_degrees(G),
        })
    return cases


def search(params):
    rows = []
    holds = True
    counter = None
    for name in params["groups"]:
        for row in _case(name):
            rows.append(row)
            if row["simples"] != row["weights"]:
                holds = False
                counter = {
                    "group": name,
                    "p": row["p"],
                    "simples": row["simples"],
                    "weights": row["weights"],
                }
                break
        if not holds:
            break
    summary = {
        "groups": list(params["groups"]),
        "cases": len(rows),
        "matched": sum(1 for r in rows if r["simples"] == r["weights"]),
        "certificate_sha256": digest(rows),
    }
    cert = {"cases": rows}
    if counter:
        cert["counterexample"] = counter
    return {"holds": holds, "summary": summary, "certificate": cert}


def check(params, result):
    require(result["holds"], "an Alperin mismatch inside the named catalog needs independent proof")
    cert = result["certificate"]
    rows = cert["cases"]
    require(isinstance(rows, list) and rows, "certificate has no cases")
    seen = []
    for name in params["groups"]:
        G = groups.named(name)
        require(groups.is_group(G), f"{name}: failed group axioms on replay")
        order = len(G)
        # independent conjugacy / abelianization / degree checks
        classes = groups.conjugacy_classes(G)
        ab = groups.abelianization_order(G)
        degrees = groups.character_degrees(G)
        require(sum(d * d for d in degrees) == order, f"{name}: degree square-sum")
        require(len(degrees) == len(classes), f"{name}: degree count vs classes")
        require(degrees.count(1) == ab, f"{name}: linear character count")
        for p in _primes(order):
            simples = len(groups.p_regular_classes(G, p))
            # rebuild weights without trusting the certificate's radical list
            weights, details = groups.alperin_weight_count(G, p)
            require(simples == weights, f"{name}, p={p}: simples {simples} != weights {weights}")
            # match one certificate row
            matches = [r for r in rows if r["group"] == name and r["p"] == p]
            require(len(matches) == 1, f"{name}, p={p}: expected one certificate row")
            row = matches[0]
            require(row["order"] == order, f"{name}: order drift")
            require(row["simples"] == simples, f"{name}, p={p}: simples drift")
            require(row["weights"] == weights, f"{name}, p={p}: weights drift")
            require(row["n_classes"] == len(classes), f"{name}: class count drift")
            require(row["abelianization"] == ab, f"{name}: abelianization drift")
            require(row["degrees"] == degrees, f"{name}: degree list drift")
            require(len(row["radicals"]) == len(details), f"{name}, p={p}: radical count")
            for a, b in zip(row["radicals"], details):
                require(a["q_order"] == b["q_order"], f"{name}, p={p}: radical order")
                require(a["defect_zero"] == b["defect_zero"], f"{name}, p={p}: defect-zero")
                require(a["h_order"] == b["h_order"], f"{name}, p={p}: quotient order")
            seen.append((name, p))
    expected = []
    for name in params["groups"]:
        for p in _primes(len(groups.named(name))):
            expected.append((name, p))
    require(sorted(seen) == sorted(expected), "certificate cases do not match the named catalog")
    require(result["summary"]["cases"] == len(rows), "summary case count")
    require(result["summary"]["matched"] == len(rows), "summary matched count")
    require(result["summary"]["certificate_sha256"] == digest(rows), "summary hash")
