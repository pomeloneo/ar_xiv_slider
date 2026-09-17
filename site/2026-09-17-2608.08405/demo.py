"""Accumulation and common-effect cancellation in a synthetic capacity model.
Run: python3 demo.py
"""
from statistics import mean
a=.8
steady_private_erosion=2
for length in (1,5,20):
    path=[steady_private_erosion*(1-a**t) for t in range(1,length+1)]
    g=mean(1-a**t for t in range(1,length+1))
    finite=mean(path)
    print(f'L={length}: average_erosion={finite:.6f}; G={g:.6f}; corrected={finite/g:.6f}')
    assert abs(finite/g-steady_private_erosion)<1e-12
for crowding in (0,5):
    market_shock=3
    control=10+market_shock-crowding
    treated=10+market_shock-crowding-2
    print(f'common_crowding={crowding}: control={control}, treated={treated}, within_date_difference={treated-control}')
true_g=mean(1-a**t for t in range(1,6))
wrong_g=mean(1-.5**t for t in range(1,6))
print(f'boundary: correcting with wrong persistence gives {2*true_g/wrong_g:.6f}, true steady effect=2')
print('PASS: common shocks and common crowding both cancel; correction depends on the assumed kernel.')
