calibration = [
    ((0.98, 0.92, 0.95), True),
    ((0.92, 0.88, 0.91), True),
    ((0.86, 0.82, 0.90), True),
    ((0.81, 0.84, 0.79), True),
    ((0.70, 0.76, 0.72), False),
    ((0.62, 0.71, 0.67), True),
]

def fused(channels):
    return sum(channels) / len(channels)

rows = [(fused(channels), correct) for channels, correct in calibration]
candidates = sorted({score for score, _ in rows}, reverse=True)
feasible = []
for threshold in candidates:
    accepted = [correct for score, correct in rows if score >= threshold]
    risk = 1 - sum(accepted) / len(accepted)
    if risk <= 0.10:
        feasible.append((len(accepted), threshold, risk))
coverage, threshold, risk = max(feasible)
print(f"教学校准：阈值 {threshold:.2f}，放行 {coverage}/{len(rows)}，经验错误率 {risk:.0%}")
new_fields = {
    "字段A": (0.90, 0.87, 0.93),
    "字段B": (0.78, 0.83, 0.76),
}
for name, channels in new_fields.items():
    score = fused(channels)
    route = "自动批准" if score >= threshold else "人工复核"
    print(f"{name} 三通道={channels}，融合={score:.2f} → {route}")
assert threshold > 0.79 and fused(new_fields["字段A"]) >= threshold
print("边界：六条手写样本只能演示阈值逻辑，不构成论文的保形风险上界或上线保证。")
