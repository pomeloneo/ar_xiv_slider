truth = [1.0, -0.5, 0.7, 1.4, -0.2]
pit = [0.6, -0.1, 0.4, 0.8, 0.1]
future_trained = [1.3, 0.4, -0.2, 1.8, 0.5]

def mse(values):
    return sum((y - p) ** 2 for y, p in zip(truth, values)) / len(truth)

print("期  真值  PIT  暴露版  修订D  PIT误差平方  暴露版误差平方")
for i, (y, p, q) in enumerate(zip(truth, pit, future_trained), 1):
    print(f"{i:>2} {y:>5.1f} {p:>5.1f} {q:>7.1f} {q-p:>7.1f} {(y-p)**2:>11.2f} {(y-q)**2:>15.2f}")
print(f"PIT MSE={mse(pit):.3f}；暴露版 MSE={mse(future_trained):.3f}")
assert mse(future_trained) > mse(pit)
print("边界：数据为教学数组；它只说明时间暴露与准确率是两件事，不代表任何真实资产表现。")
