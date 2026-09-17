"""Teaching calculation of the screening deviation, not an empirical replication."""
def evaluate(p, delta, epsilon=0.1, a=10.0, b=4.0, c=1.0):
    gamma = p * epsilon + (1-p) * (1-epsilon)
    positive = p * epsilon / gamma
    negative = (1-p) * epsilon / ((1-p)*epsilon + p*(1-epsilon))
    value = (p*epsilon*a+(1-p)*(1-epsilon)*c)/(1-delta*(1-gamma))
    good = positive*a+(1-positive)*c
    bad = negative*a+(1-negative)*c
    assert abs(value-(p*epsilon*a+(1-p)*(1-epsilon)*c+(1-gamma)*delta*value)) < 1e-10
    return value, positive, value > b and good > delta*value > bad

for p, delta in [(0.99,0.99),(0.6,0.99),(0.99,0.5)]:
    value, posterior, viable = evaluate(p,delta)
    print(f"p={p:.2f}, delta={delta:.2f}: posterior={posterior:.3f}, V={value:.3f}, screening_viable={viable}")
assert evaluate(0.99,0.99)[2]
assert not evaluate(0.6,0.99)[2]
assert not evaluate(0.99,0.5)[2]
