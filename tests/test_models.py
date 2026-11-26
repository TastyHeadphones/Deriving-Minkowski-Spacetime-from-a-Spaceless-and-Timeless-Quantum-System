import unittest
from fractions import Fraction
from itertools import combinations, product

from experiments import models
from experiments.run import run


class Models(unittest.TestCase):
    def test_every_small_graph_has_exact_edge_support(self):
        pairs = list(combinations(range(4), 2))
        for mask in product((False, True), repeat=len(pairs)):
            edges = [p for included, p in zip(mask, pairs, strict=True) if included]
            registers = models.endpoint_registers(4, edges)
            for first, second in pairs:
                expected = 2 if (first, second) in edges else 0
                self.assertEqual(models.enumerate_information_bits(registers, first, second), expected)
                self.assertEqual(models.information_bits(registers, first, second), expected)

    def test_distance_and_intervention_are_distinct(self):
        for edges in [[(0, 1), (1, 2)], [(0, 1)]]:
            metric = [models.distances(3, edges, source) for source in range(3)]
            for a, b, c in product(range(3), repeat=3):
                self.assertEqual(metric[a][b], metric[b][a])
                self.assertEqual(metric[a][b] == 0, a == b)
                if metric[a][b] is not None and metric[b][c] is not None:
                    self.assertLessEqual(metric[a][c], metric[a][b] + metric[b][c])
            for n, snapshot in enumerate(models.signal_rounds(3, edges, 0, 3)):
                self.assertEqual(snapshot, [i for i, d in enumerate(metric[0]) if d is not None and d <= n])

    def test_grid_volume_and_spectral_returns(self):
        for d in range(1, 5):
            for r in range(4):
                exact = sum(sum(map(abs, p)) <= r for p in product(range(-r, r + 1), repeat=d))
                self.assertEqual(models.lattice_ball(d, r), exact)
            self.assertEqual(models.product_lazy_return(d, 0), 1)
            self.assertEqual(models.product_lazy_return(d, 1), Fraction(1, 2)**d)

    def test_grid_rounding_bound(self):
        for row in run()["continuum_grid"]:
            self.assertLessEqual(Fraction(row["max_sampled_error"]), Fraction(row["proven_error_bound"]))

    def test_bell_local_choice_does_not_change_remote_marginal(self):
        self.assertEqual(models.bell_remote_marginals(), [[Fraction(1, 2)] * 2] * 2)

    def test_clock_and_conditional_boost(self):
        for zero, one in models.clock_probabilities(8):
            self.assertAlmostEqual(zero + one, 1)
        self.assertEqual(models.clock_probabilities(8)[4], [0, 1])
        for beta in [-0.9, -0.4, 0.0, 0.4, 0.9]:
            t, x = models.boost(2, 1, beta)
            self.assertAlmostEqual(t*t - x*x, 3)

    def test_deterministic_results(self):
        self.assertEqual(run(), run())


if __name__ == "__main__":
    unittest.main()
