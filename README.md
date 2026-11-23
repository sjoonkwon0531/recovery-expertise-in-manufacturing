# Recovery expertise in manufacturing: a minimal capability-renewal model

Code and outputs that reproduce every number and figure in the manuscript "Automation and the renewal of abnormal-situation recovery expertise in manufacturing: a minimal capability-renewal model" (submitted).

The model describes how the capability to recover abnormal situations is renewed when automation resolves a share α of escalation-worthy events and an automatically resolved case retains a fraction χ of the learning value of a human-handled one:

    dS/dt = K E(α) h_n(S) − (r + o) S,   E(α) = (1 − α) + χα + ε,   h_n(S) = Sⁿ/(Sⁿ + S_cⁿ)

## Environment
Python 3.12; NumPy ≥ 2.0; SciPy ≥ 1.13; Matplotlib ≥ 3.9 (see `requirements.txt`). Figures use the first available font in the order defined in `sjfig.py`: Arial Narrow, Liberation Sans Narrow (metric-compatible), then common fallbacks. The figures in `figures/` were drawn with Liberation Sans Narrow; with another font, regenerate and check legend placement.

## Commands
```
pip install -r requirements.txt
python3 analysis4.py   # entry point: computes every number in the manuscript, writes results4.json
python3 figs4.py       # draws Figs. 1-4 (grayscale) from model4.py and results4.json into figures/
```

## Files
- `model4.py`: model equations (1)–(9), calibration (3), closed forms (4)–(7), saddle-node boundary for n = 2 (A3), fixed-K required retention (10), retention inflow multiplier (11)
- `analysis4.py`: scenario, sensitivity, Monte Carlo (seed 7, 1,000 draws per case) and perturbation-ranking (seed 11, 300 draws) computations
- `figs4.py`, `sjfig.py`: figures at final print size (159 mm wide)
- `results4.json`: numerical results referenced in the text
- `figures/`: Figs. 1–4 as PDF (vector) and PNG

## Notes
- S is measured relative to a reference sustainable stock (S = 1 at α0, o0, μ = 1). Comparisons use R = S/S(2025).
- Archetype parameters are scenario assumptions informed by public context; they are not estimates.
- Scenario ranges reflect assumed parameter distributions; they are not probabilities of real outcomes.
- The code was developed with the assistance of a generative AI tool, as described in the manuscript's Methods.
