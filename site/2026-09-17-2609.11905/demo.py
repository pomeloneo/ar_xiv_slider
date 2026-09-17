"""Verify the Gaussian special case of EVaR risk contribution.
Run: python3 demo.py
"""
from math import sqrt, log
eta=.05
k=sqrt(-2*log(eta))
sigmas=[.1,.2]
def calc(w,mu):
    vol=sqrt(sum((wi*si)**2 for wi,si in zip(w,sigmas)))
    dev=k*vol
    dev_rc=[k*wi*wi*si*si/vol for wi,si in zip(w,sigmas)]
    raw=dev-sum(wi*mi for wi,mi in zip(w,mu))
    raw_rc=[ri-wi*mi for ri,wi,mi in zip(dev_rc,w,mu)]
    assert abs(sum(dev_rc)-dev)<1e-12
    assert abs(sum(raw_rc)-raw)<1e-12
    return vol,dev,dev_rc,raw,raw_rc
w=[2/3,1/3]
for mu in ([0,0],[.08,.01]):
    vol,dev,rc,raw,rrc=calc(w,mu)
    print(f'mean={mu}; weights={[round(x,4) for x in w]}')
    print(f' volatility={vol:.6f}; centered_EVaR={dev:.6f}; contributions={[round(x,6) for x in rc]}')
    print(f' raw_EVaR={raw:.6f}; raw_contributions={[round(x,6) for x in rrc]}')
assert abs(calc(w,[0,0])[2][0]-calc(w,[0,0])[2][1])<1e-12
_,_,_,boundary,_=calc(w,[1,1])
print(f'boundary with unrealistically high mean: raw_EVaR={boundary:.6f}; inverse-risk positivity must be checked')
print('PASS: centered Gaussian EVaR rescales volatility; raw EVaR includes the mean.')
