"""Exact arithmetic for the worker-side switch in Example W."""
from fractions import Fraction as F
q_bad,q_good=F(3,5),F(3,4)
p0=F(5,16); reconstruction=F(1,100)
c_standard,c_intensive=F(1,10),F(19,25)
p1=p0*q_good/(p0*q_good+(1-p0)*q_bad)
warning=q_bad+(q_good-q_bad)*p1
experienced=1-warning-c_standard
novice=experienced-reconstruction
intensive=1-c_intensive
print(f"posterior: {p0} -> {p1} = {float(p1):.6f}")
print(f"experienced standard={float(experienced):.6f}; novice standard={float(novice):.6f}; intensive={float(intensive):.6f}")
print("experienced chooses standard; novice chooses intensive")
assert p1==F(25,69)
assert experienced==F(113,460)
assert novice<intensive<experienced
print("weak-assessment duration in the paper example: 5 / 0.01 = 500 opportunities")
