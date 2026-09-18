import math

def corr_matrix(channels):
    centered = []
    for values in channels:
        mean = sum(values) / len(values)
        deviations = [value - mean for value in values]
        scale = math.sqrt(sum(value * value for value in deviations))
        centered.append([value / scale for value in deviations])
    return [[sum(a*b for a, b in zip(left, right)) for right in centered] for left in centered]

def dominant_eigenvalue(matrix, steps=40):
    vector = [1 / math.sqrt(len(matrix))] * len(matrix)
    value = 0.0
    for _ in range(steps):
        product = [sum(row[j] * vector[j] for j in range(len(vector))) for row in matrix]
        norm = math.sqrt(sum(item * item for item in product))
        vector = [item / norm for item in product]
        value = sum(vector[i] * sum(matrix[i][j] * vector[j] for j in range(len(vector))) for i in range(len(vector)))
    return value, vector

base = [math.sin(i * 0.7) for i in range(30)]
independent = [
    [math.sin(i * 0.7) for i in range(30)],
    [math.sin(i * 1.1 + 0.8) for i in range(30)],
    [math.cos(i * 1.7 + 0.3) for i in range(30)],
]
synchronized = [
    [base[i] + 0.18 * math.sin(i * 1.3) for i in range(30)],
    [0.9 * base[i] + 0.15 * math.cos(i * 1.1) for i in range(30)],
    [1.1 * base[i] + 0.12 * math.sin(i * 1.9) for i in range(30)],
]

scores = []
for label, channels in (("近似独立", independent), ("共享节拍", synchronized)):
    matrix = corr_matrix(channels)
    eigenvalue, vector = dominant_eigenvalue(matrix)
    si = eigenvalue / sum(matrix[i][i] for i in range(3))
    participation = [item * item for item in vector]
    scores.append(si)
    print(f"{label}：SI={si:.3f}，参与度=" + ",".join(f"{item:.2f}" for item in participation))

cusum = 0.0
baseline, allowance, threshold = scores[0], 0.05, 0.40
for second, si in enumerate([scores[0]] * 3 + [scores[1]] * 4, 1):
    cusum = max(0.0, cusum + si - baseline - allowance)
    print(f"秒{second}：SI={si:.3f}，CUSUM={cusum:.3f}，告警={'是' if cusum > threshold else '否'}")
assert scores[1] > scores[0] and cusum > threshold
print("边界：波形与阈值均为教学构造；不是RTDS或现场SCADA，也不能复现论文检测指标。")
