inputs = {'低类型原信号': 4, '高类型原信号': 8, '低类型AI后信号': 7, '高类型新信号': 10}
steps = ['雇主只看总信号', '低类型用AI接近原高类型', '原8不再充分区分', '高类型提高到10维持分离']
normal = 'AI 替代低类型部分努力，却可能把高类型的信号竞赛推高。'
boundary = '数值是教学故事，没有求论文均衡，也不预测真实招聘市场。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
