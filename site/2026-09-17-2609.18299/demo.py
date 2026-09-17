"""Exact WF and checks of the paper's analytic QP examples; not a general QP solver."""
from fractions import Fraction as F
def wf(p):
    n=len(p); x=[[F(0) for _ in range(n)] for _ in range(n)]
    for j in range(n):
        while sum(row[j] for row in x)<1:
            active=[i for i in range(n) if x[i][j]<p[i][j]]
            if not active:break
            step=min(min(p[i][j]-x[i][j] for i in active),(1-sum(row[j] for row in x))/len(active))
            for i in active:x[i][j]+=step
    while any(sum(row)<1 for row in x):
        rows=[i for i in range(n) if sum(x[i])<1]
        cols=[j for j in range(n) if sum(row[j] for row in x)<1]
        step=min(min((1-sum(x[i]))/len(cols) for i in rows),min((1-sum(row[j] for row in x))/len(rows) for j in cols))
        for i in rows:
            for j in cols:x[i][j]+=step
    return x
def overlap(actual,target):return sum(min(x,p) for x,p in zip(actual,target))
def check(name,p,x):
    n=len(p)
    assert all(sum(row)==1 for row in x)
    assert all(sum(row[j] for row in x)==1 for j in range(n))
    values=[overlap(row,target) for row,target in zip(x,p)]
    assert all(values[i]>=overlap(x[j],p[i]) for i in range(n) for j in range(n))
    print(name,"overlap="+str([str(v) for v in values]),"sum="+str(sum(values)),"min="+str(min(values)))
p=[[F(1),F(0),F(0)],[F(1,2),F(1,2),F(0)],[F(1,2),F(1,2),F(0)]]
q=[[F(1,2),F(0),F(1,2)],[F(1,4),F(1,2),F(1,4)],[F(1,4),F(1,2),F(1,4)]]
check("example 1 WF",p,wf(p));check("example 1 QP",p,q)
p2=[[F(0),F(2,5),F(3,5)],[F(2,5),F(2,5),F(1,5)],[F(2,5),F(2,5),F(1,5)]]
q2=[[F(1,5),F(1,5),F(3,5)],[F(2,5),F(2,5),F(1,5)],[F(2,5),F(2,5),F(1,5)]]
check("example 4 WF",p2,wf(p2));check("example 4 QP",p2,q2)
