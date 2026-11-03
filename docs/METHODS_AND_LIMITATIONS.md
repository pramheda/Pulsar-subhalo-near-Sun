# Methods and limits of the inference

## Frame

Pulsars are placed from the catalogue's Galactic longitude l, latitude b and adopted distance d (`GL`, `GB`, `DIST`). The frame has the Sun at (R⊙, 0, z⊙) with R⊙ = 8.178 kpc and z⊙ = 0. X decreases toward the Galactic centre and Y points toward l = 90°, so a pulsar's position is (R⊙ − d cos b cos l, d cos b sin l, z⊙ + d sin b). This convention is confirmed by the data: J1640+2224 and J1713+0747 land 0.24 and 0.17 kpc from Table 1's centre (7.3, 0.57, 0.63) kpc, consistent with Table 1's pair separation of 0.36 kpc. The paper itself gives only R⊙ ≈ 8 kpc. `frame_scan` in `results/selection.json` repeats the test for R⊙ = 7.9–8.4 kpc and z⊙ = −0.03, 0, +0.03 kpc; seven named pulsars are outside 1 kpc in every case.

## Closest possible distance

For a unit sightline n from the Sun S and centre C, the point S + t n closest to C has t = max(0, n·(C − S)). If n·(C − S) ≤ 0, the sightline points away from the centre and its closest point is the Sun. The Sun is 1.22 kpc from C, so these pulsars cannot be within 1 kpc for any distance. This applies to J0125−2327, J0645+5158, J1012−4235 and J1125−6014, and is independent of parallax and distance uncertainties.

## Written rule

S/N is |`ALOS_PS`| / `ALOS_PS_ERR` for every catalogue row with a spin-derived acceleration (41 rows). Rows with S/N > 1 and catalogue position within 1 kpc of C are J1713+0747, J1640+2224, J1751−2857, J1801−1417 and J2033+1734. The first two are the reference binary pair.

## Gravity response

With y = Ṗ_obs − Ṗ_Shk, B = γ√(Py) and â = (c/P)[y − (mB + b)], an extra true line-of-sight acceleration δa adds Pδa/c to y. Differentiating gives dâ/da = 1 − m dB/dy = 1 − mγ²P/(2B), with γ = 3.2×10¹⁹ G, m = 5.9×10⁻²⁹ G⁻¹ and B evaluated from the row's own inputs. Donlon et al. (2025, Appendix A) note that computing B this way, without first removing the Galactic acceleration, is an approximation, and treat its effect as added scatter in the accelerations. R shows that it also changes how strongly each catalogue value responds to a real acceleration. R describes the catalogue estimator. A likelihood that models it explicitly can still extract information, so R alone does not give the change in the published posterior.

## Magnetic-field consistency

Each printed number is allowed its rounding interval: ± half a unit in its last printed digit. A row passes if some P, Ṗ_obs and Ṗ_Shk within their intervals give a B within the printed B's interval. This is exact interval arithmetic with 50-digit decimals, not a statistical test. All 59 positive-B rows of v1 pass. 23 of 52 rows of v3 fail.

The "consistent-B" acceleration changes only the braking term, â′ = â − (c/P) m (B_inputs − B_printed), keeping every other published term. It is a sensitivity calculation, not a replacement measurement.

## Solar term

The subhalo is modelled as a point mass of 2.45×10⁷ M☉ at (7.43, 0.38, 0.21) kpc, the paper's compact-object result. For each pulsar, the line-of-sight components (positive away from the Sun) of the subhalo's pull on the pulsar and on the Sun are reported separately. Timing measures the difference.

## What is not established

- The actual list of pulsars, catalogue version and code used in the fit.
- Any change to the published mass, position or Bayes factor. No fit was rerun.
- Whether the binary-pair signal on which the paper says the result depends is robust. That question is outside this repository.
