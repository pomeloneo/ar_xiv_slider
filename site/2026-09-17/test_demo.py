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
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(Path(__file__).with_name("demo.py")), *arguments],
            capture_output=True, text=True, check=False,
        )

    def test_default_starts_with_weather_story_and_shows_day_allocation(self) -> None:
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("晴 / 阴 / 小雨 / 大雨", result.stdout)
        self.assertIn("A 站原来平均等待：3 分钟", result.stdout)
        self.assertIn("B 站原来平均等待：3.25 分钟", result.stdout)
        self.assertIn("假想未来 8 天，每种天气最多 4 天", result.stdout)
        self.assertIn("晴 4 天 + 阴 0 天 + 小雨 0 天 + 大雨 4 天", result.stdout)
        self.assertIn("A 站最慢平均：5 分钟", result.stdout)
        self.assertIn("B 站最慢平均：3.5 分钟", result.stdout)
        self.assertLess(result.stdout.index("公交"), result.stdout.index("CVaR"))
        self.assertIn("不是实际公交记录", result.stdout)
        self.assertIn("停运", result.stdout)

    def test_days_cap_preserves_verified_results(self) -> None:
        for cap, wait_a, wait_b in ((2, "3", "3.25"), (3, "4", "3.375"),
                                    (4, "5", "3.5"), (8, "9", "4")):
            with self.subTest(cap=cap):
                result = self.run_cli("--days-cap", str(cap))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"A 站最慢平均：{wait_a} 分钟", result.stdout)
                self.assertIn(f"B 站最慢平均：{wait_b} 分钟", result.stdout)

    def test_days_cap_and_lambda_are_compatible_but_mutually_exclusive(self) -> None:
        by_days = self.run_cli("--days-cap", "3")
        by_lambda = self.run_cli("--lambda", "1.5")
        self.assertEqual(by_days.returncode, 0, by_days.stderr)
        self.assertEqual(by_lambda.returncode, 0, by_lambda.stderr)
        self.assertEqual(by_days.stdout, by_lambda.stdout)
        result = self.run_cli("--days-cap", "4", "--lambda", "2")
        self.assertEqual(result.returncode, 2)

    def test_invalid_days_caps_are_rejected(self) -> None:
        for cap in ("1", "9", "2.5", "nan", "four"):
            with self.subTest(cap=cap):
                self.assertEqual(self.run_cli("--days-cap", cap).returncode, 2)

    def test_non_half_integer_lambda_does_not_round_into_an_eight_day_schedule(self) -> None:
        result = self.run_cli("--lambda", "1.25")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("不保证对应 8 天的整数安排", result.stdout)
        self.assertIn("不作四舍五入", result.stdout)
        self.assertIn("晴 5/16", result.stdout)
        self.assertIn("大雨 5/16", result.stdout)
        self.assertNotIn("A 站最慢安排：", result.stdout)
        self.assertIn("A 站最慢平均：3.5 分钟", result.stdout)

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
