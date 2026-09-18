inputs = {'你前方初始数量': 100, '观测撤单': 40, '前端撤单后前方': 60, '后端撤单后前方': 100}
steps = ['观察价位总量减少 40', '构造撤在你前方的相容历史', '构造撤在你后方的相容历史', '比较后续成交所需市场单量']
normal = '同一聚合轨迹不能唯一决定你的成交，因此应报告区间或敏感性。'
boundary = '没有真实交易、费用、延迟或市场冲击，不是执行建议。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
