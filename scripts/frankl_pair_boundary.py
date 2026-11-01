#!/usr/bin/env python3
"""Known doubleton theorem and a falsifier of its triple-local extension.

If {a,b} belongs to a finite union-closed family, a or b is abundant.
The 27-set Sarvate–Renaud family shows the analogous triple-local
claim fails. Neither establishes or refutes Frankl's full conjecture.
"""
import argparse
import json
from pathlib import Path


def parse(n, sets):
    if type(n) is not int or n < 2:
        raise ValueError("n must be an integer >= 2")
    if not isinstance(sets, list) or not sets:
        raise ValueError("sets must be a nonempty list")
    masks = set()
    for s in sets:
        if not isinstance(s, list):
            raise ValueError("each set must be a list")
        bits = 0
        for element in s:
            if type(element) is not int or not 0 <= element < n:
                raise ValueError("bad element index")
            if bits & (1 << element):
                raise ValueError("duplicate element")
            bits |= 1 << element
        if bits in masks:
            raise ValueError("duplicate set")
        masks.add(bits)
    return masks


def is_closed_bitwise(masks):
    return all(a | b in masks for a in masks for b in masks)


def is_closed_independent(masks, n):
    objects = {frozenset(i for i in range(n) if mask & (1 << i)) for mask in masks}
    return all(a.union(b) in objects for a in objects for b in objects)


def ensure_closed(n, sets):
    masks = parse(n, sets)
    if not is_closed_bitwise(masks) or not is_closed_independent(masks, n):
        raise ValueError("not union-closed")
    return masks


def frequencies(n, masks):
    return [sum(bool(mask & (1 << i)) for mask in masks) for i in range(n)]


def doubleton_certificate(n, sets, a, b):
    masks = ensure_closed(n, sets)
    if type(a) is not int or type(b) is not int or a == b or not (
        0 <= a < n and 0 <= b < n
    ):
        raise ValueError("distinct pair elements required")
    pair = (1 << a) | (1 << b)
    if pair not in masks:
        raise ValueError("the exact doubleton must belong to the family")
    neither = {mask for mask in masks if not mask & pair}
    both = {mask for mask in masks if mask & pair == pair}
    only_a = {mask for mask in masks if mask & pair == 1 << a}
    only_b = {mask for mask in masks if mask & pair == 1 << b}
    images = {mask | pair for mask in neither}
    if not images <= both or len(images) != len(neither):
        raise AssertionError("the union-closure injection is not sound")
    counts = frequencies(n, masks)
    if counts[a] + counts[b] != len(masks) + len(both) - len(neither):
        raise AssertionError("independent frequency identity disagrees with partition")
    assert len(neither) + len(only_a) + len(only_b) + len(both) == len(masks)
    if 2 * max(counts[a], counts[b]) < len(masks):
        raise AssertionError("doubleton theorem unexpectedly failed")
    return {
        "family_size": len(masks), "pair": [a, b],
        "partition": {"neither": len(neither), "a_only": len(only_a),
                      "b_only": len(only_b), "both": len(both)},
        "injection_size": len(images),
        "frequency_a": counts[a], "frequency_b": counts[b],
        "combined_frequency": counts[a] + counts[b],
        "abundant_element": a if 2 * counts[a] >= len(masks) else b,
        "classification": "known general doubleton theorem, independently checked instance",
    }


def triple_local_falsifier(n, sets, triple):
    masks = ensure_closed(n, sets)
    if (not isinstance(triple, list) or len(triple) != 3 or
            any(type(i) is not int or not 0 <= i < n for i in triple) or
            len(set(triple)) != 3):
        raise ValueError("three distinct element indices required")
    chosen = sum(1 << i for i in triple)
    if chosen not in masks:
        raise ValueError("the exact triple must be a member of the family")
    counts = frequencies(n, masks)
    if not all(2 * counts[i] < len(masks) for i in triple):
        raise ValueError("this family does not falsify triple-local abundance")
    return {
        "family_size": len(masks), "triple": triple,
        "triple_frequencies": [counts[i] for i in triple],
        "max_frequency": max(counts),
        "some_other_element_abundant": any(
            i not in triple and 2 * counts[i] >= len(masks) for i in range(n)),
        "minimum_set_size": min(mask.bit_count() for mask in masks),
        "classification": "counterexample ONLY to triple-local strengthening; not to Frankl",
    }


def replay(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("format") != "svyable.frankl.triple-local.v1":
        raise ValueError("unrecognized certificate format")
    result = triple_local_falsifier(data["n"], data["sets"], data["triple"])
    if (data["n"] != 9 or result["family_size"] != 27 or
            result["triple"] != [0, 1, 2] or
            result["triple_frequencies"] != [13, 13, 13] or
            result["minimum_set_size"] != 3 or
            not result["some_other_element_abundant"]):
        raise ValueError("does not reproduce the cited 27-set boundary example")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path,
                        default=Path("examples/FRANKL_SARVATE_RENAUD.json"))
    parser.add_argument("--doubleton", nargs=2, type=int, metavar=("A", "B"),
                        help="certify a two-element member of a union-closed family")
    args = parser.parse_args()
    try:
        if args.doubleton:
            data = json.loads(args.certificate.read_text(encoding="utf-8"))
            if data.get("format") not in (
                "svyable.frankl.family.v1", "svyable.frankl.triple-local.v1"
            ):
                raise ValueError("unrecognized certificate format")
            result = doubleton_certificate(data["n"], data["sets"], *args.doubleton)
        else:
            result = replay(args.certificate)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
