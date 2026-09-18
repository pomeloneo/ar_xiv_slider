inputs = {'共同安排': '每周远程3天', '员工甲': '异步更新+关闭通知', '员工乙': '持续待命+少同步'}
steps = ['先记录安排', '再编码沟通与健康行为', '连接可能结果', '加入偏好和文化情境']
normal = '相同远程天数不能替代行为测量。'
boundary = '这是概念分类练习，没有测量真实员工、估计因果效应或给出管理规定。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
