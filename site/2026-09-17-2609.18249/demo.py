items=[{"id":"A","color":"red","side":"left","price":120},{"id":"B","color":"red","side":"right","price":80},{"id":"C","color":"blue","side":"left","price":70}]
def select(preference):
    return [x["id"] for x in items if x["color"]==preference["color"] and x["price"]<=preference["budget"] and (preference["side"]=="either" or x["side"]==preference["side"])]
p={"color":"red","side":"left","budget":100}
print("第一轮偏好：",p,"匹配：",select(p))
assert select(p)==[]
p={**p,"side":"either"}
print("第二轮只放宽位置：",p,"匹配：",select(p))
assert select(p)==["B"] and p["budget"]==100
print("无匹配时应解释缺口；不能改写价格或编造商品。")
print("手工结构化商品示例，不是视觉模型训练复现。")
