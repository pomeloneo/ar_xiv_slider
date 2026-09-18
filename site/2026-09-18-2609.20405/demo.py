alpha, depreciation, population, floor = 1/3, 0.05, 0.02, 0.50

def run(label, caution):
    k = 0.55
    rows = []
    for t in range(18):
        net_output = k ** alpha - (depreciation + population) * k
        if net_output <= floor + 0.06:
            consumption = floor
            regime = "保底"
        else:
            surplus = net_output - floor
            saving_rate = max(0.12, 0.68 - caution * 0.11 * t)
            consumption = floor + surplus * (1 - saving_rate)
            regime = "起飞"
        saving = max(0.0, net_output - consumption)
        rows.append((t, k, consumption, saving, regime))
        k += saving
    print(label + "：" + "；".join(f"t{t} k={k:.2f} c={c:.2f} {r}" for t, k, c, _, r in rows[::5]))
    return rows

front = run("早期偏多储蓄", 0.12)
back = run("早期偏少储蓄", 0.35)
assert all(row[2] >= floor for row in front + back)
print("边界：储蓄率是人为教学规则，不是论文的最优路径、Lambert W公式或误差界数值验证。")
