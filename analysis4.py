"""All numerical results for manuscript v7 (Safety Science submission). Run: python3 analysis4.py (writes results4.json)."""
import json
import numpy as np
import model4 as m

A = m.ARCH
res = {"params": A, "transition_input": {k: list(v) for k, v in m.TRANSITION.items()}}

# R1 baseline and chi scenarios, R(2045) and timing
base = {}
for k, p in A.items():
    row = {}
    for chi in (0.0, 0.25, 0.5):
        ts, S, _ = m.simulate(p, chi=chi)
        R = S / S[0]
        row[f"chi{chi}"] = dict(R2035=round(m.at(ts, R, 2035), 10), R2045=round(m.at(ts, R, 2045), 10),
                                cross05=m.first_cross(ts, R, 0.5))
    row["tau0"] = round((1 + p["Sc"]) / (p["r"] + p["o0"]), 10)
    Sfin = m.steady_state(p, p["a1"])
    row["Sstar_a1"] = round(Sfin, 10)
    row["tau_at_a1"] = round(m.tau_local(p, Sfin), 10) if Sfin > 0 else None
    row["alpha_c"] = round(m.alpha_q(p, 0.0), 10)
    base[k] = row
res["baseline"] = base

# depleted start for C (S0 = 0.6), reported as R and as S
ts, S, _ = m.simulate(A["C"], S0=0.6)
res["C_depleted"] = dict(S2045=round(m.at(ts, S, 2045), 10), R2045=round(m.at(ts, S, 2045) / 0.6, 10))

# R2 retention ceilings over q and chi; required chi
ceil = {}
for k, p in A.items():
    grid = {}
    for chi in (0.0, 0.5):
        for q in (0.6, 0.8, 0.9):
            grid[f"chi{chi}_q{q}"] = round(m.alpha_q(p, q, chi=chi), 10)
    b0 = m.alpha_q(p, 0.8) - p["a0"]; b5 = m.alpha_q(p, 0.8, chi=0.5) - p["a0"]
    grid["budget_chi0_q0.8"] = round(b0, 10)
    grid["budget_chi0.5_q0.8"] = round(b5, 10)
    grid["budget_ratio_chi0.5"] = round(b5 / b0, 10)
    grid["chi_required_fixedK_q0.8_at_a1"] = round(m.chi_required_fixedK(p, 0.8), 10)
    grid["chi_required_q0.8_at_a1"] = round(m.chi_required(p, 0.8), 10)
    grid["alpha_c_chi0"] = round(m.alpha_q(p, 0.0), 10)
    grid["alpha_c_chi0.5"] = round(m.alpha_q(p, 0.0, chi=0.5), 10)
    ceil[k] = grid
res["ceilings"] = ceil

# R3 loss channels
p = A["A"]
lc = {}
for chi in (0.0, 0.5):
    ts, S, mm = m.simulate(p, chi=chi)
    lc[f"A_M2045_chi{chi}"] = round(float(m.ramp_mult(m.at(ts, S, 2045))), 10)
for b in (0.1, 0.5):
    ts, S, _ = m.simulate(p)
    lc[f"A_M2045_b{b}"] = round(float(m.ramp_mult(m.at(ts, S, 2045), b=b)), 10)
pB = A["B"]
ts, S, mm = m.simulate(pB)
aB = np.array([mm["alpha"](t) for t in ts])
for c in (1.0, 4.0, 9.0):
    P = m.cond_failure(S, aB, pB["a0"], c)
    Pfix = m.cond_failure(np.ones_like(S), aB, pB["a0"], c)
    P0 = 1 / (1 + c)
    f = (1 - aB) / (1 - pB["a0"])
    lc[f"B_P_ratio_c{c:g}"] = round(float(P[-1] / P0), 10)
    lc[f"B_Pfix_ratio_c{c:g}"] = round(float(Pfix[-1] / P0), 10)
    lc[f"B_Pf_ratio_c{c:g}"] = round(float(P[-1] * f[-1] / P0), 10)
res["loss"] = lc

# R4 transitions counterfactual (B, C)
tr = {}
for k in ("B", "C"):
    pk = A[k]
    out = {}
    for lab, kw in [("auto_and_transition", dict(transition=m.TRANSITION[k])),
                    ("transition_only", dict(transition=m.TRANSITION[k], a1=pk["a0"])),
                    ("auto_only", dict())]:
        ts, S, _ = m.simulate(pk, **kw)
        out[lab] = dict(R2045=round(m.at(ts, S, 2045), 10), Rmin=round(float(S.min()), 10))
    tr[k] = out
res["transition_results"] = tr

# R5 structural sensitivity (R2045) and Hill existence boundaries
struct = {}
for k, p in A.items():
    row = {}
    for lab, kw in [("base", {}), ("eps0.1", {"eps": 0.1}), ("eps0.2", {"eps": 0.2}),
                    ("chi0.25", {"chi": 0.25}), ("chi0.5", {"chi": 0.5}),
                    ("mu0.9", {"mu": 0.9}), ("mu1.1", {"mu": 1.1}), ("n2", {"n": 2})]:
        ts, S, _ = m.simulate(p, **kw)
        row[lab] = round(m.at(ts, S, 2045) / S[0], 10)
    row["alphaSN_n2"] = round(m.hill_existence_boundary(p), 10)
    row["alpha_c_eps0.2"] = round(m.alpha_q(p, 0.0, eps=0.2), 10)
    struct[k] = row
res["structural"] = struct

# R6 Monte Carlo (scenario ranges under assumed distributions)
rng = np.random.default_rng(7)
mc = {}
for chi in (0.0, 0.5):
    for k, p in A.items():
        vals = []
        for _ in range(1000):
            q = dict(p)
            q["r"] = p["r"] * rng.uniform(0.7, 1.3)
            q["o0"] = p["o0"] * rng.uniform(0.7, 1.3)
            q["Sc"] = p["Sc"] * rng.uniform(0.7, 1.3)
            q["a0"] = p["a0"] + rng.uniform(-0.05, 0.05)
            q["a1"] = min(p["a1"] + rng.uniform(-0.05, 0.05), 0.97)
            mu = rng.uniform(0.9, 1.1)
            ts, S, _ = m.simulate(q, chi=chi, mu=mu, npts=201)
            vals.append(m.at(ts, S, 2045) / S[0])
        v = np.array(vals)
        mc[f"{k}_chi{chi}"] = dict(median=round(float(np.median(v)), 10), p05=round(float(np.percentile(v, 5)), 10),
                                   p95=round(float(np.percentile(v, 95)), 10), raw=[round(float(x), 6) for x in v])
res["mc"] = mc

# R7 levers (specified finite perturbations; unequal sizes and costs) and ranking stability
LEV = {"K x1.3": {"K": 1.3}, "Sc x0.7": {"Sc": 0.7}, "r x0.7": {"r": 0.7}, "chi +0.25": {"dchi": 0.25}}
lev = {}
for k, p in A.items():
    row = {}
    ts, S, _ = m.simulate(p); row["base"] = round(m.at(ts, S, 2045), 10)
    for lab, lv in LEV.items():
        ts, S, _ = m.simulate(p, lever=lv); row[lab] = round(m.at(ts, S, 2045), 10)
    lev[k] = row
res["levers"] = lev
size = {}
for k, p in A.items():
    row = {}
    for d in (0.05, 0.10, 0.25):
        ts, S, _ = m.simulate(p, lever={"dchi": d}); row[f"dchi{d}"] = round(m.at(ts, S, 2045), 10)
    row["K x1.3"] = lev[k]["K x1.3"]
    row["inflow_chi0.25_at_a0"] = round(m.inflow_multiplier_chi(p["a0"], 0.25), 10)
    row["inflow_chi0.25_at_a1"] = round(m.inflow_multiplier_chi(p["a1"], 0.25), 10)
    size[k] = row
res["lever_size"] = size
res["crossover_alpha_p0.3_dchi0.25"] = round(0.3 / (0.3 + 0.25), 10)
# ranking stability: fraction of draws where each lever is top
rng = np.random.default_rng(11)
stab = {}
for k, p in A.items():
    wins = {lab: 0 for lab in LEV}
    wins3 = {lab: 0 for lab in LEV if lab != "chi +0.25"}
    N = 300
    for _ in range(N):
        q = dict(p)
        q["r"] = p["r"] * rng.uniform(0.7, 1.3)
        q["o0"] = p["o0"] * rng.uniform(0.7, 1.3)
        q["Sc"] = p["Sc"] * rng.uniform(0.7, 1.3)
        vals = {}
        for lab, lv in LEV.items():
            ts, S, _ = m.simulate(q, lever=lv, npts=101)
            vals[lab] = S[-1]
        wins[max(vals, key=vals.get)] += 1
        v3 = {kk: vv for kk, vv in vals.items() if kk != "chi +0.25"}
        wins3[max(v3, key=v3.get)] += 1
    stab[k] = {"all": {lab: round(w / N, 10) for lab, w in wins.items()},
               "conventional": {lab: round(w / N, 10) for lab, w in wins3.items()}}
res["lever_top_share"] = stab

# R8 recovery after reverting automation in 2045 (S0 = 1 archetypes)
rec = {}
from scipy.integrate import solve_ivp
for k, p in A.items():
    ts, S, _ = m.simulate(p)                       # 2025-2045 on the assumed path (ends exactly at 2045)
    S45 = S[-1]
    mm = m.build(p, alpha_fn=lambda t, p=p: p["a0"])
    ev = lambda t, y: y[0] - 0.9
    ev.terminal = True; ev.direction = 1
    sol = solve_ivp(mm["rhs"], (2045.0, 2145.0), [S45], events=ev, rtol=1e-10, atol=1e-12)
    tr_ = sol.t_events[0]
    rec[k] = dict(R2045=round(float(S45), 10), years_to_0p9=round(float(tr_[0] - 2045.0), 10) if len(tr_) else None)
res["recovery"] = rec

json.dump(res, open("results4.json", "w"), indent=1)
if __name__ == "__main__":
    slim = {k: v for k, v in res.items() if k != "mc"}
    print(json.dumps(slim, indent=1))
    print({k: {kk: vv for kk, vv in v.items() if kk != "raw"} for k, v in mc.items()})
