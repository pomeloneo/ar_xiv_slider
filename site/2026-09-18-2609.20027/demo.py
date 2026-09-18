inputs = {'高分十分位响应率': 0.8, '中间十分位响应率': 0.35, '低分十分位响应率': 0.1, '另一目标': '0.4、0.7、0.3（不单调）'}
steps = ['按归因分十分位', '分别训练并测目标行为', '检查高分到低分是否单调下降', '不单调时拒绝把排序当过滤保证']
normal = '第一组排序有方向性证据；第二目标不稳定，不能照搬过滤阈值。'
boundary = '响应率是教学数字，没有训练模型，也不表示归因方法的真实效果。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
