inputs = {'训练允许组合': ['00', '11'], '独立乘积组合': ['00', '01', '10', '11'], '各边缘': '0/1 各 50%'}
steps = ['检查位置一的边缘为 50/50', '检查位置二的边缘也为 50/50', '独立相乘产生四种组合', '01 与 10 违反训练支持集']
normal = '逐个条件采样能保留两位置相同的约束，并行独立采样不能。'
boundary = '这是二位分布算例，不是论文的 ScanAndAdd 模型训练或真实扩散系统测试。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
