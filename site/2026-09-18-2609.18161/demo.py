inputs = {'附加费': 10, '高通涨价流失销量': 100, '转向对手': 60, '退出市场': 40}
steps = ['政府税情形税款归第三方', '附加费情形对手手机仍向高通付费', '高通从转移的60台保留收费', '因此两制度的调价激励不同']
normal = '收费文字相同不等于收款方的竞争激励相同。'
boundary = '数字是钱流类比，没有求均衡、估计真实转移率或评价个案损害。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
