inputs = {'村A到诊所': '8公里', '村B到诊所': '8公里', '村A': '近主干网', '村B': '多层支路断裂'}
steps = ['确认局部距离都差', '检查接入镇级道路', '检查接入区域服务', '区分局部缺口与系统断裂']
normal = '同样 8 公里可对应完全不同的干预范围。'
boundary = '没有真实路线、设施容量或医疗结果，不能据此安排具体资源。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
