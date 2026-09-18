inputs = {'红群住区': '东西各半', '蓝群住区': '东西各半', '世界A': '只按距离交友', '世界B': '距离相同但偏好同色'}
steps = ['确认居住构成相同', '建立随机混合参照', '比较实际同群连接', '把额外偏离归入社会通道']
normal = '传统地理隔离相同，社会隔离可以完全不同。'
boundary = '两群玩具网络没有拟合 Facebook 数据，也不能识别真实人的偏好或歧视。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
