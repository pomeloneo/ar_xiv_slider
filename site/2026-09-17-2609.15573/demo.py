"""Local evaluation of the complete-information marginal expression (Eq. 7)."""
def marginal(theta,network=True):
    local=-1.0
    external=0.2*theta*10*1.0 if network else 0.0
    return local,external,local+external
for theta,network in [(1,True),(0.2,True),(1,False)]:
    local,external,total=marginal(theta,network)
    print(f"ability={theta}, network={network}: local={local:.1f}, external={external:.1f}, total={total:.1f}, positive={total>0}")
assert marginal(1)[2]>0
assert marginal(0.2)[2]<0
assert marginal(1,False)[2]<0
