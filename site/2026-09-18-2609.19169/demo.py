inputs = {'机器内存': '64GB', '引擎A': '200 tok/s, 100/100, 35GB, 质量通过', '引擎B': '230 tok/s, 100/100, 61GB, 质量失败'}
steps = ['先检查完成率', '再保留系统内存余量', '核对任务质量', '最后才比较速度']
normal = 'A 虽然慢 30 tok/s，却通过可用性门槛；B 不能因速度第一直接胜出。'
boundary = '数字是教学设定，没有运行论文引擎，也不代表任何真实版本的性能。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
