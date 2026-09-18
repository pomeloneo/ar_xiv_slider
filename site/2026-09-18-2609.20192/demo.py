inputs = {'方案A': 'λ=8,m=0.10', '方案B': 'λ=4,m=0.10', '公式': 'B=(1/λ-m)/(1-m)'}
steps = ['A 缓冲约 0.0278', 'B 缓冲约 0.1667', '缓冲越小越接近追缴', '弱锚时 A 更易反馈放大']
normal = '同一维持保证金下，更高杠杆压缩 margin buffer。'
boundary = '只演示论文控制量，不是实际券商保证金模型或市场风险预测。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
