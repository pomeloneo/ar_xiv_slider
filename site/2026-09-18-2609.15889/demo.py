inputs = {'计算': '2ms', '网络': '5ms（与计算重叠）', '管理日志': '1ms（串行）'}
steps = ['重叠阶段取max(2,5)=5ms', '串行加1ms得到6ms', '同输入重复得到同轨迹', '没有真机测量就不声称6ms是真实延迟']
normal = '功能与虚拟时间可重复，但物理准确度仍需目标机器校准。'
boundary = '没有启动 Cnuas、QEMU、RDMA 或物理机架，只演示计时公式。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
