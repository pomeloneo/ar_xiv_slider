inputs = {'模型商份额': ['30%', '25%', '25%', '20%'], '光刻设备份额': ['100%'], '关键材料成本份额': '0.1%'}
steps = ['平方份额计算两层HHI', '比较1,800阈值', '估算材料翻倍的成本传导', '再检查完全断供是否可替代']
normal = '下游选择多并不能消除共同上游的单点依赖。'
boundary = '份额为教学例，不是重新计算论文数据，也不构成产业或投资建议。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
