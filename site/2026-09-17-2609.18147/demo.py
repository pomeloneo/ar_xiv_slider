"""Synthetic resource-pooling and participation examples, not medical simulation."""
from itertools import product
states=list(product([0,2],repeat=2))
separate=sum(sum(min(1,d) for d in state) for state in states)/len(states)
pooled=sum(min(2,sum(state)) for state in states)/len(states)
print(f"equal-probability demand states: separate={separate}, pooled={pooled}")
assert separate==1 and pooled==1.5
r=(0.9,0.4); s=(0.4,1.1); floor=(0.8,0.3)
feasible=[]
for step in range(1001):
    a=step/1000
    utility=tuple(a*x+(1-a)*y for x,y in zip(r,s))
    if all(x+1e-12>=b for x,b in zip(utility,floor)):feasible.append((sum(utility),a,utility))
total,a,utility=max(feasible)
print(f"unconstrained S: utilities={s}, sum={sum(s)}, region A below floor={s[0]<floor[0]}")
print(f"constrained mixture: share_R={a:.3f}, utilities=({utility[0]:.3f},{utility[1]:.3f}), sum={total:.3f}")
assert abs(a-0.8)<1e-9
