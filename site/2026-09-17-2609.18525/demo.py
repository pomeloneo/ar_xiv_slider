from statistics import mean,pvariance
def fisher(a,b):
    denominator=pvariance(a)+pvariance(b)
    if denominator==0: return 0.0 if mean(a)==mean(b) else float("inf")
    return (mean(a)-mean(b))**2/denominator
a=[-3,-2,-1];b=[1,2,3]
print(f"原始表示 Fisher={fisher(a,b):.1f}")
print(f"取绝对值后 Fisher={fisher(list(map(abs,a)),list(map(abs,b))):.1f}")
xor_a=[(-1,-1),(1,1)];xor_b=[(-1,1),(1,-1)]
scores=[fisher([x[k] for x in xor_a],[x[k] for x in xor_b]) for k in (0,1)]
correct=sum(x*y>0 for x,y in xor_a)+sum(x*y<0 for x,y in xor_b)
print("边界：逐维分数",scores,"；乘积规则正确",correct,"/4")
assert scores==[0.0,0.0] and correct==4
print("Fisher比率不是分类任务的F1-score；未使用原论文肌电数据。")
