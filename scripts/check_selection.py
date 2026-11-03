"""Test the paper's stated solitary-pulsar selection against the catalogue it uses.

Python standard library only. The paper selects "S/N > 1 solitary pulsars that are near (< 1 kpc)
the common center of PSR J1640+2224/PSR J1713+0747", which Table 1 gives as (7.3, 0.57, 0.63) kpc,
and names eight. This script places every catalogue pulsar in that Galactocentric frame and
reports:
  - each named pulsar's distance from the centre at its catalogue distance;
  - the closest any point on its line of sight comes to the centre, for any distance >= 0;
  - which pulsars the written rule actually selects;
  - the subhalo's own pull on the Sun, which Eq. (8) does not include.
"""
from pathlib import Path
import csv
import json
import math
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_catalogue import fetch

CENTRE = (7.3, 0.57, 0.63)                     # Table 1, kpc
SUBHALO = dict(mass_Msun=2.45e7, xyz_kpc=(7.43, 0.38, 0.21))   # abstract, compact-object fit
NAMED = ['J0125-2327', 'J0645+5158', 'J1012-4235', 'J1125-6014', 'J1751-2857', 'J1910+1256', 'J2017+0603', 'J1600-3053']
R_SUN = 8.178                                  # kpc; the frame check below confirms the convention
G, MSUN, KPC, YEAR = 6.67430e-11, 1.98840987e30, 3.0856775814913673e19, 3.15576e7


def read(path):
    with open(path, newline='') as fh:
        r = csv.DictReader(fh)
        next(r)                                # units row
        return {row['NAME']: row for row in r}


def frame(l_deg, b_deg, r_sun=R_SUN, z_sun=0.0):
    """Sun at (+r_sun, 0, z_sun); X decreases toward the Galactic centre; Y toward l = 90 deg."""
    l, b = math.radians(l_deg), math.radians(b_deg)
    sun = (r_sun, 0.0, z_sun)
    n = (-math.cos(b) * math.cos(l), math.cos(b) * math.sin(l), math.sin(b))
    return sun, n


def place(row, **kw):
    sun, n = frame(float(row['GL']), float(row['GB']), **kw)
    d = float(row['DIST'])
    return tuple(s + d * u for s, u in zip(sun, n)), sun, n


def closest_on_sightline(sun, n, centre=CENTRE):
    t = max(0.0, sum(u * (c - s) for u, c, s in zip(n, centre, sun)))
    return math.dist(tuple(s + t * u for s, u in zip(sun, n)), centre), t == 0.0


def spin_acceleration_rows(rows):
    for name, row in rows.items():
        if row['ALOS_PS'] and row['ALOS_PS_ERR']:
            yield name, row, abs(float(row['ALOS_PS'])) / float(row['ALOS_PS_ERR'])


def los_pull(mass, src, at, n):
    """Line-of-sight component (mm/s/yr, positive away from the Sun) of the attraction toward src."""
    r = [s - a for s, a in zip(src, at)]
    dist = math.sqrt(sum(x * x for x in r))
    g = G * mass * MSUN / (dist * KPC) ** 2
    return g * sum(x / dist * u for x, u in zip(r, n)) * 1e3 * YEAR


def run():
    rows = read(fetch()['donlon_v3_data.csv'])

    frame_check = {}
    for name in ['J1640+2224', 'J1713+0747']:
        p, _, _ = place(rows[name])
        frame_check[name] = dict(xyz_kpc=[round(v, 3) for v in p], distance_from_centre_kpc=round(math.dist(p, CENTRE), 3))

    named = []
    for name in NAMED:
        row = rows[name]
        p, sun, n = place(row)
        closest, at_sun = closest_on_sightline(sun, n)
        named.append(dict(pulsar=name, catalogue_distance_kpc=float(row['DIST']),
                          signal_to_noise=round(abs(float(row['ALOS_PS'])) / float(row['ALOS_PS_ERR']), 2),
                          distance_from_centre_kpc=round(math.dist(p, CENTRE), 3),
                          closest_possible_kpc=round(closest, 3), closest_possible_is_the_sun=at_sun,
                          meets_stated_rule=math.dist(p, CENTRE) < 1.0))

    selected = []
    for name, row, sn in spin_acceleration_rows(rows):
        p, _, _ = place(row)
        if sn > 1 and math.dist(p, CENTRE) < 1.0:
            selected.append(dict(pulsar=name, signal_to_noise=round(sn, 2),
                                 distance_from_centre_kpc=round(math.dist(p, CENTRE), 3),
                                 named_in_paper=name in NAMED,
                                 is_the_reference_pair=name in ('J1640+2224', 'J1713+0747')))
    selected.sort(key=lambda r: r['distance_from_centre_kpc'])

    scan = []
    for r_sun in [7.9, 8.0, 8.1, 8.178, 8.3, 8.4]:
        for z_sun in [-0.03, 0.0, 0.03]:
            out, impossible = 0, 0
            for name in NAMED:
                p, sun, n = place(rows[name], r_sun=r_sun, z_sun=z_sun)
                out += math.dist(p, CENTRE) >= 1.0
                impossible += closest_on_sightline(sun, n)[0] >= 1.0
            scan.append(dict(r_sun_kpc=r_sun, z_sun_kpc=z_sun, named_outside_1kpc=out, named_that_can_never_be_inside=impossible))

    sun = (R_SUN, 0.0, 0.0)
    m, s = SUBHALO['mass_Msun'], SUBHALO['xyz_kpc']
    r_sun_sub = math.dist(sun, s)
    solar_pull = G * m * MSUN / (r_sun_sub * KPC) ** 2 * 1e3 * YEAR
    terms = []
    for name in ['J1640+2224', 'J1713+0747'] + NAMED:
        p, _, n = place(rows[name])
        on_pulsar = los_pull(m, s, p, n)
        on_sun = los_pull(m, s, sun, n)
        terms.append(dict(pulsar=name, pull_on_pulsar_mm_s_yr=round(on_pulsar, 4),
                          pull_on_sun_mm_s_yr=round(on_sun, 4),
                          measured_relative_mm_s_yr=round(on_pulsar - on_sun, 4)))

    return dict(
        centre_kpc=CENTRE, sun_kpc=[R_SUN, 0.0, 0.0], sun_to_centre_kpc=round(math.dist(sun, CENTRE), 4),
        frame_check=frame_check, named=named,
        named_outside_1kpc=sum(not r['meets_stated_rule'] for r in named),
        named_that_can_never_be_inside=sum(r['closest_possible_kpc'] >= 1.0 for r in named),
        largest_named_distance_kpc=max(r['distance_from_centre_kpc'] for r in named),
        selected_by_written_rule=selected, frame_scan=scan,
        solar_term=dict(subhalo=SUBHALO, sun_to_subhalo_kpc=round(r_sun_sub, 4),
                        pull_on_sun_mm_s_yr=round(solar_pull, 4), per_pulsar=terms))


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
