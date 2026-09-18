inputs = {'强连接': 'A-B=10', '弱连接': 'A-C=2, B-D=2', '早期方案': 'A上/B下', '软方案': 'B可在优化中换层'}
steps = ['从连接强度建立相近起点', '保留B的软层概率', '同时比较线长和同层重叠', '收敛后固定层号并合法化']
normal = '软层搜索可以修正早期分层，而不是让后续2D布局背负不可逆决定。'
boundary = '没有求解 HPWL、制造规则或论文基准，只展示联合决策逻辑。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
