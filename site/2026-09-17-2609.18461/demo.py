memories={"临街酒店太吵":{"travel","quiet"},"周末选人少公园":{"leisure","quiet"},"工作时常开线上会议":{"work","audio"}}
def activate(query):
    return [(text,len(tags&query)) for text,tags in memories.items() if tags&query]
for name,query in [("住宿",{"travel","quiet"}),("会议设备",{"work","audio"}),("园艺",{"gardening"})]:
    activated=activate(query)
    print(name,activated if activated else "证据不足")
assert len(activate({"travel","quiet"}))==2
assert len(activate({"work","audio"}))==1
assert activate({"gardening"})==[]
print("手工概念集合仅模拟问题条件化连接，不是SAE、GNN或隐含偏好推断复现。")
