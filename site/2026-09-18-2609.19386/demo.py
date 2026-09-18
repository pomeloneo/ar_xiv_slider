inputs = {'观测ATT': -4, '选择混杂强度': 0.3, '趋势差异': 5, '对齐': '同方向'}
steps = ['确认隐藏因素影响处理概率', '确认它影响未处理趋势', '检查两个影响是否同向', '比较可能偏误与4单位结论']
normal = '缺少任一通道时偏误会减弱；三者同时强且对齐时才容易推翻结论。'
boundary = '未实现论文精确公式、DML 或最低工资数据估计，只演示偏误结构。'

print("教学输入：")
for name, value in inputs.items():
    print(f"- {name}：{value}")
print("中间状态：")
for index, step in enumerate(steps, 1):
    print(f"{index}. {step}")
print("正常例：" + normal)
assert inputs and steps and normal
print("边界：" + boundary)
