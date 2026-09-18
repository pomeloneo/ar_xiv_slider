households = {
    "甲": {"extreme", "multidimensional", "food"},
    "乙": {"multidimensional", "food"},
    "丙": {"relative"},
    "丁": {"food", "relative"},
    "戊": set(),
}
measures = ["extreme", "multidimensional", "food", "relative"]
counts = {measure: sum(measure in flags for flags in households.values()) for measure in measures}
naive_sum = sum(counts.values())
union = {name for name, flags in households.items() if flags}

print("各尺子人数：" + "，".join(f"{key}={value}" for key, value in counts.items()))
print(f"直接相加={naive_sum} 人次；实际被至少一种尺子识别={len(union)} 人")
print("被重复计数：" + "，".join(f"{name}({len(flags)}项)" for name, flags in households.items() if len(flags) > 1))
assert naive_sum > len(union)
print("边界：家庭与标签完全虚构，只演示集合重叠；不能据此估计任何国家或全球贫困人数。")
