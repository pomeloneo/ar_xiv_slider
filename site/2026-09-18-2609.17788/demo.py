inputs = {'初始价格': 100, '窄区间': '95—105', '宽区间': '80—120', '新价格': 110}
steps = ['窄区间内资本更集中', '价格升至 110', '窄区间已越界停止有效做市', '宽区间仍覆盖但单位资本费份额更低']
normal = '窄区间不是免费增益，它用更高在区间效率交换更高越界与重平衡风险。'
boundary = '未计算真实 AMM 头寸、无常损失、gas、滑点或任何投资回报。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
