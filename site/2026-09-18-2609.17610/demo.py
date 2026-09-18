from math import isclose

concentrated = [0.95, 0.02, 0.02, 0.01]
balanced = [0.25, 0.25, 0.25, 0.25]

def effective_count(shares):
    assert isclose(sum(shares), 1.0)
    return 1 / sum(share * share for share in shares)

print(f"原始类别数：{len(concentrated)}")
print(f"95%集中分布的有效类别数：{effective_count(concentrated):.2f}")
print(f"四类均衡分布的有效类别数：{effective_count(balanced):.2f}")
print("含义：同样都是四个标签，频率高度集中时更像一个主导类别。")
assert effective_count(concentrated) < 1.2
assert effective_count(balanced) == 4
print("边界：有效数量只概括频率集中度，不测成交、流动性、独立信息或经济价值。")
