inputs = {'国内产量生成': '每单位1张', '可靠进口生成': '每单位0.5张', '脆弱进口消耗': '每单位1张'}
steps = ['计算各流量的证书净贡献', '汇总证书供给和需求', '短缺时证书价格上升', '采购转向安全贡献更高的来源']
normal = '统一证书价格把分散的供应选择连接到同一数量目标。'
boundary = '没有求解论文的一般均衡，也未评估现实 WTO 合法性或任何国家政策。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
