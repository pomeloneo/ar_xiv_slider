inputs = {'初始危机': '高', '初始保护': '30%', '保护有效性': '降低危机', '放松条件': '危机下降'}
steps = ['危机高降低采用门槛', '保护升至70%使危机下降', '危机低使保护降至40%', '保护下降后危机反弹']
normal = '行为与危机互推可形成多轮变化，而非单向扩散到终点。'
boundary = '百分比为教学轨迹，没有运行疫情模型、估计参数或预测感染。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
