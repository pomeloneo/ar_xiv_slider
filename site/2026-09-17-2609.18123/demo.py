from statistics import median,mean,pstdev
naive,honest,candidate=106.0,20.3,10.0
print(f"同一候选：朴素基线 {naive/candidate:.2f}x，合理基线 {honest/candidate:.2f}x")
base=[20,22,18]; new=[10,11,9]
ratios=[a/b for a,b in zip(base,new)]
print(f"成对倍率={ratios}，中位数={median(ratios):.2f}x")
inputs=[1,2,3]; expected=[x*x for x in inputs]; cheating=inputs
print(f"正确性检查：返回输入的候选通过吗？{cheating==expected}")
assert cheating!=expected
print(f"另一设备的本地基线20、新版本25：{20/25:.2f}x，实际变慢")
assert honest/candidate<naive/candidate
print("这些时间是手工数据；本脚本不做真实硬件性能评测。")
