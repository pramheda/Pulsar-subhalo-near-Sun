"""Check the solitary-pulsar accelerations the fit takes from Donlon et al. (2025).

Python standard library only. The catalogue estimates each solitary pulsar's line-of-sight
acceleration from its spin-down:

    y     = Pdot_obs - Pdot_Shk                      (spin-down after the proper-motion correction)
    B     = gamma * sqrt(P * y),  gamma = 3.2e19 G   (surface magnetic field, BSURF)
    a_hat = (c / P) * (y - (m * B + b))              (m = 5.9e-29 /G, b = -2.8e-21: braking calibration)

Two properties are tested:
1. Internal consistency. Every printed B should be reproducible from that row's printed P, Pdot_obs
   and Pdot_Shk, allowing each printed number its rounding interval. This holds for every row of v1
   but not for v3, whose Shklovskii column was updated without recomputing B.
2. Response to gravity. An extra true acceleration da changes y by P*da/c, and B with it, so
   d(a_hat)/d(a_true) = R = 1 - m * gamma^2 * P / (2 B). R = 1 would mean a faithful accelerometer.
"""
from pathlib import Path
from decimal import Decimal, getcontext
import csv
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_catalogue import fetch
from check_selection import NAMED

getcontext().prec = 50
GAMMA, M, B0 = 3.2e19, 5.9e-29, -2.8e-21
C, YEAR = 299792458.0, 3.15576e7
TO_MM_S_YR = 1e3 * YEAR


def read(path):
    with open(path, newline='') as fh:
        r = csv.DictReader(fh)
        next(r)
        return list(r)


def rounding_interval(text):
    text = text.strip()
    mant, _, exp = text.lower().partition('e')
    places = len(mant.split('.')[1]) if '.' in mant else 0
    half = Decimal(1).scaleb((int(exp) if exp else 0) - places) / 2
    v = Decimal(text)
    return v - half, v + half


def b_is_reproducible(row):
    p = rounding_interval(row['PS'])
    obs = rounding_interval(row['PSDOT_OBS'])
    shk = rounding_interval(row['PSDOT_SHK'] or '0')
    g = Decimal('3.2e19')
    lo = g * (p[0] * max(obs[0] - shk[1], Decimal(0))).sqrt()
    hi = g * (p[1] * (obs[1] - shk[0])).sqrt()
    b = rounding_interval(row['BSURF'])
    return not (hi < b[0] or lo > b[1])


def consistency(rows):
    tested = [r for r in rows if r['BSURF'] and Decimal(r['BSURF']) > 0]
    failing = [r['NAME'] for r in tested if not b_is_reproducible(r)]
    return dict(rows_with_positive_B=len(tested), rows_whose_B_cannot_be_reproduced=len(failing), failing=failing)


def run():
    paths = fetch()
    v1, v3 = read(paths['donlon_v1_data.csv']), read(paths['donlon_v3_data.csv'])
    by_name = {r['NAME']: r for r in v3}
    named = []
    for name in NAMED:
        r = by_name[name]
        p, obs, shk = float(r['PS']), float(r['PSDOT_OBS']), float(r['PSDOT_SHK'] or 0)
        b_printed = float(r['BSURF'])
        b_inputs = GAMMA * (p * (obs - shk)) ** 0.5
        a_printed, a_err = float(r['ALOS_PS']), float(r['ALOS_PS_ERR'])
        # Change only the braking term, from the printed B to the B implied by the row's own inputs.
        a_consistent = a_printed - C / p * M * (b_inputs - b_printed) * TO_MM_S_YR
        named.append(dict(pulsar=name, B_printed_G=b_printed, B_from_row_inputs_G=round(b_inputs, -3),
                          B_reproducible=b_is_reproducible(r),
                          acceleration_printed_mm_s_yr=a_printed, acceleration_error_mm_s_yr=a_err,
                          acceleration_with_consistent_B_mm_s_yr=round(a_consistent, 3),
                          shift_in_errors=round((a_consistent - a_printed) / a_err, 2),
                          gravity_response_R=round(1 - M * GAMMA ** 2 * p / (2 * b_inputs), 3)))
    return dict(catalogue_commit='6cb4e31f6b2e732f5973b024634507c2e4f59988',
                v1=consistency(v1), v3=consistency(v3), named=named,
                named_with_irreproducible_B=[n['pulsar'] for n in named if not n['B_reproducible']])


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
