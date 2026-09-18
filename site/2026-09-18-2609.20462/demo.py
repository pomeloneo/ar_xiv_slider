inputs = {'合规': 8, '质量': 3, '速度': -7, '体验': -2}
steps = ['计算总绝对幅度20', '计算净效果2', '努力翻倍会同步放大正负影响', '把速度损失降为-2后再看净效果']
normal = '先改冲突结构可能比按原结构加倍执行更有效。'
boundary = '各目标被粗略放在同一尺度，只演示论文逻辑，不能作为真实组织评分。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
