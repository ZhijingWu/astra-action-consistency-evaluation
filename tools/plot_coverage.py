"""Plot retained coverage counts only; no media or model access."""
import argparse
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New figure directory')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    with (ROOT / 'results/astra_coverage.csv').open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'svg.hashsalt': 'astra-coverage-v1', 'axes.spines.top': False,
                         'axes.spines.right': False})
    x = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(8.4, 4.7), layout='constrained')
    for offset, method, color in [(-.19, 'M0', '#657387'), (.19, 'M2', '#217A96')]:
        counts = [int(row[method + '_valid']) for row in rows]
        bars = ax.bar(x + offset, np.array(counts) / 96 * 100, width=.36, label=method, color=color)
        ax.bar_label(bars, labels=[f'{count}/96' for count in counts], padding=4, fontsize=9)
    ax.axhline(85, color='#A33A29', linestyle='--', linewidth=1.3, label='Frozen M2 coverage gate (85%)')
    ax.set(xticks=x, xticklabels=['A17', 'B17', 'A17_repeat\n(exact duplicate)', 'A29', 'B29'],
           ylim=(0, 112), ylabel='Eligible intervals (%)',
           title='Estimator eligibility on five retained Astra outputs')
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.grid(axis='y', alpha=.18)
    ax.set_axisbelow(True)
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.17), ncols=3, frameon=False, fontsize=9)
    fig.savefig(args.output / 'astra_coverage.png', dpi=200)
    fig.savefig(args.output / 'astra_coverage.svg', metadata={'Date': None})
    svg = args.output / 'astra_coverage.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8', newline='\n')
    print('Saved coverage PNG/SVG from results/astra_coverage.csv')


if __name__ == '__main__':
    main()
