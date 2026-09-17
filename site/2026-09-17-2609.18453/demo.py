from statistics import mean
correct=[1,0]; confidence=[0.5,0.5]
ece=abs(mean(correct)-mean(confidence))
blind_good=[0.5,0.5]; blind_bad=[0.5,0.5]
grounded_good=[0.9,0.9]; grounded_bad=[0.1,0.1]
tgs=lambda good,bad: mean(a-b for a,b in zip(good,bad))
print(f"两题一对一错，始终报50%：单分组ECE={ece:.2f}")
print(f"轨迹不敏感的教学系统：好坏差={tgs(blind_good,blind_bad):.2f}")
print(f"会区分轨迹的教学系统：好坏差={tgs(grounded_good,grounded_bad):.2f}")
print(f"边界：两题差值+0.4/-0.4相互抵消，平均={mean([0.4,-0.4]):.2f}")
assert ece==0 and tgs(blind_good,blind_bad)==0
print("分值均为手工设定，没有调用或评测真实视觉语言模型。")
