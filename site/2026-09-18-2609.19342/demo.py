load_mw = [80, 82, 118, 84, 79, 105, 81]
generation_plan = [85, 85, 90, 90, 85, 90, 85]
power_limit = 25.0
energy_capacity = 100.0
soc_mwh = 60.0
hours = 0.25

print("时段  负荷  发电计划  电池放电(+)/充电(-)  SOC")
for index, (load, generation) in enumerate(zip(load_mw, generation_plan), 1):
    requested = load - generation
    battery = max(-power_limit, min(power_limit, requested))
    energy_change = battery * hours
    if energy_change > soc_mwh:
        battery = soc_mwh / hours
        energy_change = soc_mwh
    if -energy_change > energy_capacity - soc_mwh:
        energy_change = -(energy_capacity - soc_mwh)
        battery = energy_change / hours
    soc_mwh -= energy_change
    print(f"{index:>2} {load:>6.0f} {generation:>8.0f} {battery:>18.1f} {soc_mwh:>7.1f}")

print(f"期末SOC={soc_mwh:.1f} MWh；功率上限={power_limit:.0f} MW")
assert 0 <= soc_mwh <= energy_capacity
print("边界：负荷、时长和控制规则均为教学构造；未包含效率、退化、机组约束、价格、备用或SSTI。")
