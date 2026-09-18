from itertools import combinations

edges = {"A": ["B"], "B": ["C", "D"], "C": [], "D": []}
nodes = tuple(edges)

def cascade(rescued):
    failed = {"A"}
    changed = True
    while changed:
        changed = False
        for source, targets in edges.items():
            if source in failed:
                for target in targets:
                    if target not in rescued and target not in failed:
                        failed.add(target)
                        changed = True
    return failed

baseline = cascade(set())
print("不救助：" + "、".join(sorted(baseline)))
results = []
for (node,) in combinations(("B", "C", "D"), 1):
    failed = cascade({node})
    results.append((len(failed), node, failed))
    print(f"救 {node}：失败 " + "、".join(sorted(failed)))
best = min(results)
assert best[1] == "B" and best[0] == 1
print("最小失败方案：救 B，同时间接保护 C、D。")
print("边界：这是确定性布尔传播的精确枚举，不含估值、成本差异、概率、QUBO惩罚或真实金融机构。")
