"""Inventory accounting under persistent flow; no RL training or LOB replication.
Run: python3 demo.py
"""
def run(flow,adaptive):
    inventory=cash=0
    price=100
    fills=0
    for t,direction in enumerate(flow):
        bid=price-.5
        # Teacher's rule: after three consecutive sells, stop buying.
        recent=flow[max(0,t-3):t]
        pause=adaptive and len(recent)==3 and all(x==-1 for x in recent)
        if direction==-1 and not pause:
            inventory+=1
            cash-=bid
            fills+=1
        elif direction==1 and inventory>0:
            inventory-=1
            cash+=price+.5
            fills+=1
        price+=direction
    return inventory,cash+inventory*price,fills
for name,flow in [('persistent selling',[-1]*8),('reversal',[-1]*4+[1]*4)]:
    for adaptive in (False,True):
        q,pnl,fills=run(flow,adaptive)
        print(f'{name}, adaptive={adaptive}: inventory={q}, marked_PnL={pnl:.2f}, fills={fills}')
assert run([-1]*8,True)[1] > run([-1]*8,False)[1]
print('PASS: a spread capture is not net profit when inventory is repriced.')
print('Boundary: pausing quotes also changes participation; this hand-coded rule does not reproduce RLMM or prove robust profitability.')
