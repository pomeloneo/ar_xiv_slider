inputs = {'甲': ['A', 'B', 'C'], '乙中等重合': ['B', 'C', 'D'], '乙完全重合': ['A', 'B', 'C']}
steps = ['找共享概念', '找各自独有概念', '检查合并后新路径', '比较共同语言和互补性']
normal = 'B、C 的共享让 A 与 D 可接通，同时仍保留互补知识。'
boundary = '集合例没有网络权重、搜索行为或真实创新绩效。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
