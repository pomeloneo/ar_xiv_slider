"""Power-law tail arithmetic, not a fit to private insurance data.
Run: python3 demo.py
"""
from math import exp
alpha=1.74
for multiplier in (1,10,100):
    relative_probability=multiplier**(1-alpha)
    toy_return_period=4.2/relative_probability
    print(f'multiplier={multiplier}: relative_tail={relative_probability:.6f}, toy_return_period={toy_return_period:.2f} years')
correct=10**(1-alpha)
misprint=10**(-alpha)
print(f'equation check: 10^(-0.74)={correct:.6f}; 10^(-1.74)={misprint:.6f}')
for a in (1.5,1.74,2.1):
    print(f'sensitivity alpha={a}: tail_ratio_at_100={100**(1-a):.6f}')
rate=1/206
print(f'Poisson teaching assumption: probability of >=1 event within 10 years={1-exp(-10*rate):.4%}')
assert abs(correct/misprint-10)<1e-10
print('PASS: density exponent and tail exponent differ by one; return periods are not schedules.')
