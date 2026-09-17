"""Feasibility and utility for a synthetic menu, not optimal auction replication."""
menu=[(0.0,0.0),(0.5,1.5),(1.0,4.0)]
def choose(value,cap):
    feasible=[(value*x-pay,x,pay) for x,pay in menu if pay<=cap*x+1e-12]
    return max(feasible)
for cap in [2,3,5]:
    utility,allocation,payment=choose(10,cap)
    print(f"cap={cap}: allocation={allocation}, payment={payment}, utility={utility}")
assert choose(10,2)[1]==0
assert choose(10,3)[1]==0.5
assert choose(10,5)[1]==1
print("boundary: 1.5 <= 2 but 1.5 / 0.5 = 3 > 2, so the half-allocation violates cap=2")
