inputs = {'方法A': '1小时/材料，误差约5%', '方法B': '10万小时/材料，设置敏感', '目标': '筛选10万种材料'}
steps = ['检查方法能否计算目标性质', '比较成本是否可扩展', '检查误差和协议稳定性', '用精选B样本校准代理并保存不确定性']
normal = '能算不等于适合直接建库，规模化需要成本与可信度同时过关。'
boundary = '数字为教学设定，没有运行 DFT、训练代理或复核任何候选材料。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
