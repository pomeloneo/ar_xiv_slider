from math import exp,log1p
positive,negative,lr=0.7,0.8,0.5
loss=lambda p,n:log1p(exp(n-p))
before=loss(positive,negative)
bad_probability=1/(1+exp(positive-negative))
new_positive=positive+lr*bad_probability
new_negative=negative-lr*bad_probability
print(f"更新前：正例={positive:.4f}，负例={negative:.4f}，余量={positive-negative:.4f}，损失={before:.4f}")
print(f"更新后：正例={new_positive:.4f}，负例={new_negative:.4f}，余量={new_positive-new_negative:.4f}，损失={loss(new_positive,new_negative):.4f}")
assert new_positive>new_negative and loss(new_positive,new_negative)<before
evidence={"概念A":"教学文献A"}
print("边界：概念B有外部证据吗？",evidence.get("概念B"),"-> 跳过")
print("仅优化两个自由分数；不代表文本编码器训练或泛化效果。")
