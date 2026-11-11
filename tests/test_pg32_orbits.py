import unittest
from scripts.pg32_orbits import act, gl4_columns, independent_four, orbit, rank


class OrbitTests(unittest.TestCase):
    def test_exact_orbit_stabilizers(self):
        self.assertEqual(sum(1 for _ in gl4_columns()), 20160)
        for seed, expected in [((1, 2, 4, 8), (840, 24)),
                               ((1, 2, 4, 8, 15), (168, 120))]:
            images, stabilizer = orbit(seed)
            self.assertEqual((len(images), stabilizer), expected)
            self.assertTrue(all(independent_four(p) for p in images))

    def test_singular_and_dependent_controls(self):
        self.assertEqual(rank((1, 2, 4, 7)), 3)
        self.assertFalse(independent_four((1, 2, 4, 7)))
        self.assertEqual(rank(act((1, 2, 4, 7), v) for v in (1, 2, 4, 8)), 3)


if __name__ == '__main__':
    unittest.main()
