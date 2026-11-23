"""Capability-renewal model for recovery expertise under automation (corresponds to manuscript v7 (Safety Science submission); equation numbers unchanged from v5).

    dS/dt = K E(alpha) h_n(S) - (r + o(t)) S                                   (2)
    E(alpha) = (1 - alpha) + chi*alpha + eps                                     (1)  exposure
    h_n(S) = S^n / (S^n + Sc^n)                                                  mentor gate (n = 1 baseline)
    K = mu (r + o0)(1 + Sc^n) / E(alpha0)                                       (3)  reference calibration

S is measured relative to a reference sustainable stock (S = 1 at alpha0, o0, mu = 1).
Comparisons across archetypes use R(t) = S(t)/S(2025).
Entry point for all manuscript numbers: analysis4.py (writes results4.json); figs4.py draws the figures.
Equation numbers follow manuscripts v5 to v7: (1) exposure, (2) dynamics, (3) calibration, (4) steady state,
(5) extinction threshold, (6) retention ceiling, (7) local relaxation time, (8) ramp-up index, (9) escalated-event index.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

T0 = 2025.0
T1 = 2045.0

ARCH = {
    "A": dict(name="Fast-cycle", a0=0.55, a1=0.85, r=0.06, o0=0.20, Sc=0.35, S0=1.0),
    "B": dict(name="Slow high-hazard process", a0=0.45, a1=0.70, r=0.075, o0=0.033, Sc=0.50, S0=1.0),
    "C": dict(name="Craft-intensive", a0=0.20, a1=0.45, r=0.09, o0=0.05, Sc=0.80, S0=1.0),
}
TRANSITION = {"B": (0.07, 2030.0, 2040.0), "C": (0.05, 2026.0, 2036.0)}


def smooth_box(t, ts, te, w=0.8):
    return 0.5 * (np.tanh((t - ts) / w) - np.tanh((t - te) / w))


def ramp(t, a0, a1):
    x = np.clip((t - T0) / 10.0, 0, 1)
    x = 3 * x**2 - 2 * x**3
    return a0 + (a1 - a0) * x


def build(p, chi=0.0, eps=0.0, n=1, mu=1.0, lever=None, transition=None, alpha_fn=None, a1=None):
    lever = lever or {}
    a0 = p["a0"]
    a1 = p["a1"] if a1 is None else a1
    r = p["r"] * lever.get("r", 1.0)
    Sc = p["Sc"] * lever.get("Sc", 1.0)
    chi_ref = chi                                   # structural retention used for calibration
    chi = min(chi_ref + lever.get("dchi", 0.0), 1.0)  # retention after an intervention
    E0 = (1 - a0) + chi_ref * a0 + eps
    # calibration uses the reference (pre-intervention) system; interventions then act with K held
    K = mu * (p["r"] + p["o0"]) * (1 + p["Sc"] ** n) / E0
    K *= lever.get("K", 1.0)

    def alpha(t):
        return alpha_fn(t) if alpha_fn else ramp(t, a0, a1)

    def o(t):
        v = p["o0"]
        if transition:
            dO, ts, te = transition
            v += dO * smooth_box(t, ts, te)
        return v

    def E(a):
        return (1 - a) + chi * a + eps

    def rhs(t, y):
        S = max(y[0], 0.0)
        return [K * E(alpha(t)) * S**n / (S**n + Sc**n) - (r + o(t)) * S]

    return dict(alpha=alpha, o=o, E=E, rhs=rhs, K=K, r=r, Sc=Sc, chi=chi, eps=eps, n=n, E0=E0)


def simulate(p, t1=T1, npts=2001, S0=None, **kw):
    m = build(p, **kw)
    ts = np.linspace(T0, t1, npts)
    s0 = p["S0"] if S0 is None else S0
    sol = solve_ivp(m["rhs"], (T0, t1), [s0], t_eval=ts, rtol=1e-9, atol=1e-12)
    return ts, sol.y[0], m


def at(ts, y, year):
    return float(np.interp(year, ts, y))


def first_cross(ts, y, level):
    idx = np.where(y < level)[0]
    return float(ts[idx[0]]) if len(idx) else None


# ---------------- closed forms (n = 1, mu = 1, o = o0 unless stated)
def steady_state(p, alpha, chi=0.0, eps=0.0, o=None, mu=1.0):
    o = p["o0"] if o is None else o
    E0 = (1 - p["a0"]) + chi * p["a0"] + eps
    K = mu * (p["r"] + p["o0"]) * (1 + p["Sc"]) / E0
    E = (1 - alpha) + chi * alpha + eps
    return max(E * K / (p["r"] + o) - p["Sc"], 0.0)


def alpha_q(p, q, chi=0.0, eps=0.0, o=None, mu=1.0):
    """Automation level at which the steady state equals q (retention ceiling). eq. (6)."""
    o = p["o0"] if o is None else o
    E0 = (1 - p["a0"]) + chi * p["a0"] + eps
    K = mu * (p["r"] + p["o0"]) * (1 + p["Sc"]) / E0
    if chi >= 1.0:
        # exposure no longer depends on alpha: the target is met at every alpha or at none
        Sstar = (1 + eps) * K / (p["r"] + o) - p["Sc"]
        return np.inf if Sstar >= q else -np.inf
    return (1 + eps - (q + p["Sc"]) * (p["r"] + o) / K) / (1 - chi)


def chi_required(p, q=0.8, a=None):
    """Smallest chi that keeps the steady state at q when automation is a (default a1)."""
    a = p["a1"] if a is None else a
    f = lambda c: alpha_q(p, q, chi=c) - a
    if f(0.0) >= 0:
        return 0.0
    return brentq(f, 0.0, 0.999999)


def tau_local(p, Sstar, o=None):
    o = p["o0"] if o is None else o
    return (Sstar + p["Sc"]) / ((p["r"] + o) * Sstar)


def hill_existence_boundary(p, chi=0.0):
    """n = 2: positive equilibria exist iff A >= 2 Sc, A = E(alpha) K/(r + o0); returns alpha_SN."""
    Sc = p["Sc"]
    E0 = (1 - p["a0"]) + chi * p["a0"]
    # A(alpha) = E(alpha)/E0 * (1 + Sc^2); A = 2 Sc  ->  E(alpha) = 2 Sc E0/(1 + Sc^2)
    Etarget = 2 * Sc * E0 / (1 + Sc**2)
    return (1 - Etarget) / (1 - chi)


def ramp_mult(S, b=0.25):
    return (1 + b) / (np.maximum(S, 0) + b)


def cond_failure(S, a, a0, c=4.0):
    d = (1 - a0) / (1 - a)
    return d / (d + c * np.maximum(S, 0))


def chi_required_fixedK(p, q=0.8, a=None):
    """Required chi when K stays at its chi = 0 calibration (retrofit of an existing system)."""
    a = p["a1"] if a is None else a
    val = ((q + p["Sc"]) / (1 + p["Sc"]) * (1 - p["a0"]) - (1 - a)) / a
    return max(0.0, val)


def inflow_multiplier_chi(alpha, dchi):
    """Instantaneous acquisition multiplier of a chi increment at fixed S, alpha (K fixed, chi = eps = 0)."""
    return 1 + alpha * dchi / (1 - alpha)
