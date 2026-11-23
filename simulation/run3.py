import sys
import numpy as np
import sim3 as S

REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 150


def run(a, b, c, h1=True, sectors=True, p_det=0.40, design="blocks",
        do_dedup=True, reps=REPS, n_dogs=25, n_start=12, rate=0.6):
    out = dict(n1=[], n2=[], p1=[], p2=[], pv=[], g=[], dup=[], gshk=[])
    for _ in range(reps):
        dogs = S.simulate_park(h1=h1, n_dogs=n_dogs, n_start=n_start,
                               shake_per_dog_hr=rate)
        sh = S.record_shakes(dogs, a, p_det, sectors, design=design)
        raw = len(sh)
        if do_dedup:
            sh = S.dedup(sh)
        out["dup"].append(raw - len(sh))
        fo = S.record_focals(dogs, b, design=design)
        ga = S.record_gates(dogs, c)
        k1, n1, k2, n2, r = S.analyze(sh, fo)
        out["n1"].append(n1); out["n2"].append(n2); out["g"].append(len(ga))
        out["gshk"].append(sum(1 for x in ga if x["shook"]))
        if r and n1 >= 5 and n2 >= 5:
            out["p1"].append(r["p1"]); out["p2"].append(r["p2"]); out["pv"].append(r["pval"])
        else:
            out["pv"].append(np.nan)
    return out


def line(label, o, reps=REPS):
    pv = np.array(o["pv"], dtype=float)
    ok = ~np.isnan(pv)
    sig = np.sum((pv < 0.05) & ok) / reps
    p1 = 100 * np.mean(o["p1"]) if o["p1"] else float("nan")
    p2 = 100 * np.mean(o["p2"]) if o["p2"] else float("nan")
    print(f"{label:<34} shakes={np.mean(o['n1']):5.1f} focals={np.mean(o['n2']):6.1f} "
          f"gates={np.mean(o['g']):4.1f} shake%={p1:5.1f} ctrl%={p2:5.1f} "
          f"testable={100*ok.mean():5.0f}% p<.05={100*sig:5.1f}% dup={np.mean(o['dup']):4.1f}",
          flush=True)


if __name__ == "__main__":
    W = 130
    if __name__ != "__main__":
        import sys as _s; _s.exit if False else None
    print("=" * W, flush=True)
    print(f"PACKTRACK FEASIBILITY SIMULATION   17 teams of 2 · 25 dogs · 80 min collection · {REPS} simulated park-days per row", flush=True)
    print("=" * W, flush=True)
    print("shake% = behavior differed across the shake    ctrl% = behavior differed across a control window", flush=True)
    print("testable = runs where both n>=5    p<.05 = share of park-days reaching significance    dup = duplicate records\n", flush=True)

    pres, tot = [], []
    for _ in range(40):
        dogs = S.simulate_park(True)
        pres += [sum(1 for d in dogs if d["a"] <= t < d["d"]) for t in range(0, S.SESSION, 60)]
        tot.append(sum(len(d["shakes"]) for d in dogs))
    print(f"Park: {np.mean(pres):.1f} dogs present on average (peak {max(pres)}), "
          f"{np.mean(tot):.1f} shakes occur park-wide per session\n", flush=True)

    print("--- 1. THE WINDOW DESIGN. Under H0 shakes are random, so a sound test must find no difference. ---\n", flush=True)
    line("H0  app: 20 s focal (as built)", run(9, 4, 4, h1=False, design="app20"))
    line("H0  app: 10 s focal", run(9, 4, 4, h1=False, design="app10"))
    line("H0  matched 10 s blocks", run(9, 4, 4, h1=False, design="blocks"))

    print("\n--- 2. POWER under H1 (75% of shakes sit on a behavior boundary) ---\n", flush=True)
    line("H1  app: 20 s focal (as built)", run(9, 4, 4, h1=True, design="app20"))
    line("H1  app: 10 s focal", run(9, 4, 4, h1=True, design="app10"))
    line("H1  matched 10 s blocks", run(9, 4, 4, h1=True, design="blocks"))

    print("\n--- 3. TEAM ALLOCATION (matched blocks, H1) ---\n", flush=True)
    for a, b, c in [(13, 2, 2), (11, 3, 3), (10, 4, 3), (9, 4, 4), (8, 5, 4), (6, 6, 5), (4, 9, 4)]:
        line(f"A={a:2d} shake  B={b} focal  C={c} gate", run(a, b, c))

    print("\n--- 4. HOW GOOD ARE THE OBSERVERS? (A=9 B=4 C=4, sector teams) ---\n", flush=True)
    for pd in [0.20, 0.30, 0.40, 0.55]:
        line(f"park-scan detection {pd:.2f}/shake", run(9, 4, 4, p_det=pd))

    print("\n--- 5. HOW MANY SHAKES DO DOGS ACTUALLY DO? (key unknown) ---\n", flush=True)
    for r in [0.3, 0.6, 1.2, 2.0]:
        line(f"{r:.1f} shakes per dog-hour", run(9, 4, 4, rate=r))

    print("\n--- 6. BUSIER PARK: all 25 dogs present most of the session ---\n", flush=True)
    line("25 dogs, 20 present at start", run(9, 4, 4, n_dogs=25, n_start=20))
    line("25 dogs, 20 at start, 1.2/dog-hr", run(9, 4, 4, n_dogs=25, n_start=20, rate=1.2))

    print("\n--- 7. DUPLICATE RECORDS from whole-park scanning (A=9) ---\n", flush=True)
    line("sectors assigned", run(9, 4, 4, sectors=True))
    line("whole park, deduped", run(9, 4, 4, sectors=False, do_dedup=True))
    line("whole park, NOT deduped (page now)", run(9, 4, 4, sectors=False, do_dedup=False))

    print("\n--- 8. FALSE POSITIVES, recommended setup ---\n", flush=True)
    line("H0  A=9 B=4 C=4 matched blocks", run(9, 4, 4, h1=False, design="blocks", reps=REPS))

    print("\n--- 9. GATE CAPACITY (5 min trials) ---\n", flush=True)
    for c in [1, 2, 3, 4]:
        got, arr, shk = [], [], []
        for _ in range(200):
            dogs = S.simulate_park(True)
            g = S.record_gates(dogs, c)
            got.append(len(g)); shk.append(sum(1 for x in g if x["shook"]))
            arr.append(sum(1 for d in dogs if d["a"] > 0))
        print(f"  {c} gate team(s): {np.mean(got):4.1f} of {np.mean(arr):4.1f} arrivals captured, "
              f"{np.mean(shk):4.1f} shook", flush=True)
