"""Figures for manuscript v7 (Safety Science submission). Run analysis4.py first (results4.json)."""
import json
import numpy as np
import sjfig
import model4 as m

P = sjfig.PALETTE
# Grayscale: archetypes differ by gray level and marker shape, so figures read in black-and-white print.
COL = {"A": "0.0", "B": "0.40", "C": "0.62"}
MK = {"A": "o", "B": "s", "C": "^"}
ME = 0.1  # marker spacing as a fraction of the line length
LAB = {k: f"{k}: {v['name']}" for k, v in m.ARCH.items()}
R = json.load(open("results4.json"))
YRS = [2025, 2030, 2035, 2040, 2045]

# ---------------- Fig 1
fig, axes = sjfig.figure("paper", width=159, aspect=0.42, ncols=2, gridspec_kw={"width_ratios": [1.3, 1]})
ax = axes[0]
for k, p in m.ARCH.items():
    for chi, ls in ((0.0, "-"), (0.5, "--")):
        ts, S, _ = m.simulate(p, chi=chi)
        ax.plot(ts, S / S[0], color=COL[k], ls=ls, marker=MK[k], markevery=ME, ms=3.5, mfc=(COL[k] if chi == 0 else "white"), label=(LAB[k] if chi == 0 else None))
ax.plot([], [], color="0.0", ls="-", label=r"$\chi$ = 0 (filled)")
ax.plot([], [], color="0.0", ls="--", label=r"$\chi$ = 0.5 (open)")
ax.axhline(0.5, color=P["light"], lw=0.8, zorder=0)
ax.set_xlim(2025, 2045); ax.set_ylim(0, 1.05); ax.set_xticks(YRS)
ax.set_xlabel("Year"); ax.set_ylabel(r"$\mathit{R}$ = $\mathit{S}$/$\mathit{S}$(2025)")
ax.legend(loc="lower left", fontsize=7, ncol=1)
ax = axes[1]
rows = []
for k in ("A", "B", "C"):
    for chi in (0.0, 0.5):
        rows.append((k, chi))
for i, (k, chi) in enumerate(rows[::-1]):
    v = np.array(R["mc"][f"{k}_chi{chi}"]["raw"])
    ax.plot([np.percentile(v, 5), np.percentile(v, 95)], [i, i], color=COL[k], lw=2.2, solid_capstyle="butt")
    ax.plot(np.median(v), i, MK[k], color=(COL[k] if chi == 0 else "white"), mec=COL[k], mew=1.3, ms=5)
ax.set_yticks(range(len(rows)), [f"{k}, $\\chi$ = {chi:g}" for k, chi in rows[::-1]])
ax.axvline(0.5, color=P["baseline"], lw=0.8, ls="--")
ax.set_xlim(0, 1); ax.set_xlabel(r"$\mathit{R}$ in 2045 (median, 5–95%)")
sjfig.label_panels(fig, axes); sjfig.audit(fig); sjfig.save(fig, "fig1_trajectories", source="figs4.py")

# ---------------- Fig 2
fig, axes = sjfig.figure("paper", width=159, aspect=0.44, ncols=2, gridspec_kw={"width_ratios": [1.15, 1]})
ax = axes[0]
p = m.ARCH["A"]
al = np.linspace(0, 0.99, 200); ch = np.linspace(0, 1, 201)
Z = np.array([[m.steady_state(p, a, chi=c) for a in al] for c in ch])
im = ax.pcolormesh(al, ch, Z, cmap="Greys", vmin=0, vmax=2.2, shading="auto", rasterized=True)
cs = ax.contour(al, ch, Z, levels=[0.8], colors="black", linewidths=1.3, linestyles="--")
ax.contour(al, ch, np.where(Z > 0, 1, 0), levels=[0.5], colors="black", linewidths=1.3)
ax.plot([p["a0"]], [0], "o", color="white", mec="black", ms=5, clip_on=False, zorder=5)
ax.plot([p["a1"]], [0], "^", color="0.5", mec="black", ms=5, clip_on=False, zorder=5)
ax.text(0.47, 0.40, r"$\mathit{S^*}$ = 0.8", color="black", fontsize=7.5, bbox=dict(fc="white", ec="none", pad=0.6))
ax.text(0.885, 0.08, r"$\mathit{S^*}$ = 0", color="black", fontsize=7.5, rotation=90, bbox=dict(fc="white", ec="none", pad=0.6))
ax.set_xlabel(r"Automation of escalation-worthy events, $\mathit{\alpha}$")
ax.set_ylabel(r"Learning retained from automated cases, $\mathit{\chi}$")
cb = fig.colorbar(im, ax=ax, pad=0.02, fraction=0.06); cb.set_label(r"Steady state $\mathit{S^*}$ (archetype A)")
ax = axes[1]
chis = np.linspace(0, 0.8, 161)
for k, pk in m.ARCH.items():
    ax.plot(chis, [m.alpha_q(pk, 0.8, chi=c) for c in chis], color=COL[k], marker=MK[k], markevery=ME, ms=3.5, label=LAB[k])
    ax.axhline(pk["a1"], color=COL[k], lw=0.8, ls=":")
    cr = R["ceilings"][k]["chi_required_q0.8_at_a1"]
    ax.plot(cr, pk["a1"], MK[k], color="white", mec=COL[k], mew=1.3, ms=5)
ax.set_xlim(0, 0.8); ax.set_ylim(0.2, 1.0)
ax.set_xlabel(r"$\mathit{\chi}$")
ax.set_ylabel(r"Retention ceiling $\mathit{\alpha}_{0.8}$")
ax.legend(loc="upper left", fontsize=7)
sjfig.label_panels(fig, axes); sjfig.audit(fig); sjfig.save(fig, "fig2_chi_map", source="figs4.py")

# ---------------- Fig 3
fig, axes = sjfig.figure("paper", width=159, aspect=0.40, ncols=2)
ax = axes[0]
for chi, ls in ((0.0, "-"), (0.5, "--")):
    ts, S, _ = m.simulate(m.ARCH["A"], chi=chi)
    ax.plot(ts, m.ramp_mult(S), color=COL["A"], ls=ls, label=fr"A, $\chi$ = {chi:g}")
ax.set_xlim(2025, 2045); ax.set_xticks(YRS); ax.set_ylim(0.9, 3.0)
ax.set_xlabel("Year"); ax.set_ylabel(r"Ramp-up time multiplier, $\mathit{M}$")
ax.legend(loc="upper left")
ax = axes[1]
pB = m.ARCH["B"]
ts, S, mm = m.simulate(pB)
a = np.array([mm["alpha"](t) for t in ts]); f = (1 - a) / (1 - pB["a0"])
def ratio(c, Sx):
    return m.cond_failure(Sx, a, pB["a0"], c) / (1 / (1 + c))
lo = np.minimum.reduce([ratio(c, S) for c in (1, 4, 9)]); hi = np.maximum.reduce([ratio(c, S) for c in (1, 4, 9)])
ax.fill_between(ts, lo, hi, color=COL["B"], alpha=0.18, lw=0)
ax.plot(ts, ratio(4, S), color=COL["B"], label=r"$\mathit{P}$, $\mathit{c}$ = 4 (band: 1–9)")
ax.plot(ts, ratio(4, np.ones_like(S)), color=COL["B"], ls="--", label=r"$\mathit{P}$ with $\mathit{S}$ fixed")
pf = [ratio(c, S) * f for c in (1, 4, 9)]
ax.fill_between(ts, np.minimum.reduce(pf), np.maximum.reduce(pf), color="0.5", alpha=0.18, lw=0)
ax.plot(ts, ratio(4, S) * f, color="0.0", ls=":", label=r"$\mathit{Pf}$, $\mathit{c}$ = 4 (band: 1–9)")
ax.axhline(1, color=P["light"], lw=0.8, zorder=0)
ax.set_xlim(2025, 2045); ax.set_xticks(YRS); ax.set_ylim(0.6, 2.9)
ax.set_xlabel("Year"); ax.set_ylabel("Index for escalated events (2025 = 1)")
ax.legend(loc="upper left", fontsize=7)
sjfig.label_panels(fig, axes); sjfig.audit(fig); sjfig.save(fig, "fig3_loss_channels", source="figs4.py")

# ---------------- Fig 4
fig, axes = sjfig.figure("paper", width=159, aspect=0.40, ncols=2)
ax = axes[0]
cases = [("Baseline", {}, "0.0", "-"), (r"$\mathit{K}$ ×1.3", {"K": 1.3}, "0.35", "--"),
         (r"$\mathit{S_c}$ ×0.7", {"Sc": 0.7}, "0.35", "-."), (r"$\mathit{r}$ ×0.7", {"r": 0.7}, "0.35", ":"),
         (r"$\mathit{\chi}$ +0.25", {"dchi": 0.25}, "0.55", "-")]
for lab, lv, c, ls in cases:
    ts, S, _ = m.simulate(m.ARCH["A"], lever=lv)
    mk = dict(marker="o", markevery=ME, ms=3.5, mfc="white") if "chi" in lab else {}
    ax.plot(ts, S, color=c, ls=ls, label=lab, **mk)
ax.set_xlim(2025, 2045); ax.set_xticks(YRS); ax.set_ylim(0, 1.3)
ax.set_xlabel("Year"); ax.set_ylabel(r"$\mathit{S}$, archetype A")
ax.legend(loc="lower left", fontsize=7, ncol=2)
ax = axes[1]
for k in ("B", "C"):
    pk = m.ARCH[k]
    ts, S, _ = m.simulate(pk, transition=m.TRANSITION[k])
    ax.plot(ts, S, color=COL[k], marker=MK[k], markevery=ME, ms=3.5, label=f"{k}, automation and transition")
    ts, S, _ = m.simulate(pk, transition=m.TRANSITION[k], a1=pk["a0"])
    ax.plot(ts, S, color=COL[k], ls="--", marker=MK[k], markevery=ME, ms=3.5, mfc="white", label=f"{k}, transition only")
ax.set_xlim(2025, 2045); ax.set_xticks(YRS); ax.set_ylim(0, 1.1)
ax.set_xlabel("Year"); ax.set_ylabel(r"$\mathit{S}$ (reference stock = 1)")
ax.legend(loc="lower left", fontsize=7)
sjfig.label_panels(fig, axes); sjfig.audit(fig); sjfig.save(fig, "fig4_levers_transitions", source="figs4.py")
