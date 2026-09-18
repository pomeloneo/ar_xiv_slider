inputs = {'地区原型': ['A北部', 'B沿海', 'C中部'], '方案': 'ABC', '相邻方案': 'ABB'}
steps = ['把相似选区聚成字母', '按整套计划组成单词', '对ABC赋0.7权重', '对ABB赋0.3并检查层间连接']
normal = '软归属保留方案靠近多个层的事实。'
boundary = '没有生成合法选区、计算人口平衡或证明分层采样的统计增益。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
