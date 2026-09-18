inputs = {'车站': '10万人快速换乘', '广场': '5000人反复共处', '学校': '与广场共享许多家庭人对'}
steps = ['用流量找移动中心', '用同处找社会中心', '用共享人对连广场与学校', '比较三种城市结构']
normal = '流量最大、共处最多和社会重叠最强可以落在不同地点。'
boundary = '没有处理真实 CDR，也不推断个人身份、关系或城市规划效果。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
