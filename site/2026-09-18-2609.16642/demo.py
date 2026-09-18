inputs = {'规则': '官方全年值>5%则YES', '初值': '5.2%', '修订值': '4.9%', '历史规则版本': '缺失'}
steps = ['按当时规则读取初值', '首次映射为 YES', '官方修订后映射为 NO', '历史版本缺失时标记不可测']
normal = 'first 和 stable decidability 可以不同，且历史证据不足时两者都不能伪造。'
boundary = '示例未对应真实 Kalshi 合约，也没有测量市场价格或延迟。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
