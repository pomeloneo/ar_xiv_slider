places = {
    "附近咖啡馆": {"score": 0.75, "km": 1.2},
    "附近商店": {"score": 0.65, "km": 1.8},
    "跨城办公室": {"score": 0.05, "km": 22.0},
    "城市图书馆": {"score": -0.10, "km": 18.0},
}
routes = {
    "附近探索者": [("附近咖啡馆", 40), ("附近商店", 20)],
    "远行通勤者": [("跨城办公室", 45), ("城市图书馆", 15)],
}
residential_score = 0.80

def experienced(route):
    minutes = sum(duration for _, duration in route)
    score = sum(places[name]["score"] * duration for name, duration in route) / minutes
    distance = sum(places[name]["km"] * duration for name, duration in route) / minutes
    return score, distance

print(f"两人的居住暴露都为 {residential_score:+.2f}")
for person, route in routes.items():
    score, distance = experienced(route)
    print(f"{person}：平均距离 {distance:.1f} km，经历分数 {score:+.2f}")
assert abs(experienced(routes["远行通勤者"])[0]) < abs(experienced(routes["附近探索者"])[0])
print("边界：地点分数、路线和停留时间均为虚构；结果只演示加权定义，不证明远行会造成政治态度变化。")
