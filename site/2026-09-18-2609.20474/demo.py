inputs = {'基础真成功': 70, '计划后真成功': 77, '失败轨迹': 23, '验证器拦下失败': 14, '错拦正确': 4}
steps = ['先算计划多完成 7 个任务', '再算验证器少放出 14 个错误', '同时记录错拦 4 个正确结果', '按业务的错误责任决定权重']
normal = '计划改善完成能力；验证器控制交付风险，它们不能用一个成功率混为一谈。'
boundary = '数字是教学缩放，不是论文原始样本重算，也没有估算你的真实业务损失。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
