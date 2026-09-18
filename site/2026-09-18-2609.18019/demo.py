state = {}
events = [
    ("add", "A"),
    ("trade", "A"),
    ("shadow_fill", "A"),
    ("add", "B"),
    ("delete", "B"),
]
for kind, followed in events:
    if kind == "add":
        state[followed] = "resting"
        print(f"{followed}: 新增被选中 → 影子挂单，状态=resting")
    elif kind == "trade" and followed in state:
        state[followed] = "grace"
        print(f"{followed}: 被跟随单成交 → 开启宽限，状态=grace")
    elif kind == "shadow_fill" and state.get(followed) == "grace":
        state[followed] = "filled"
        print(f"{followed}: 扫单继续 → 影子成交，状态=filled")
    elif kind == "delete" and followed in state:
        state[followed] = "cancelled"
        print(f"{followed}: 被跟随单撤销 → 影子立即撤销，状态=cancelled")
assert state == {"A": "filled", "B": "cancelled"}
print("边界：消息顺序为手写示例；没有价格、队列深度、延迟、自身市场冲击或真实交易。")
