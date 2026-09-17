#!/usr/bin/env python3
"""用四张天气卡，比较两个公交站在不利天气安排下的平均等候时间。

卡片上的分钟数完全人为设定，不是实际公交记录，也不是金融收益。
先讲生活故事，最后再对照论文里的“有界重加权”和“上尾 CVaR”。
数学出处：arXiv:2608.23416v2，§4 A3 与 §6 Theorem 6.2。
https://arxiv.org/html/2608.23416v2
只演示这一计算机制，不复现论文金融实验，也不模拟其他公理。
"""

import argparse
from fractions import Fraction
from typing import Iterable


LOSSES = {"A": (1, 1, 1, 9), "B": (3, 3, 3, 4)}
WEATHER = ("晴", "阴", "小雨", "大雨")
STORY_DAYS = 8


def exact_number(value: object) -> Fraction:
    """把输入读成精确的数；布尔值、无穷大等不能当成卡片上的数字。"""
    if isinstance(value, bool):
        raise ValueError("必须输入有限数值，不能输入布尔值")
    try:
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("必须输入有限数值") from exc


def worst_case_loss(
    losses: Iterable[object], recurrence_bound: object
) -> tuple[Fraction, tuple[Fraction, ...]]:
    """找允许范围内最慢的平均等待：先给等待最久的天气多安排天数。

    四卡原来等频时，每张占 1/4；允许增到原比例的 Λ 倍，最多占 Λ/4。
    将比例从较快情景搬向未放满的较慢情景，不会降低平均等待时间。
    相同分钟数按卡片原顺序处理；用分数避免四舍五入破坏比例约束。
    技术写法：最大化 sum(q_i * loss_i)，sum(q)=1，0<=q_i<=Λ/n。
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
    """保留精确分数，同时给常见的小数一个便于阅读的写法。"""
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
    options = parser.add_mutually_exclusive_group()
    options.add_argument(
        "--days-cap", type=int, choices=range(2, 9), metavar="2..8",
        help="假想未来 8 天中，每种天气最多几天；默认 4",
    )
    options.add_argument(
        "--lambda", dest="bound", type=parse_bound,
        help="论文参数：每种天气比例最多增到原来的几倍，有限且 >= 1；与 --days-cap 互斥",
    )
    args = parser.parse_args()
    bound = args.bound if args.bound is not None else Fraction(args.days_cap or 4, 2)
    integral_days = (bound * 2).denominator == 1
    print("先想一个生活问题：A、B 两个公交站，在哪个站等车更稳妥？")
    print("这是虚构的教学故事，不是实际公交记录，也不是论文金融实验复现。")
    print("四张天气卡：晴 / 阴 / 小雨 / 大雨。每种天气下的等候分钟数暂时固定。")
    print("A 站：[1, 1, 1, 9] 分钟；B 站：[3, 3, 3, 4] 分钟。越少越好。")
    print("假想以前四种天气出现得一样多，所以每张卡各占四分之一。")
    for name, waits in LOSSES.items():
        print(f"{name} 站原来平均等待：{float(Fraction(sum(waits), 4)):.6g} 分钟")
    print("这样算，A 更快；但如果以后大雨变多，结论还一样吗？")

    if integral_days:
        cap_days = min(int(bound * 2), STORY_DAYS)
        print(f"\n先说清允许的变化：假想未来 8 天，每种天气最多 {cap_days} 天。")
        print("这不是天气预报，是我们为这道题先定的范围；总共仍须安排满 8 天。")
    else:
        print("\n你输入的是比例上限：每种天气最多占原来比例的 " + str(bound) + " 倍。")
        print("这里的“权重”只是所占比例，不保证对应 8 天的整数安排；不作四舍五入。")
        print("下面保留精确分数，只算比例改变后的平均等待时间。")
    print("做法：先给等待最久的天气放到上限，再给次慢的天气，直到安排完。")
    print("等待时间相同时，按晴、阴、小雨、大雨的原顺序选卡。")

    for name, waits in LOSSES.items():
        average, weights = worst_case_loss(waits, bound)
        print(f"\n来看 {name} 站：")
        if integral_days:
            remaining = STORY_DAYS
            for index in sorted(range(4), key=waits.__getitem__, reverse=True):
                days = weights[index] * STORY_DAYS
                if not days:
                    continue
                assert days.denominator == 1
                remaining -= int(days)
                print(f"  给{WEATHER[index]}安排 {days} 天（每天等 {waits[index]} 分钟），还剩 {remaining} 天。")
            arrangement = " + ".join(
                f"{weather} {weight * STORY_DAYS} 天" for weather, weight in zip(WEATHER, weights)
            )
            print(f"{name} 站最慢安排：{arrangement}")
            terms = " + ".join(f"{weight * STORY_DAYS}×{wait}" for weight, wait in zip(weights, waits))
            print(f"  计算：({terms}) ÷ 8")
        else:
            proportions = "；".join(f"{weather} {weight}" for weather, weight in zip(WEATHER, weights))
            print(f"{name} 站各天气所占比例：{proportions}")
            terms = " + ".join(f"({weight})×{wait}" for weight, wait in zip(weights, waits))
            print(f"  计算：{terms}")
        print(f"{name} 站最慢平均：{float(average):.6g} 分钟")
    print("这比较的是各站在允许范围内最慢的平均等待；不是说未来一定这样下雨。")

    print("\n换个上限再看（仍是假想未来 8 天）：")
    print("每种天气最多几天 | A 最慢平均/分钟 | B 最慢平均/分钟 | 此比较下较快者")
    expected = {
        2: (Fraction(3), Fraction(13, 4)),
        3: (Fraction(4), Fraction(27, 8)),
        4: (Fraction(5), Fraction(7, 2)),
        8: (Fraction(9), Fraction(4)),
    }
    for cap_days, reference in expected.items():
        risk_a = worst_case_loss(LOSSES["A"], Fraction(cap_days, 2))[0]
        risk_b = worst_case_loss(LOSSES["B"], Fraction(cap_days, 2))[0]
        assert (risk_a, risk_b) == reference
        winner = "A" if risk_a < risk_b else "B" if risk_b < risk_a else "持平"
        print(f"{cap_days} | {float(risk_a):.6g} | {float(risk_b):.6g} | {winner}")

    print("\n什么时候这套算法管不了？")
    print("假如出现卡片里没有的停运情景，等到 20 分钟才换乘离开。")
    print("旧卡里 A 最久只等 9 分钟，怎样多抽旧卡都造不出新卡上的 20 分钟。")
    print("所以这个结果只管得到已写进卡片的情景，并且假设同一张卡的等待时间不变。")
    print("故事中的天气卡不是论文里的真实市场状态；这些分钟数也不是金融收益。")

    print("\n【想对照论文时再看】")
    print("“权重”就是每种情景所占的比例；改变这些比例，叫“重加权”。")
    print(f"论文用 Λ 表示比例最多增到原来的几倍；本次 Λ={bound}。")
    print("每种天气原占 1/4，所以新比例最多 Λ/4；8 天写法的上限天数=2×Λ。")
    print("“上尾”指等待较久的一端；CVaR 是把这一端取一定比例后求平均。")
    print("在四卡等频的题里，上述最慢平均等于最差 1/Λ 比例的平均，边界卡可只取一部分。")
    print("数学出处：arXiv:2608.23416v2 §4 A3、§6 定理 6.2。只验证这个计算，不复现论文实证。")


if __name__ == "__main__":
    main()
