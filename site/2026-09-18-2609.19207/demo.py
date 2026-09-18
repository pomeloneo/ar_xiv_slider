requests = [
    ("tile-1", "layer3-seg7"),
    ("tile-2", "layer3-seg7"),
    ("tile-3", "layer3-seg8"),
    ("tile-4", "layer3-seg7"),
]
homes = {"layer3-seg7": "home-A", "layer3-seg8": "home-B"}

central_sends = len(requests)
groups = {}
for tile, segment in requests:
    groups.setdefault(segment, []).append(tile)
multicast_sends = len(groups)
home_load = {}
for segment in groups:
    home = homes[segment]
    home_load[home] = home_load.get(home, 0) + 1

print(f"集中逐请求发送：{central_sends} 份")
for segment, targets in groups.items():
    print(f"{homes[segment]} 对 {segment} 组播 1 份 → {','.join(targets)}")
print(f"分散组播发送：{multicast_sends} 份；home负载={home_load}")
print(f"此例减少 {(1 - multicast_sends/central_sends)*100:.0f}% 的数据份数")
assert multicast_sends < central_sends
print("边界：只按相同段合并请求；未模拟跳数、拥塞、credit、重复抑制、流水线或论文FPGA。")
