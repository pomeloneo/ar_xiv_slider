power_kw = 12.0
nominal_v = 48.0
resistance = nominal_v ** 2 / (power_kw * 1000)
line_resistance = 0.015

print("电压  恒功率电流  电阻负载电流  恒功率线路压降  电阻线路压降")
constant_currents = []
for voltage in (52, 48, 44, 40):
    constant_i = power_kw * 1000 / voltage
    resistive_i = voltage / resistance
    constant_currents.append(constant_i)
    print(
        f"{voltage:>4}V {constant_i:>10.1f}A {resistive_i:>12.1f}A"
        f" {constant_i*line_resistance:>14.2f}V {resistive_i*line_resistance:>12.2f}V"
    )
assert constant_currents[-1] > constant_currents[0]
print("边界：这是静态 I=P/V 对比；真实稳定性还取决于控制器、阻抗、储能、保护和扰动时间尺度。")
