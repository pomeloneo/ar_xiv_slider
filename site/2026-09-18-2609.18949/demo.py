from collections import Counter

truth = ["stable"] * 18 + ["watch", "stress"]
always_stable = ["stable"] * 20
balanced = ["stable"] * 17 + ["watch", "watch", "stress"]
labels = ("stable", "watch", "stress")

def metrics(predicted):
    accuracy = sum(a == b for a, b in zip(truth, predicted)) / len(truth)
    f1s = []
    for label in labels:
        tp = sum(t == label and p == label for t, p in zip(truth, predicted))
        fp = sum(t != label and p == label for t, p in zip(truth, predicted))
        fn = sum(t == label and p != label for t, p in zip(truth, predicted))
        f1s.append(0 if 2 * tp + fp + fn == 0 else 2 * tp / (2 * tp + fp + fn))
    return accuracy, sum(f1s) / len(f1s)

print("真实类别：" + str(Counter(truth)))
for name, predicted in (("永远稳定", always_stable), ("识别少数类", balanced)):
    accuracy, macro_f1 = metrics(predicted)
    print(f"{name}：accuracy={accuracy:.0%}，Macro-F1={macro_f1:.3f}")
assert metrics(always_stable)[0] == 0.9
assert metrics(balanced)[1] > metrics(always_stable)[1]
print("边界：20条手写标签不测概率校准、时间泄漏、价格偏离、成本或真实稳定币风险。")
