for n in [2,8,32]:
    miss_true=(1-0.2)**n
    miss_rival=(1-0.1)**n
    print(f"N={n}: 没采到真线索={miss_true:.4f}; 没采到竞争线索={miss_rival:.4f}")
population=["T_fixed","R_fixed"]+["uncertain"]*6
after=["T" if x=="T_fixed" else "R" for x in population]
print("不确定者全跟随R后：",after,"真答案比例=",after.count("T")/len(after))
assert (0.8**32)<(0.8**2) and set(after)=={"T","R"}
print("边界：此覆盖算例不包含完整交流动力学，不能重现或证明准确率峰值。")
