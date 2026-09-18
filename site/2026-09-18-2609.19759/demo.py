inputs = {'稀疏任务': '三条独立调研后汇总', '紧耦合任务': '日志→令牌→数据库', '智能体数': 3}
steps = ['画出子任务依赖边', '检查每个节点是否需要完整前序', '估算重复上下文', '仅对独立分支按需并行']
normal = '调研分支适合并行；严格诊断链更适合一个保留完整状态的智能体。'
boundary = '示例只比较依赖结构，没有运行 SAIGE、语言模型或论文基准。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
