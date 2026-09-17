#!/usr/bin/env python3
"""有限历史块上的教学算例：有界重加权 = 上尾 CVaR。

出处：arXiv:2608.23416v2，§4 A3 与 §6 Theorem 6.2。
https://arxiv.org/html/2608.23416v2
这是人工构造的无量纲损失，不是收益率，也不复现论文市场实验。
只实现等权历史块上的有限线性规划，不模拟论文的其他公理。
"""

import argparse
from fractions import Fraction
from typing import Iterable


LOSSES = {"A": (1, 1, 1, 9), "B": (3, 3, 3, 4)}


def exact_number(value: object) -> Fraction:
    """Read finite numbers exactly; reject Boolean and nonnumeric inputs."""
    if isinstance(value, bool):
        raise ValueError("必须输入有限数值，不能输入布尔值")
    try:
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("必须输入有限数值") from exc


def worst_case_loss(
    losses: Iterable[object], recurrence_bound: object
) -> tuple[Fraction, tuple[Fraction, ...]]:
    """Maximize sum(q_i * loss_i), subject to sum(q)=1 and 0<=q_i<=Λ/n.

    Historical weights are 1/n. Thus q_i/(1/n)<=Λ is the finite analogue
    of the bounded density ratio. Fill the largest losses first; an exchange
    from any smaller loss to an unfilled larger one cannot lower the objective.
    Equal losses retain their original order. Fractions avoid rounding leakage.
    """
    values = tuple(exact_number(loss) for loss in losses)
    bound = exact_number(recurrence_bound)
    if not values:
        raise ValueError("至少需要一个历史块")
    if bound < 1:
        raise ValueError("Lambda 必须有限且 >= 1，否则权重约束不可行")

    cap = bound / len(values)
    weights = [Fraction(0) for _ in values]
    remaining = Fraction(1)
    for index in sorted(range(len(values)), key=values.__getitem__, reverse=True):
        weight = min(cap, remaining)
        weights[index] = weight
        remaining -= weight
        if remaining == 0:
            break
    assert remaining == 0
    assert sum(weights) == 1 and all(0 <= weight <= cap for weight in weights)
    return sum(weight * loss for weight, loss in zip(weights, values)), tuple(weights)


def show(value: Fraction) -> str:
    """Show exact fraction plus a short decimal for nonintegral numbers."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value} ({float(value):.6g})"


def parse_bound(value: str) -> Fraction:
    try:
        bound = exact_number(value)
        if bound < 1:
            raise ValueError("Lambda 必须有限且 >= 1")
        return bound
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lambda", dest="bound", type=parse_bound, default=Fraction(2),
        help="显示详细权重的 Λ，有限且 >= 1；默认 2，支持 1.5 或 3/2",
    )
    args = parser.parse_args()
    print("教学模拟｜有限历史块 CVaR；不是论文实验复现，也不是交易建议。")
    print("输入：A=[1, 1, 1, 9]；B=[3, 3, 3, 4]。单位：损失点，越低越好。")
    print("历史各块权重=1/4；未来权重 q_i>=0，sum(q_i)=1，q_i<=Λ/4。")
    print("机制：按损失从高到低分配权重，每块最多 Λ/4，直到总量为 1。")
    print("这等于最差 1/Λ 历史概率质量的平均损失（允许切分边界块）。")
    print("\nΛ | A 最坏期望损失 | B 最坏期望损失 | 此准则更优者")
    expected = {
        Fraction(1): (Fraction(3), Fraction(13, 4)),
        Fraction(3, 2): (Fraction(4), Fraction(27, 8)),
        Fraction(2): (Fraction(5), Fraction(7, 2)),
        Fraction(4): (Fraction(9), Fraction(4)),
    }
    for bound, reference in expected.items():
        risk_a = worst_case_loss(LOSSES["A"], bound)[0]
        risk_b = worst_case_loss(LOSSES["B"], bound)[0]
        assert (risk_a, risk_b) == reference
        winner = "A" if risk_a < risk_b else "B" if risk_b < risk_a else "持平"
        print(f"{show(bound)} | {show(risk_a)} | {show(risk_b)} | {winner}")

    print(f"\n详细中间状态：Λ={show(args.bound)}，单块权重上限={show(args.bound / 4)}")
    for name, losses in LOSSES.items():
        risk, weights = worst_case_loss(losses, args.bound)
        print(f"{name}：原块顺序权重=[{', '.join(str(weight) for weight in weights)}]")
        terms = " + ".join(f"({weight})×{loss}" for weight, loss in zip(weights, losses))
        print(f"   最坏期望损失 = {terms} = {show(risk)}")

    print("\n边界例：若未来全落到未见过的损失 20，历史 A 最大损失只有 9。")
    print("新状态的历史概率为 0，任何有限 Λ 的历史重加权都无法给它正概率。")
    print("这违反本算例的覆盖假设；表中的最坏值不能约束这个未来。")
    print("算例只验证给定 Λ 和历史块的计算；没有证明真实未来符合这些假设。")


if __name__ == "__main__":
    main()
