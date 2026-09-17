def check(events):
    approved=None; limit=0; done=False; output=[]
    for kind,person,amount in events:
        if kind=="approve":
            approved,limit=person,amount; done=False; output.append("批准已记录")
        elif kind!="execute":
            output.append("拒绝：未知事件类型")
        elif approved!=person:
            output.append("拒绝：未批准或对象不匹配")
        elif amount>limit:
            output.append("拒绝：数量超出批准值")
        else:
            done=True; output.append("执行允许")
    output.append("结束：已完成" if done else "结束：仍有待完成义务")
    return output
cases={"正常":[("approve","甲",42),("execute","甲",40)],"错对象":[("approve","甲",42),("execute","乙",40)],"超限":[("approve","甲",42),("execute","甲",50)],"缺批准":[("execute","甲",40)],"新批准仍待执行":[("approve","甲",42),("execute","甲",40),("approve","乙",30)],"新批准随后完成":[("approve","甲",42),("execute","甲",40),("approve","乙",30),("execute","乙",30)]}
cases["未知事件被拒绝"]=[("approve","甲",42),("cancel","甲",1)]
cases["拒绝后仍能执行"]=[("approve","甲",42),("cancel","甲",1),("execute","甲",40)]
for name,events in cases.items(): print(name," -> ".join(check(events)))
assert check(cases["正常"])[-1]=="结束：已完成"
assert "拒绝" in check(cases["错对象"])[1]
assert check(cases["新批准仍待执行"])[-1]=="结束：仍有待完成义务"
assert check(cases["新批准随后完成"])[-1]=="结束：已完成"
assert check(cases["未知事件被拒绝"])[1]=="拒绝：未知事件类型"
assert check(cases["未知事件被拒绝"])[-1]=="结束：仍有待完成义务"
assert check(cases["拒绝后仍能执行"])[-1]=="结束：已完成"
print("单义务模型：新批准替换旧义务并重置完成标记；未实现完整LTLf编译器。")
