from math import isclose
n, compute, read = 6, 8, 5
serial=n*(compute+read)
pipeline=compute+read+(n-1)*max(compute,read)
print(f"教学流水线：串行 {serial} ms，理想重叠 {pipeline} ms")
assert serial==78 and pipeline==53
slow=12
print(f"读盘变慢：串行 {n*(compute+slow)} ms，理想重叠 {compute+slow+(n-1)*max(compute,slow)} ms")
base,delta,step=1.0,0.02,0.1
merged=round((base+delta)/step)*step
separate=base+delta
print(f"补丁合并再取整={merged:.2f}；独立计算后相加={separate:.2f}")
assert isclose(merged,1.0) and isclose(separate,1.02)
print("边界：以上假设预测名单直接采用、无调度开销，不是实测模型吞吐。")
