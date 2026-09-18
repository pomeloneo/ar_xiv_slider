inputs = {'节省电费': '100元', '少发电损失': '70元', '少拿发电补贴': '20元', '冷机资本维护': '尚未计入'}
steps = ['记录100元节电收益', '减去70元发电机会成本', '再减20元补贴损失', '剩10元再与冷机固定成本比较']
normal = '余热并不免费，运行毛收益很小且未必覆盖设备年金。'
boundary = '数字为教学算例，没有运行论文8,760小时优化，也不构成核电或数据中心投资建议。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
