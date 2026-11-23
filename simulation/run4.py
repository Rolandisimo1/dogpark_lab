import numpy as np
import sim3 as S
from run3 import run, line

REPS = 200

print("\n--- 6. BUSIER PARK: more dogs present at once ---\n", flush=True)
line("25 dogs, 12 present at start", run(9, 4, 4, n_dogs=25, n_start=12, reps=REPS), REPS)
line("25 dogs, 20 present at start", run(9, 4, 4, n_dogs=25, n_start=20, reps=REPS), REPS)
line("35 dogs, 20 at start", run(9, 4, 4, n_dogs=35, n_start=20, reps=REPS), REPS)

print("\n--- 7. DUPLICATE RECORDS from whole-park scanning (A=9 teams) ---\n", flush=True)
line("sectors assigned", run(9, 4, 4, sectors=True, reps=REPS), REPS)
line("whole park, deduped", run(9, 4, 4, sectors=False, do_dedup=True, reps=REPS), REPS)
line("whole park, NOT deduped", run(9, 4, 4, sectors=False, do_dedup=False, reps=REPS), REPS)

print("\n--- 8. FALSE POSITIVES, recommended setup (should be near 5%) ---\n", flush=True)
line("H0, matched blocks, sectors", run(9, 4, 4, h1=False, design="blocks", reps=REPS), REPS)

print("\n--- 9. GATE CAPACITY (5 min trials) ---\n", flush=True)
for c in [1, 2, 3, 4]:
    got, arr, shk = [], [], []
    for _ in range(200):
        dogs = S.simulate_park(True)
        g = S.record_gates(dogs, c)
        got.append(len(g)); shk.append(sum(1 for x in g if x["shook"]))
        arr.append(sum(1 for d in dogs if d["a"] > 0))
    print(f"  {c} gate team(s): {np.mean(got):4.1f} of {np.mean(arr):4.1f} arrivals "
          f"captured, {np.mean(shk):4.1f} shook", flush=True)

print("\n--- 10. THE GATE TEST: entering dogs vs baseline 5 min shake probability ---", flush=True)
print("Baseline comes from the focal windows. This test has a true denominator.\n", flush=True)
for rate in [0.6, 1.2]:
    sig, n1s, p1s, p2s = 0, [], [], []
    for _ in range(300):
        dogs = S.simulate_park(h1=True, shake_per_dog_hr=rate)
        ga = S.record_gates(dogs, 3)
        fo = S.record_focals(dogs, 4)
        k1 = sum(1 for x in ga if x["shook"]); n1 = len(ga)
        # baseline: shakes per dog-second from focal effort, scaled to 300 s
        dog_sec = len(fo) * 20
        n_sh = sum(1 for x in fo if x["shook"])
        p_base = 1 - np.exp(-(n_sh / max(dog_sec, 1)) * 300) if dog_sec else 0
        k2 = int(round(p_base * n1 * 4)); n2 = n1 * 4     # pseudo-control of 4x size
        r = S.two_prop(k1, n1, k2, n2)
        n1s.append(n1); p1s.append(k1 / max(n1, 1)); p2s.append(p_base)
        if r and r["pval"] < 0.05 and n1 >= 5:
            sig += 1
    print(f"  {rate:.1f} shakes/dog-hr: gate n={np.mean(n1s):4.1f}, "
          f"{100*np.mean(p1s):4.1f}% of entering dogs shook vs {100*np.mean(p2s):4.1f}% "
          f"baseline in any 5 min -> significant in {100*sig/300:.0f}% of park-days", flush=True)

print("\n--- 11. POOLING SECTIONS / YEARS (matched blocks, 0.6/dog-hr) ---\n", flush=True)
for mult, lab in [(1, "one class"), (2, "two sections"), (3, "three sections"), (4, "four sections")]:
    sig = 0
    for _ in range(300):
        K1 = N1 = K2 = N2 = 0
        for _ in range(mult):
            dogs = S.simulate_park(True)
            sh = S.dedup(S.record_shakes(dogs, 9, 0.40, True))
            fo = S.record_focals(dogs, 4)
            k1, n1, k2, n2, _ = S.analyze(sh, fo)
            K1 += k1; N1 += n1; K2 += k2; N2 += n2
        r = S.two_prop(K1, N1, K2, N2)
        if r and N1 >= 5 and r["pval"] < 0.05:
            sig += 1
    print(f"  {lab:<16} pooled shake n grows ~{mult*8}  ->  significant in {100*sig/300:.0f}% of attempts", flush=True)
