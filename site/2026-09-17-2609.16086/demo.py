"""Recompute weighting in the paper's three-observation example."""
from itertools import permutations
from fractions import Fraction as F
import random
def canonical(cycle):return min(cycle[i:]+cycle[:i] for i in range(len(cycle)))
paths=list(permutations((0,1,2)))
values={(0,1):F(15,100),(1,2):F(20,100),(0,1,2):F(20,100)}
def basis(path):
    pairs=[(0,1),(0,2),(1,2)]
    return pairs+[canonical(path)]
def aggregate(sample,weighted):
    numerator=F(0); denominator=F(0)
    for path in sample:
        for cycle in basis(path):
            if cycle not in values:continue
            weight=F(1,6 if len(cycle)==2 else 3) if weighted else F(1)
            numerator+=weight*values[cycle]; denominator+=weight
    if denominator==0:raise ValueError("No violating cycles: mean is undefined")
    return numerator/denominator
truth=sum(values.values())/len(values)
corrected=aggregate(paths,True); naive=aggregate(paths,False)
print(f"unique-cycle mean={float(truth):.6f}; corrected all-path mean={float(corrected):.6f}; uncorrected={float(naive):.6f}")
assert corrected==truth and naive!=truth
rng=random.Random(1729)
sample=[rng.choice(paths) for _ in range(1000)]
print(f"1000 sampled paths (seed 1729): weighted mean={float(aggregate(sample,True)):.6f}")
mass={}
for path in paths:
    for cycle in basis(path):
        if cycle in values:
            weight=F(1,6 if len(cycle)==2 else 3)
            mass[values[cycle]]=mass.get(values[cycle],F(0))+weight
running=F(0)
for value,weight in sorted(mass.items()):
    running+=weight
    if running>=sum(mass.values())/2:
        median=value
        break
assert median==F(1,5)
print(f"exact weighted median over all paths = {float(median):.2f}")
