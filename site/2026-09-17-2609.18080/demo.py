def model(causal,display): return causal>0
def probe(causal,display): return display>0
cases={"正常":(1,1),"清除显示特征":(1,0),"清除控制特征":(0,1)}
for name,state in cases.items(): print(name,"模型=",model(*state),"探针=",probe(*state))
assert model(1,0)==model(1,1) and probe(1,0)!=probe(1,1)
assert model(0,1)!=model(1,1) and probe(0,1)==probe(1,1)
print("边界：正常数据里两个变量始终相等，仅观察相关无法区分控制与显示。")
print("教学结构方程，不是SAE训练或Gemma干预复现。")
