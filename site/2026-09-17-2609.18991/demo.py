truth={"length":4,"width":3}
misread={"length":4,"width":6}
def solve(facts,rule="multiply"):
    a,b=facts["length"],facts["width"]
    return a*b if rule=="multiply" else a+b
print("手工注入感知错误：",misread,"->",solve(misread))
print("纠正事实后：",truth,"->",solve(truth))
print("边界：事实正确但公式错：",truth,"->",solve(truth,"add"))
assert solve(misread)==24 and solve(truth)==12 and solve(truth,"add")==7
outcomes=["correct","wrong","unfinished","unfinished"]
print("结果计数：",{x:outcomes.count(x) for x in sorted(set(outcomes))})
print("教学算例不调用视觉模型，不能报告真实感知恢复率。")
