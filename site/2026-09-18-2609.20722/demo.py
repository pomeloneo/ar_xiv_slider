inputs = {'候选层': [6, 10, 14], '候选强度': [0.5, 1.0, 1.5], '选择指标': '准确率增益与攻击风险'}
steps = ['用中间预测找收敛区域', '用干预筛选因果头', '比较不同强度收益', '在风险过高前停止']
normal = '选择能提升目标且未越过风险阈值的配置，而不是最大强度。'
boundary = '没有加载 Transformer 或复现论文准确率；数值只演示多目标选择。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
