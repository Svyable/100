#!/usr/bin/env python3
"""Further sound rooted-pivot symmetry reduction of the CH (18,6) CNF.

See the second structural corollary in research/M074_REGULARITY.md.
This adds only constraints implied by the no-digon/no-triangle 6-regular
hypothetical counterexample, after relabeling within each root-neighbor block.
No UNSAT certificate or full theorem is claimed.
"""
import argparse
from hashlib import sha256
import io
import json
from pathlib import Path

from ch_regularity import RegularCNF


class PivotCNF(RegularCNF):
    def __init__(self):
        super().__init__(fix_root=True)
        self.by_category["pivot_symmetry"] = 0
        # In A = {1..6}, one vertex has only one A-outneighbor (the
        # six-vertex triangle lemma) and thus sends all five arcs into C.
        # Relabel this vertex 1 and its A-outneighbor 2.
        for v in (2, 3, 4, 5, 6, 13, 14, 15, 16, 17):
            self.add("pivot_symmetry", self.arc[1, v]
                     if v == 2 or v >= 13 else -self.arc[1, v])
        # Dually, in B = {7..12}, one vertex has only one B-inneighbor.
        # Relabel it 7, its B-inneighbor 8, and force C -> 7.
        for u in (8, 9, 10, 11, 12, 13, 14, 15, 16, 17):
            self.add("pivot_symmetry", self.arc[u, 7]
                     if u == 8 or u >= 13 else -self.arc[u, 7])
        # For any c in C, 1->c->7, so 7->1 would be a triangle.
        self.add("pivot_symmetry", -self.arc[7, 1])

    def output(self, stream):
        data = io.BytesIO()
        meta = super().output(data)
        encoded = (b"c pivot symmetry: vertex 1 dominates C, C dominates 7\n"
                   + data.getvalue())
        stream.write(encoded)
        meta.update(bytes=len(encoded), sha256=sha256(encoded).hexdigest(),
                    pivot_pinned=True)
        return meta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.output.open("wb") as stream:
        result = PivotCNF().output(stream)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
