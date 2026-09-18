inputs = {'真实纯度': '99.95%（教学秘密）', '合格门槛': '99.9%', '公开内容': '承诺与是否合格'}
steps = ['对真实纯度生成承诺', '计算纯度是否达到门槛', '只公开有效证明', '验证者得到合格但看不到具体值']
normal = '验证具体条件不要求把供应商的完整原始字段公开。'
boundary = '这是逻辑类比，没有实现承诺、Groth16、区块链或身份认证。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
