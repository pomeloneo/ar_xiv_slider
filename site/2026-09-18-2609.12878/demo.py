inputs = {'事件A子合约数': 100, '事件A平均回报': -0.06, '事件B子合约数': 2, '事件B平均回报': 0.1}
steps = ['按 102 个子合约加权', 'A 因子合约多占绝大权重', '再让 A、B 两事件各占一半', '比较两个平均值的符号']
normal = '同一底层结果可在两种合理统计单位下出现不同总体结论。'
boundary = '教学数字不是 Polymarket 原始交易重算，也不构成下注或投资建议。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
