"""Two-group price-spillover example, not the Philippine calibration."""
def market(kappa, treated):
    tau=0.1
    strength=sum(50/(1-tau*w) for w in treated)
    price=strength**(1/(1+kappa))
    assert abs(strength/price-price**kappa) < 1e-8
    return price

for kappa in [0,1,7]:
    before=market(kappa,[0,0]); after=market(kappa,[1,0])
    ratio=after/before
    print(f"supply elasticity={kappa}: list-price ratio={ratio:.5f}, coupon-price ratio={0.9*ratio:.5f}, untreated-price ratio={ratio:.5f}")
    assert ratio>1 and 0.9*ratio<1
