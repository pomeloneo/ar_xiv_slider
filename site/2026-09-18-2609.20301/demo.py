inputs = {'正常运行': '诊断认证→查凭据 300 token', '失败运行': '诊断认证→查凭据→刷新令牌→重试 900 token', '权重': 'token'}
steps = ['统一不同日志事件', '递归切出诊断与子步骤', '按语义路径累加 token', '比较坏运行减好运行']
normal = '差分热点指向刷新令牌与重试分支，供开发者优先调查。'
boundary = '热点不是失败因果；示例未运行论文分割模型或真实 pprof。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
