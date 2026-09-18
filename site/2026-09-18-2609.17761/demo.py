inputs = {'直接参与变化': -5, '回应减弱导致变化': 8, '残余服务变化': '20%到40%'}
steps = ['计算直接压制-5', '计算间接持续+8', '相加得到+3', '比较两通道大小决定所在区间']
normal = '机构更能撑住时，稳定参与可能反而提高。'
boundary = '数值不是现实罢工估计，也不预测持续时间或提供谈判策略。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
