"""Plot each pulsar's distance from the stated selection centre, from results/selection.json."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
BLUE, ORANGE, INK, INK2, RULE, SURFACE = '#2a78d6', '#eb6834', '#0b0b0b', '#52514e', '#c9c8c2', '#fcfcfb'


def main():
    s = json.loads((ROOT / 'results/selection.json').read_text())
    rows = [dict(name=r['pulsar'], d=r['distance_from_centre_kpc'], lo=r['closest_possible_kpc'], named=True) for r in s['named']]
    rows += [dict(name=r['pulsar'], d=r['distance_from_centre_kpc'], lo=None, named=False)
             for r in s['selected_by_written_rule'] if not r['named_in_paper'] and not r['is_the_reference_pair']]
    rows.sort(key=lambda r: r['d'])

    plt.rcParams.update({'font.size': 11, 'text.color': INK, 'axes.labelcolor': INK2, 'axes.edgecolor': RULE,
                         'xtick.color': INK2, 'ytick.color': INK, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.axvspan(0, 1, color='#eef4fc', zorder=0)
    ax.axvline(1, color=INK2, lw=1, ls='--', zorder=1)
    ax.text(0.98, len(rows) - 0.4, 'stated selection:\n< 1 kpc from the centre', ha='right', va='top', fontsize=9.5, color=INK2)
    for i, r in enumerate(rows):
        if r['lo'] is not None:
            ax.plot([r['lo'], r['d']], [i, i], color=RULE, lw=2, zorder=2, solid_capstyle='round')
            ax.plot(r['lo'], i, marker='|', ms=12, mew=2, color=INK2, zorder=3)
        ax.plot(r['d'], i, 'o', ms=9, color=BLUE if r['named'] else ORANGE, mec=SURFACE, mew=2, zorder=4)
    ax.set_yticks(range(len(rows)), [r['name'] for r in rows])
    ax.set_xlim(0, 2.2); ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xlabel('Distance from the J1640+2224 / J1713+0747 centre (kpc)')
    ax.grid(axis='x', color='#e4e3df', lw=0.8); ax.set_axisbelow(True)
    handles = [plt.Line2D([], [], marker='o', ls='', ms=9, color=BLUE, mec=SURFACE, mew=2, label='Named in the paper as meeting the rule'),
               plt.Line2D([], [], marker='o', ls='', ms=9, color=ORANGE, mec=SURFACE, mew=2, label='Meets the rule but not used'),
               plt.Line2D([], [], marker='|', ls='', ms=12, mew=2, color=INK2, label='Closest point anywhere on its line of sight')]
    ax.legend(handles=handles, loc='lower right', frameon=False, fontsize=9.5)
    ax.set_title('7 of the 8 named pulsars are outside the stated 1 kpc selection; 4 could never be inside it',
                 loc='left', fontsize=12, color=INK, pad=12)
    fig.savefig(ROOT / 'results/selection_geometry.png', dpi=180, bbox_inches='tight', facecolor=SURFACE)


if __name__ == '__main__':
    main()
