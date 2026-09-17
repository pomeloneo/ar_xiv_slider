"""Exact support enumeration for the paper's P1 with diagonal covariance.
Synthetic inputs; not the paper's branch-and-bound implementation or backtest.
Run: python3 demo.py
"""
from math import sqrt
from itertools import combinations
excess=[.08,.09,.10]
variance=[.04,.05,.09]
target=.03
supports=[s for n in (1,2,3) for s in combinations(range(3),n)]
def solve(support,gamma,penalty):
    h=sqrt(sum(excess[i]**2/variance[i] for i in support))
    if h <= gamma:
        return None
    scale=target/(h*(h-gamma))
    weights=[scale*excess[i]/variance[i] if i in support else 0 for i in range(3)]
    risk=sum(w*w*v for w,v in zip(weights,variance))
    worst=sum(w*r for w,r in zip(weights,excess))-gamma*sqrt(risk)
    assert abs(worst-target)<1e-12
    return risk+penalty*len(support),weights,risk,worst
for gamma,penalty in [(0,0),(0,.002),(.2,.002),(.3,.002)]:
    solutions=[(s,solve(s,gamma,penalty)) for s in supports]
    support,result=min([(s,r) for s,r in solutions if r is not None],key=lambda v:v[1][0])
    objective,w,risk,worst=result
    print(f'gamma={gamma}, penalty={penalty}: support={support}, weights={[round(x,4) for x in w]}, cash={1-sum(w):.4f}')
    print(f' worst_excess_return={worst:.5f}, variance={risk:.6f}, objective={objective:.6f}')
assert solve((0,),.4,.002) is None
print('Boundary: singleton A with gamma=0.4 cannot meet positive robust target.')
print('PASS: enumerated all 7 supports; each feasible solution satisfies the robust target exactly.')
