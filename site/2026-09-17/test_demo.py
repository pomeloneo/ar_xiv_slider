"""Independent vertex enumeration checks for the educational linear program."""

import itertools
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import unittest

from demo import LOSSES, worst_case_loss


def vertex_objectives(losses: tuple[int, ...], bound: Fraction) -> list[Fraction]:
    """Enumerate LP vertices: all but one coordinate must be at a bound.

    This enumerates boundary combinations; it neither orders losses nor uses
    the implementation's greedy allocation. Duplicate vertices are harmless.
    """
    size = len(losses)
    cap = bound / size
    objectives = []
    for free_index in range(size):
        fixed_indices = [index for index in range(size) if index != free_index]
        for endpoints in itertools.product((Fraction(0), cap), repeat=size - 1):
            remainder = 1 - sum(endpoints)
            if not 0 <= remainder <= cap:
                continue
            weights = [Fraction(0)] * size
            weights[free_index] = remainder
            for index, endpoint in zip(fixed_indices, endpoints):
                weights[index] = endpoint
            objectives.append(sum(weight * loss for weight, loss in zip(weights, losses)))
    return objectives


class WorstCaseLossTests(unittest.TestCase):
    def test_matches_independent_vertex_optimum(self) -> None:
        cases = (*LOSSES.values(), (-5, 2, 7, -1), (4, 4, 4, 4))
        for bound in map(Fraction, ("1", "1.5", "2", "3", "4")):
            for losses in cases:
                with self.subTest(bound=bound, losses=losses):
                    objective, weights = worst_case_loss(losses, bound)
                    self.assertEqual(objective, max(vertex_objectives(losses, bound)))
                    self.assertEqual(sum(weights), 1)
                    self.assertTrue(all(0 <= weight <= bound / 4 for weight in weights))

    def test_mean_and_max_boundaries(self) -> None:
        for losses in LOSSES.values():
            with self.subTest(losses=losses):
                self.assertEqual(worst_case_loss(losses, 1)[0], Fraction(sum(losses), 4))
                self.assertEqual(worst_case_loss(losses, 4)[0], max(losses))
                self.assertEqual(worst_case_loss(losses, 10)[0], max(losses))

    def test_fractional_tail_cut(self) -> None:
        self.assertEqual(worst_case_loss(LOSSES["A"], "1.5")[0], 4)
        self.assertEqual(worst_case_loss(LOSSES["B"], "1.5")[0], Fraction(27, 8))

    def test_equal_losses_have_stable_weights(self) -> None:
        self.assertEqual(
            worst_case_loss((4, 4, 4, 4), 2)[1],
            (Fraction(1, 2), Fraction(1, 2), Fraction(0), Fraction(0)),
        )

    def test_invalid_bounds(self) -> None:
        for bound in (0, -1, "0.99", "nan", "inf", "-inf", "1/0", "", None, True):
            with self.subTest(bound=bound), self.assertRaises(ValueError):
                worst_case_loss(LOSSES["A"], bound)

    def test_invalid_losses(self) -> None:
        for losses in ((), (1, "nan"), (float("inf"),), (True,), (None,)):
            with self.subTest(losses=losses), self.assertRaises(ValueError):
                worst_case_loss(losses, 2)

    def test_single_block(self) -> None:
        self.assertEqual(worst_case_loss((7,), 2), (7, (1,)))

    def test_cli_invalid_argument_is_rejected(self) -> None:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("demo.py")), "--lambda", "nan"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("有限数值", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
