"""Download the Donlon et al. (2025) pulsar catalogue, v1 and v3, from a pinned commit.

The upstream repository has no licence file, so the tables are not redistributed here. The
files are saved to inputs/ (git-ignored) and checked against fixed SHA-256 values.
"""
from pathlib import Path
import hashlib
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
COMMIT = '6cb4e31f6b2e732f5973b024634507c2e4f59988'
BASE = f'https://raw.githubusercontent.com/thomasdonlon/Empirical_Model_MSP_Spindown_Accels/{COMMIT}'
FILES = {
    'donlon_v1_data.csv': ('v1/data.csv', 'cdb4d34fcd8800a9b3ca1b1367f33acf35b65bb1550720cee989d5a9594d2ea0'),
    'donlon_v3_data.csv': ('v3/data.csv', '35a03b5db490fc90ec0360d06b6bc8046e4df4eb8b436dabc0001a1a5ca59e02'),
}


def fetch():
    out = ROOT / 'inputs'
    out.mkdir(exist_ok=True)
    paths = {}
    for name, (remote, sha) in FILES.items():
        path = out / name
        if not (path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == sha):
            with urllib.request.urlopen(f'{BASE}/{remote}', timeout=60) as r:
                data = r.read()
            assert hashlib.sha256(data).hexdigest() == sha, f'{remote}: unexpected checksum'
            path.write_bytes(data)
        paths[name] = path
    return paths


if __name__ == '__main__':
    for name, path in fetch().items():
        print('verified', path.relative_to(ROOT))
