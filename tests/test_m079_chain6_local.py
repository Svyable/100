"""Independent literal-poset checker for M079 chain-plus-six local sharpness.

No use of the C++ gap-state or factorial-block recurrence.
"""
import math
import pathlib
import random
import re
import shutil
import subprocess
import tempfile
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "m079_chain6_local.cpp"
WITNESS = [(-2, 0), (-3, 0), (0, 3), (-2, 2), (-6, 0), (-2, 4)]


def direct_poset_counts(intervals):
    k = len(intervals)
    left = min(a for a, _ in intervals)
    right = max(b for _, b in intervals)
    m = right - left
    n = m + k
    full = (1 << n) - 1
    pred = [0] * n
    for j in range(1, m):
        pred[j] |= 1 << (j - 1)
    for i, (a, b) in enumerate(intervals):
        x = m + i
        for j in range(m):
            if j + 1 <= a - left:
                pred[x] |= 1 << j
            if j + 1 > b - left:
                pred[j] |= 1 << x

    f = [0] * (1 << n)
    f[0] = 1
    for mask in range(1 << n):
        if not f[mask]:
            continue
        for x in range(n):
            if not (mask >> x & 1) and mask & pred[x] == pred[x]:
                f[mask | 1 << x] += f[mask]
    b = [0] * (1 << n)
    b[full] = 1
    for mask in range(full - 1, -1, -1):
        for x in range(n):
            if not (mask >> x & 1) and mask & pred[x] == pred[x]:
                b[mask] += b[mask | 1 << x]
    assert f[full] == b[0]

    pair = [[0] * n for _ in range(n)]
    for mask in range(1 << n):
        if not f[mask]:
            continue
        for x in range(n):
            if not (mask >> x & 1) and mask & pred[x] == pred[x]:
                weight = f[mask] * b[mask | 1 << x]
                for y in range(n):
                    if x != y and not (mask >> y & 1):
                        pair[x][y] += weight
    E = f[full]
    for x in range(n):
        for y in range(x + 1, n):
            assert pair[x][y] + pair[y][x] == E
    best = max(min(pair[x][y], pair[y][x])
               for x in range(n) for y in range(x + 1, n))
    return E, best


@unittest.skipUnless(shutil.which("g++"), "C++17 compiler required")
class Chain6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.exe = pathlib.Path(cls.temp.name) / "m079_chain6_local"
        subprocess.run(["g++", "-std=c++17", "-O3", str(SOURCE), "-o", str(cls.exe)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_instance(self, intervals, check=False):
        spec = ",".join(f"{a}:{b}" for a, b in intervals)
        cmd = [str(self.exe), "--instance", spec]
        if check:
            cmd.append("--check")
        out = subprocess.run(cmd, text=True, capture_output=True, check=True).stdout
        m = re.search(r"E=(\d+) best=(\d+)/(\d+)", out)
        self.assertIsNotNone(m, out)
        E, best, den = map(int, m.groups())
        self.assertEqual(E, den)
        return E, best

    def test_sharp_witness_direct_poset(self):
        self.assertEqual(self.run_instance(WITNESS, check=True), (60060, 25840))
        self.assertEqual(direct_poset_counts(WITNESS), (60060, 25840))
        self.assertNotEqual(math.prod(b-a+1 for a, b in WITNESS), 60060)

    def test_order_dual(self):
        dual = [(-b, -a) for a, b in WITNESS]
        self.assertEqual(self.run_instance(dual), (60060, 25840))
        self.assertEqual(direct_poset_counts(dual), (60060, 25840))

    def test_outsider_permutations(self):
        for order in [(5, 4, 3, 2, 1, 0), (1, 3, 0, 5, 2, 4), (2, 0, 4, 1, 5, 3)]:
            v = [WITNESS[i] for i in order]
            self.assertEqual(self.run_instance(v), (60060, 25840))

    def test_seeded_direct_poset_crosscheck(self):
        rng = random.Random(51079)
        for _ in range(35):
            v = [(0, rng.randrange(1, 4)), (-rng.randrange(1, 4), 0)]
            for j in range(4):
                a, b = -rng.randrange(4), rng.randrange(4)
                if a == b == 0:
                    b = 1
                v.append((a, b))
            self.assertEqual(self.run_instance(v), direct_poset_counts(v), v)

    def test_reject_invalid_cases(self):
        bad = [
            "-1:0,0:1,-1:1,0:2,-2:0,1:2",
            "-1:0,0:1,-1:1,0:2,-2:0,0:0",
            "-1:0,0:1,-1:1,0:2,-2:0",
            "0:1,0:2,-1:1,-1:2,0:3,-2:1",
        ]
        for spec in bad:
            proc = subprocess.run([str(self.exe), "--instance", spec],
                                  text=True, capture_output=True)
            self.assertNotEqual(proc.returncode, 0, spec)

    def test_smoke_census_and_digest(self):
        p = subprocess.run([str(self.exe), "--max-length", "4", "--check"],
                           text=True, capture_output=True, check=True)
        self.assertIn("count=82", p.stdout)
        self.assertIn("digest=7c4fb13ad7fec712", p.stdout)
        self.assertEqual(math.comb(35, 6) - 2 * math.comb(28, 6) + math.comb(21, 6), 923944)


if __name__ == "__main__":
    unittest.main()
