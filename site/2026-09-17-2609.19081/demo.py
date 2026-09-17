"""Didactic sensitivity scale; no sampling inference or case-study replication."""
treated=[100,102,112]
for name,control in [("post shock",[80,82,92]),("no shock",[80,82,84])]:
    pre_t=treated[1]-treated[0]; pre_c=control[1]-control[0]
    post_t=treated[2]-treated[1]; post_c=control[2]-control[1]
    did=post_t-post_c; alternative=post_t-pre_t
    gap=abs(post_c-pre_t)
    print(f"{name}: pretrend gap={pre_t-pre_c}, DID={did}, own-trend effect={alternative}, discordance={gap}")
    for m in [0,0.5,1]:print(f"  M={m}: teaching identified range=[{did-m*gap:g}, {did+m*gap:g}]")
    assert pre_t==pre_c
    if name=="post shock":assert gap==8 and did==0
