"""Verify file integrity, rerun both checks and compare with the saved results.

Standard library only. Downloads the pinned catalogue into inputs/ on first use.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_inputs
import check_selection

ROOT = Path(__file__).resolve().parents[1]


def run(skip_hashes=False):
    checks = 0
    if not skip_hashes:
        for line in (ROOT / 'SHA256SUMS').read_text().splitlines():
            sha, name = line.split('  ', 1)
            p = ROOT / name
            assert p.is_file() and not p.is_symlink(), name
            assert hashlib.sha256(p.read_bytes()).hexdigest() == sha, name
            checks += 1
    as_json = lambda x: json.loads(json.dumps(x))          # tuples become lists, as in the saved files
    sel, inp = as_json(check_selection.run()), as_json(check_inputs.run())
    assert sel == json.loads((ROOT / 'results/selection.json').read_text()); checks += 1
    assert inp == json.loads((ROOT / 'results/inputs.json').read_text()); checks += 1

    assert all(v['distance_from_centre_kpc'] < 0.3 for v in sel['frame_check'].values())   # frame convention
    assert sel['named_outside_1kpc'] == 7 and sel['named_that_can_never_be_inside'] == 4
    assert all(s['named_outside_1kpc'] == 7 and s['named_that_can_never_be_inside'] >= 4 for s in sel['frame_scan'])
    assert sel['largest_named_distance_kpc'] < 2.01
    others = [r['pulsar'] for r in sel['selected_by_written_rule'] if not r['named_in_paper'] and not r['is_the_reference_pair']]
    assert others == ['J1801-1417', 'J2033+1734']
    assert inp['v1']['rows_whose_B_cannot_be_reproduced'] == 0 and inp['v3']['rows_whose_B_cannot_be_reproduced'] == 23
    assert inp['named_with_irreproducible_B'] == ['J0125-2327', 'J1125-6014', 'J1600-3053']
    assert abs(sel['solar_term']['pull_on_sun_mm_s_yr'] - 0.144) < 0.001
    checks += 8
    return dict(status='PASS', checks=checks, hashes_checked=not skip_hashes,
                named_outside_1kpc=sel['named_outside_1kpc'], never_inside=sel['named_that_can_never_be_inside'],
                selected_by_written_rule_but_not_used=others,
                v3_B_irreproducible=f"{inp['v3']['rows_whose_B_cannot_be_reproduced']}/{inp['v3']['rows_with_positive_B']}",
                gravity_response_R={n['pulsar']: n['gravity_response_R'] for n in inp['named']})


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--skip-hashes', action='store_true')
    print(json.dumps(run(p.parse_args().skip_hashes), indent=2))
