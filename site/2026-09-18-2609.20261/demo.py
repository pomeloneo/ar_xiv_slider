inputs = {'库存': 12, '拟购买': 8, '推导时证书': '有效', '提交时证书': '已撤销'}
steps = ['记录库存、证书、政策和授权版本', '密封下单 8 件的提案', '提交前同时复核依赖', '证书版本变化，因此严格模式拒绝']
normal = '若所有依赖保持有效，订单和回执一起提交；本例因证书撤销而拒绝。'
boundary = '这里只演示依赖变化；没有实现论文的锁、签名、注册表或 PostgreSQL 性能实验。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
