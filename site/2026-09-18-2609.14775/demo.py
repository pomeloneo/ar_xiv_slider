inputs = {'A区': '2.0kWh × 600g/kWh', 'B区': '2.2kWh × 300g/kWh', '约束': 'B区有容量且不超SLA'}
steps = ['算A区为1200g', '算B区为660g', '比较能源增加10%', '确认碳排下降45%后再检查SLA']
normal = '能耗更高的执行位置也可能因电网更干净而总碳排更低。'
boundary = '未计网络、电价、预测误差与数据合规，不是论文60万任务仿真的复现。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
