"""
Feasibility simulation for the PackTrack dog-park lab.

Behavior streams are per-second category arrays. A shake sits ON a behavior
boundary under H1, so an observer coding "what it was doing as the shake
began" reports the activity being ended, and "what it did next" reports the
new one. The control must therefore also compare two adjacent blocks of time.

Window designs compared:
  "app20"   shake: instant at shake   vs main cat in [t, t+10]
            focal: instant at t       vs instant at t+20      (as currently built)
  "app10"   same shake coding, focal instants 10 s apart
  "blocks"  shake: main cat in [t-10, t) vs main cat in [t, t+10)
            focal: main cat in [t, t+10) vs main cat in [t+10, t+20)
            (both compare two adjacent 10 s blocks: matched by construction)
"""
import math
import numpy as np

RNG = np.random.default_rng(20261123)

CATS = ["PLAY", "CHG", "CAS", "PER", "SELF", "ALN"]
NC = len(CATS)
OCC = np.array([0.22, 0.04, 0.17, 0.12, 0.08, 0.37])
BOUT = np.array([40.0, 10.0, 18.0, 25.0, 14.0, 55.0])

SESSION = 80 * 60
MEAN_STAY = 45 * 60
P_ARR_SHAKE = 0.45
NS_RATE = 0.18          # observer did not see the lead-in
OFF = 255

PAD = 60                # seconds of padding each side of the array


def make_dog(arrive, depart):
    arr = np.full(SESSION + 2 * PAD, OFF, dtype=np.uint8)
    a, d = int(arrive) + PAD, int(depart) + PAD
    trans, t = [], a
    cat = RNG.choice(NC, p=OCC)
    while t < d:
        dur = max(1, int(RNG.exponential(BOUT[cat])))
        end = min(t + dur, d)
        arr[t:end] = cat
        t = end
        if t < d:
            trans.append(t)
            w = OCC.copy(); w[cat] = 0.0
            cat = RNG.choice(NC, p=w / w.sum())
    return arr, trans


def simulate_park(h1=True, n_dogs=25, n_start=12, shake_per_dog_hr=0.6,
                  p_trans=0.75):
    rate = shake_per_dog_hr / 3600.0
    dogs = []
    for i in range(n_dogs):
        arrive = 0.0 if i < n_start else RNG.uniform(0, SESSION * 0.85)
        depart = min(arrive + RNG.exponential(MEAN_STAY), SESSION)
        if depart - arrive < 240:
            depart = min(arrive + 240, SESSION)
        arr, trans = make_dog(arrive, depart)

        n = RNG.poisson(rate * (depart - arrive))
        shakes = []
        if h1 and trans:
            k = RNG.binomial(n, p_trans)
            if k:
                picks = RNG.choice(trans, size=min(k, len(trans)), replace=False)
                shakes += [int(p) for p in picks]
            n -= min(k, len(trans))
        shakes += [int(RNG.uniform(arrive, depart)) + PAD for _ in range(max(n, 0))]

        arr_shake = None
        if arrive > 0 and RNG.random() < P_ARR_SHAKE:
            cand = int(arrive + RNG.exponential(45.0))
            if cand < min(arrive + 300, depart):
                arr_shake = cand
                shakes.append(cand + PAD)

        lo, hi = int(arrive) + PAD + 12, int(depart) + PAD - 12
        shakes = sorted(s for s in shakes if lo <= s <= hi)
        dogs.append(dict(id=i, a=int(arrive), d=int(depart), arr=arr,
                         shakes=shakes, arr_shake=arr_shake,
                         greeters=int(min(RNG.poisson(1.3), 3))))
    return dogs


def main_cat(arr, t0, t1):
    seg = arr[max(t0, 0):t1]
    seg = seg[seg != OFF]
    if seg.size == 0:
        return None
    return int(np.bincount(seg, minlength=NC).argmax())


def inst(arr, t):
    v = int(arr[t])
    return None if v == OFF else v


# ----------------------------------------------------------------------
def record_shakes(dogs, n_teams, p_detect_park, sectors, design="blocks"):
    """Team A. Sector teams watch few dogs, so they detect far more."""
    rows = []
    p_sector = min(0.85, p_detect_park * 2.0)
    for d in dogs:
        for st in d["shakes"]:
            if sectors:
                watchers = [d["id"] % max(n_teams, 1)]
                p = p_sector
            else:
                watchers = list(range(n_teams))
                p = p_detect_park
            for w in watchers:
                if RNG.random() > p:
                    continue
                if design == "blocks":
                    pre = main_cat(d["arr"], st - 10, st)
                    post = main_cat(d["arr"], st, st + 10)
                elif design == "inst":
                    pre = inst(d["arr"], st - 2)
                    post = inst(d["arr"], st + 10)
                else:
                    pre = main_cat(d["arr"], st - 8, st - 1)
                    post = main_cat(d["arr"], st + 1, st + 11)
                if pre is None or post is None:
                    continue
                rows.append(dict(dog=d["id"], t=st, obs=w,
                                 pre="NS" if RNG.random() < NS_RATE else pre,
                                 post=post))
    return rows


def record_focals(dogs, n_teams, design="blocks", sec_per=60.0, duty=0.65):
    rows = []
    per_team = int(SESSION * duty / sec_per)
    starts = np.array([d["a"] for d in dogs])
    ends = np.array([d["d"] for d in dogs])
    span = 20
    for w in range(n_teams):
        ts = RNG.integers(0, SESSION - span - 1, size=per_team)
        for t in ts:
            ok = np.where((starts <= t) & (ends > t + span))[0]
            if ok.size == 0:
                continue
            d = dogs[int(RNG.choice(ok))]
            tp = int(t) + PAD
            if design == "blocks":
                b0 = main_cat(d["arr"], tp, tp + 10)
                b1 = main_cat(d["arr"], tp + 10, tp + 20)
            elif design in ("app10", "inst"):
                b0, b1 = inst(d["arr"], tp), inst(d["arr"], tp + 10)
            else:
                b0, b1 = inst(d["arr"], tp), inst(d["arr"], tp + 20)
            if b0 is None or b1 is None:
                continue
            rows.append(dict(dog=d["id"], t=int(t), obs=100 + w, b0=b0, b20=b1,
                             shook=any(tp <= s <= tp + span for s in d["shakes"])))
    return rows


def record_gates(dogs, n_teams, trial=300):
    arrivals = sorted([d for d in dogs if d["a"] > 0], key=lambda x: x["a"])
    free = [0] * n_teams
    rows = []
    for d in arrivals:
        for i in range(n_teams):
            if free[i] <= d["a"]:
                shook = d["arr_shake"] is not None
                lat = (d["arr_shake"] - d["a"]) if shook else None
                rows.append(dict(dog=d["id"], shook=shook, lat=lat,
                                 greeters=d["greeters"]))
                free[i] = d["a"] + (lat if shook else trial)
                break
    return rows


def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def two_prop(k1, n1, k2, n2):
    if n1 < 1 or n2 < 1:
        return None
    p1, p2 = k1 / n1, k2 / n2
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return dict(p1=p1, p2=p2, z=0.0, pval=1.0)
    z = (p1 - p2) / se
    return dict(p1=p1, p2=p2, z=z, pval=2 * (1 - phi(abs(z))))


def dedup(rows):
    keep, last = [], {}
    for r in sorted(rows, key=lambda r: (r["dog"], r["t"])):
        prev = last.get(r["dog"])
        if prev is not None and r["t"] - prev <= 20:
            continue
        last[r["dog"]] = r["t"]
        keep.append(r)
    return keep


def analyze(shakes, focals):
    sv = [r for r in shakes if r["pre"] != "NS"]
    n1 = len(sv)
    k1 = sum(1 for r in sv if r["pre"] != r["post"])
    n2 = len(focals)
    k2 = sum(1 for r in focals if r["b0"] != r["b20"])
    return k1, n1, k2, n2, two_prop(k1, n1, k2, n2)
