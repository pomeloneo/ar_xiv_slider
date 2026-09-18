headers = {
    ("亚洲", "2025"): 51.5,
    ("亚洲", "2026"): 57.0,
    ("欧洲", "2025"): 48.0,
    ("欧洲", "2026"): 49.5,
}
bare_chunks = [str(value) for value in headers.values()]
role_chunks = [
    f"指标=收入；地区={region}；年份={year}；值={value}"
    for (region, year), value in headers.items()
]
question = ("亚洲", "2025")
answer = headers[question]
print("裸值块：" + " | ".join(bare_chunks))
print("结构块：" + role_chunks[0])
print(f"问题：亚洲 2025 年收入？答案：{answer}")
assert answer == 51.5
print("中间状态：一级表头=亚洲，二级表头=2025，指标=收入，交叉值=51.5")
print("边界：规则已预先知道这张小表的层级；它没有解决合并单元格、多表混排或任意角色学习。")
