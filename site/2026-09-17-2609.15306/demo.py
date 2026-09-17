"""Same terminal prices need not imply the same conditional dynamics.
This discrete teaching example is NOT the paper's continuous-time model.
Run: python3 demo.py
"""
good = {80: [(60, .5), (100, .5)], 120: [(100, .5), (140, .5)]}
bad = {80: [(100, .5), (140, .5)], 120: [(60, .5), (100, .5)]}
def marginal(kernel):
    out = {}
    for branches in kernel.values():
        for price, probability in branches:
            out[price] = out.get(price, 0) + .5 * probability
    return dict(sorted(out.items()))
for name, kernel in [('martingale coupling', good), ('non-martingale coupling', bad)]:
    print(name)
    print(' terminal distribution:', marginal(kernel))
    for current, branches in kernel.items():
        mean = sum(p * prob for p, prob in branches)
        print(f' S1={current}: E[S2|S1]={mean:.1f}, conditional drift={mean-current:+.1f}')
    for strike in [80, 100, 120]:
        call = sum(max(p-strike, 0)*prob for p, prob in marginal(kernel).items())
        print(f' call(K={strike})={call:.2f}')
assert marginal(good) == marginal(bad)
assert all(sum(p*q for p,q in b) == s for s,b in good.items())
assert any(sum(p*q for p,q in b) != s for s,b in bad.items())
print('PASS: identical one-time marginals, different conditional martingale checks.')
