inputs = {'投资成本': 100, '封闭时可保留': 30, '迁移时可保留': 80, '额外生态价值': 40}
steps = ['开发者比较私有回报与成本', '封闭时投资不足', '迁移提高退出价值', '平台再扣除验证与真实泄漏成本']
normal = '可迁移可诱导更多投资，但是否应完全开放取决于治理成本。'
boundary = '数字不来自平台数据，没有计算任何真实产品的最优权限或迁移方案。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
