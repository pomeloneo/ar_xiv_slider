events = [
    ("前言: 修复测试失败", 12, False),
    ("旧日志A:" + "x" * 34, 38, True),
    ("旧日志B:" + "y" * 29, 33, True),
    ("最近: 已定位文件", 12, False),
    ("最近: 准备改动", 11, False),
]
budget = 100
raw = sum(size for _, size, _ in events)
print(f"T0 原始上下文：{raw} 字符，是否溢出={raw > budget}")
managed = []
for text, size, bulky in events:
    if bulky:
        managed.append(("[旧工具输出已省略]", 10))
    else:
        managed.append((text, size))
after_elision = sum(size for _, size in managed)
if after_elision > 85:
    managed[1:3] = [("[较旧事件摘要]", 12)]
after_staged = sum(size for _, size in managed)
print(f"T4 省略后：{after_elision} 字符；分阶段处理后：{after_staged} 字符")
print("保留状态：" + " | ".join(text for text, _ in managed))
assert raw > budget and after_staged <= budget
print("边界：字符变少不证明摘要保留了修复语义，也不复现模型成功率、调用成本或真实上下文计数。")
