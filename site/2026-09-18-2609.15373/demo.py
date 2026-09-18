inputs = {'Oracle最终': '12:00', '协议解析': '12:02', '可赎回': '12:02', '观察赎回': '12:05'}
steps = ['记录上游 Oracle 结果', 'adapter/协议写入赔付', '中奖头寸变为可赎回', '持有人实际调用赎回']
normal = '从协议解析到观察赎回是 3 分钟，但不代表所有权益都在 3 分钟兑现。'
boundary = '不是链上数据重建，也没有推断任何用户资金或平台可靠性。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
