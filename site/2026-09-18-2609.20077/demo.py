closeness = {
    "对照": [3.0, 3.2, 3.3, 3.5, 3.6],
    "记忆": [3.1, 3.3, 3.4, 3.6, 3.7],
    "问卷": [3.2, 3.3, 3.5, 3.6, 3.8],
}
changes = {name: values[-1] - values[0] for name, values in closeness.items()}
for name, values in closeness.items():
    print(f"{name}：{values[0]:.1f} → {values[-1]:.1f}，五日变化 {changes[name]:+.1f}")
for name in ("记忆", "问卷"):
    print(f"{name}相对对照的额外变化：{changes[name] - changes['对照']:+.1f}")

after = {"对照后悔": 2.0, "记忆组诡异感": 1.7, "问卷组后悔": 2.4}
print("不同结果不能合并：" + "，".join(f"{key}={value}" for key, value in after.items()))
assert abs(changes["记忆"] - changes["对照"]) < 0.01
print("边界：所有均值均为教学构造，只演示时间效应与组别交互的区别，不是论文结果复算。")
