"""Exact finite-set check of Example 2; no equilibrium solver."""
def normalize(groups):
    return tuple(sorted(tuple(sorted(group)) for group in groups if group))

def update(private, public):
    return normalize(set(x) & set(y) for x in private for y in public)

players = [({1,2},{3}),({1},{2,3})]
b_public = ({1,2},{3})
target = [update(player,b_public) for player in players]
print("B target:",target)
for name, rule in [("A silent",({1,2,3},)),("A reveals",({1,3},{2}))]:
    actual = [update(player,rule) for player in players]
    matches = [a == b for a,b in zip(actual,target)]
    print(name,actual,"individual matches:",matches,"joint:",all(matches))
    assert not all(matches)
assert all(update(player,b_public) == expected for player,expected in zip(players,target))
