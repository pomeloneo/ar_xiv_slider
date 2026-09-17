"""Illustrate historical extremeness and joint exceedance, not an HR estimator.
Run: python3 demo.py
"""
history = {'A':[1, 2, 3, 4, 5], 'B':[10, 20, 30, 40, 50]}
today = {'A':4.5, 'B':12.0}
from math import sqrt
pattern = [4, 40]
current = list(today.values())
similarity=sum(x*y for x,y in zip(current,pattern))/(sqrt(sum(x*x for x in current))*sqrt(sum(x*x for x in pattern)))
for name in history:
    values=history[name]
    rank=sum(x <= today[name] for x in values)/len(values)
    binary=int(today[name] > sum(values)/len(values))
    print(f'{name}: raw={today[name]:.1f}, historical_rank={rank:.2f}, exceeds_past_mean={binary}')
    jeam=.5*max(0,similarity)+.5*rank
    print(f' JEAM teaching weight(g=0.5, fixed past pattern)={jeam:.6f}, cosine={similarity:.6f}')
joint = [(0,0),(0,1),(1,0),(1,1),(1,1)]
p_a=sum(a for a,b in joint)/len(joint)
p_b=sum(b for a,b in joint)/len(joint)
p_ab=sum(a*b for a,b in joint)/len(joint)
print(f'joint toy history: P(A)={p_a:.2f}, P(B)={p_b:.2f}, P(A and B)={p_ab:.2f}')
print(f'independence shortcut={p_a*p_b:.2f}; empirical joint={p_ab:.2f}')
changed_today=60
past_rank=sum(x<=changed_today for x in history['B'])/len(history['B'])
leaked=history['B']+[1000]
leaked_rank=sum(x<=changed_today for x in leaked)/len(leaked)
print(f'boundary: B=60 has past-only rank {past_rank:.3f}; leaking future 1000 changes rank to {leaked_rank:.3f}')
assert p_ab > p_a*p_b
assert past_rank == 1 and leaked_rank < 1
print('PASS: magnitude, historical extremeness, and co-occurrence are different quantities.')
