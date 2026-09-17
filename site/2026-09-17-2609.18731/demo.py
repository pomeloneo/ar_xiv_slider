from collections import deque
def plan(can_open):
    start=("A",False); queue=deque([(start,[])]); seen={start}
    while queue:
        (room,opened),steps=queue.popleft()
        if room=="B": return steps
        options=[]
        if can_open and not opened: options.append(((room,True),"开门"))
        if room=="A" and opened: options.append((("B",opened),"移动到B"))
        for state,action in options:
            if state not in seen: seen.add(state); queue.append((state,steps+[action]))
    return None
print("目标在B：词汇合法；可用开门动作时计划=",plan(True))
print("目标在B：词汇合法；没有开门动作时计划=",plan(False))
vocabulary={"at"}; requested="happy"
print("目标开心：谓词是否已定义？",requested in vocabulary)
assert plan(True)==["开门","移动到B"] and plan(False) is None
print("手写符号规划示例，不是六种LLM的翻译评测复现。")
