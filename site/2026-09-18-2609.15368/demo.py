inputs = {'第一代': '请求→提议→争议→重置', '第二代': '请求→提议→Oracle最终', '规则澄清': '两代之间'}
steps = ['按 request generation 分组', '保留第一代争议', '把澄清绑定到时间位置', '第二代最终不覆盖第一代历史']
normal = '同一个问题具有多段状态路径，不能压成单一解决时间。'
boundary = '没有读取链上账户或判断任何争议动机，也不是杠杆产品设计建议。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
