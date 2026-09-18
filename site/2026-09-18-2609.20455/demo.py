inputs = {'失败': '关系方向读反', '候选地址': 'Q3.execution.step2', '局部旧正确数': 4, '候选后正确数': 3}
steps = ['对比成功与失败轨迹', '归因到 Q3 的方向步骤', '只生成该字段候选编辑', '局部正确数下降，因此回滚']
normal = '候选没有越过 Local Gate，不进入全局提交。'
boundary = '这是规则化演示，没有调用教师模型或复现三个基准分数。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
