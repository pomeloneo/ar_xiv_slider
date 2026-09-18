returns = {"先进国": 1.18, "追赶国": 1.30, "连接国": 1.22}
distance = {"先进国": 0.10, "追赶国": 0.65, "连接国": 0.30}

def flows(friction):
    score = {name: ret / (1 + friction * distance[name]) for name, ret in returns.items()}
    total = sum(score.values())
    return {name: 100 * value / total for name, value in score.items()}

for label, friction in [("低摩擦", 0.2), ("中摩擦", 1.0), ("高摩擦", 3.0)]:
    allocation = flows(friction)
    print(label + "：" + "，".join(f"{k} {v:.1f}" for k, v in allocation.items()))
low, high = flows(0.2), flows(3.0)
print(f"追赶国份额变化：{low['追赶国']:.1f} → {high['追赶国']:.1f}")
assert high["追赶国"] < low["追赶国"]
print("边界：份额是自造的局部折价算例，不含汇率、企业融资、家庭分布或论文CEV求解。")
