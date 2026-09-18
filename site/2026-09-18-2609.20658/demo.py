tasks = {
    "AI代写并直接发送邮件": {
        "human_led": False, "rewrote": False, "voice": False, "can_explain": True,
    },
    "人主导故事并迭代AI插图": {
        "human_led": True, "rewrote": True, "voice": True, "can_explain": True,
    },
}
labels = {
    "human_led": "人主导关键决定",
    "rewrote": "有实质迭代或重写",
    "voice": "保留个人声音",
    "can_explain": "能解释并维护成果",
}

for task, states in tasks.items():
    present = [labels[key] for key, value in states.items() if value]
    missing = [labels[key] for key, value in states.items() if not value]
    print(task)
    print("  已观察：" + "、".join(present))
    print("  待补：" + ("、".join(missing) if missing else "无"))
assert all(tasks["人主导故事并迭代AI插图"].values())
print("边界：这是论文主题的教学检查表，不是心理量表，也不能判定版权、署名或组织合规。")
