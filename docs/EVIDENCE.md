# Claim-to-evidence map

| Claim | Inspect | Reproduce |
|---|---|---|
| The paper states a < 1 kpc rule and names eight solitary pulsars | `sources/chakrabarti2026_quotes.md` | Read the quotation |
| The frame convention is right | `results/selection.json` → `frame_check` | `python3 scripts/check_selection.py` |
| Seven of the eight named pulsars are outside 1 kpc; four can never be inside | `named`, `named_that_can_never_be_inside` | `python3 scripts/check_selection.py` |
| The result does not depend on the solar position | `frame_scan` | `python3 scripts/check_selection.py` |
| The written rule selects J1801−1417 and J2033+1734, which are not used | `selected_by_written_rule` | `python3 scripts/check_selection.py` |
| The catalogue accelerations respond to gravity by R ≠ 1 | `results/inputs.json` → `named[].gravity_response_R` | `python3 scripts/check_inputs.py` |
| 23 of 52 v3 magnetic fields cannot be reproduced from their rows; 0 of 59 in v1 | `v1`, `v3` | `python3 scripts/check_inputs.py` |
| The subhalo would pull the Sun by 0.144 mm/s/yr, which Eq. 8 omits | `solar_term` | `python3 scripts/check_selection.py` |

## Primary sources

1. S. Chakrabarti, P. Chang, S. Profumo, P. Craig, *Constraints on a dark matter sub-halo near the Sun from pulsar timing*, [Phys. Rev. Lett. 136, 041201 (2026)](https://doi.org/10.1103/29xz-nt5z); accepted version [arXiv:2507.16932v3](https://arxiv.org/abs/2507.16932v3) (2 December 2025). Abstract, selection paragraph, Table 1 and Eqs. 7–8.
2. T. Donlon, S. Chakrabarti, S. Vanderwaal, L. M. Widrow, S. Ransom, E. Ramirez-Ruiz, *Empirical Modeling of Magnetic Braking in Millisecond Pulsars to Measure the Local Dark Matter Density and Effects of Orbiting Satellite Galaxies*, Phys. Rev. D 111, 103036 (2025), [arXiv:2501.03409](https://arxiv.org/abs/2501.03409). The paper's Reference [13] for the solitary-pulsar accelerations.
3. Catalogue files `v1/data.csv` and `v3/data.csv` in [thomasdonlon/Empirical_Model_MSP_Spindown_Accels at 6cb4e31](https://github.com/thomasdonlon/Empirical_Model_MSP_Spindown_Accels/tree/6cb4e31f6b2e732f5973b024634507c2e4f59988). SHA-256 values are in `scripts/fetch_catalogue.py` and `provenance/SOURCES.json`.
