inputs = {'自动化前劳动收入': 60, '自动化前资本收入': 40, '自动化后劳动收入': 10, '自动化后资本收入': 90}
steps = ['比较两期要素份额', '识别自动化后的稀缺收益来源', '工资端税基缩小', '资本收益或所有权工具直接触达主要份额']
normal = '政策工具的着力点应跟随收入来源，而不是沿用旧结构。'
boundary = '这不是未来预测或福利模型，只演示论文假设下的分配直觉。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
