import unittest

from analyze_human_model_agreement import (
    cohens_kappa,
    collapse,
    compute_metrics,
    quadratic_weight,
    unweighted_weight,
)


class CollapseTests(unittest.TestCase):
    def test_maps_five_level_to_three_level(self):
        self.assertEqual(collapse(-2), -1)
        self.assertEqual(collapse(-1), -1)
        self.assertEqual(collapse(0), 0)
        self.assertEqual(collapse(1), 1)
        self.assertEqual(collapse(2), 1)


class CohensKappaTests(unittest.TestCase):
    def test_perfect_agreement_is_kappa_one(self):
        pairs = [(-2, -2), (-1, -1), (0, 0), (1, 1), (2, 2)]
        self.assertAlmostEqual(cohens_kappa(pairs, [-2, -1, 0, 1, 2], unweighted_weight), 1.0)
        self.assertAlmostEqual(cohens_kappa(pairs, [-2, -1, 0, 1, 2], quadratic_weight), 1.0)

    def test_matches_hand_computed_n11_constraint_following_figures(self):
        # Reproduces the original (now superseded) N=11 human_model_agreement_summary.json
        # constraint_following block exactly -- this fixture is the regression guard for
        # the kappa/agreement math itself, independent of which files are on disk.
        human = [0, -1, -2, 0, 2, -2, 2, -1, -1, 0, -2]
        model = [-1, -2, -2, -2, -1, -2, 2, -2, 2, -2, -2]
        pairs = list(zip(human, model))
        result = compute_metrics(pairs)
        self.assertEqual(result["n"], 11)
        self.assertAlmostEqual(result["exact_five_level_agreement"], 0.36363636363636365)
        self.assertAlmostEqual(result["directional_agreement"], 0.5454545454545454)
        self.assertAlmostEqual(result["weighted_cohens_kappa_quadratic"], 0.4210526315789472)
        self.assertAlmostEqual(result["collapsed_cohens_kappa"], 0.12698412698412687)
        self.assertAlmostEqual(result["mean_absolute_disagreement"], 1.1818181818181819)


class ComputeMetricsTests(unittest.TestCase):
    def test_directional_agreement_uses_collapsed_buckets(self):
        # both "slightly A" and "clearly A" collapse to the same bucket
        pairs = [(-1, -2), (1, 2), (0, 0)]
        result = compute_metrics(pairs)
        self.assertEqual(result["directional_agreement"], 1.0)
        self.assertLess(result["exact_five_level_agreement"], 1.0)

    def test_severe_disagreement_is_two_step_gap_or_more(self):
        pairs = [(-2, 2), (-2, 1), (-2, 0), (-2, -1), (-2, -2)]
        result = compute_metrics(pairs)
        # gaps: 4, 3, 2, 1, 0 -> only the first two are >= 3
        self.assertEqual(result["severe_disagreement_cases"], 2)


if __name__ == "__main__":
    unittest.main()
