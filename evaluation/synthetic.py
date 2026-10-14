"""Portable CPU runner for the unchanged synthetic scene and estimators.

Full-suite execution is optional future reproduction, not publication QA.
No Astra modules, weights, video downloads, or GPU libraries are imported.
"""
import argparse
import csv
import json
from pathlib import Path
import cv2
import numpy as np
from geometry import Scene
from estimators import Estimator, cells
import motion_controls
from evaluator import m0_row, median, truth_augment, summarize

ROOT = Path(__file__).resolve().parents[1]


def score_pair(scene, index, row, detail):
    truth = scene.truth(scene.grid, index)
    support = truth['support']
    fraction = float(np.mean(support))
    grid_cells = cells(scene.grid[support])
    delta = scene.angles[index + 1] - scene.angles[index]
    oracle = {'fraction': fraction, 'cells': grid_cells,
              'adequate': bool(fraction >= .1 and grid_cells >= 6),
              'direction': int(np.sign(delta)) if abs(delta) > 1e-12 else 0,
              'median_dx': median(truth['flow'][support, 0])}
    return truth_augment(row, detail, scene, index, oracle)


def run_case(config, split, name, intervals=96, methods=('M0', 'M1', 'M2')):
    if not 1 <= intervals <= 96:
        raise ValueError('intervals must be in [1,96]')
    if not set(methods) <= {'M0', 'M1', 'M2'}:
        raise ValueError('unknown method')
    case = next(c for c in config['cases'] if c['name'] == name)
    scene = Scene(config['splits'][split], case)
    frames = []
    rows = []
    estimates = {m: Estimator(m) for m in methods if m != 'M0'}
    previous = None
    for j in range(intervals + 1):
        frame, _, _ = scene.render(j)
        if 'M0' in methods:
            frames.append(frame)
        current = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        if j:
            for method, estimator in estimates.items():
                row, detail = estimator.update(previous, current, j - 1)
                row = score_pair(scene, j - 1, row, detail)
                row.update(split=split, case=name, time_start_seconds=(j - 1) / 20)
                rows.append(row)
        previous = current
    if 'M0' in methods:
        mask = motion_controls.make_mask(config['M0']['mask'])
        baseline = motion_controls.track(frames, mask)
        for i, record in enumerate(baseline['intervals']):
            row, detail = m0_row(record, i)
            row = score_pair(scene, i, row, detail)
            row.update(split=split, case=name, time_start_seconds=i / 20)
            rows.append(row)
    return sorted(rows, key=lambda r: (r['method'], r['from_frame']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split', choices=['development', 'heldout', 'all'], default='heldout')
    parser.add_argument('--case', default='slow_positive', help='Frozen case name, or all')
    parser.add_argument('--intervals', type=int, default=96)
    parser.add_argument('--output', type=Path, required=True, help='New output directory; refuses overwrite')
    args = parser.parse_args()
    config = json.loads((ROOT / 'configs/synthetic_frozen.json').read_text(encoding='utf-8'))
    splits = list(config['splits']) if args.split == 'all' else [args.split]
    names = [c['name'] for c in config['cases']] if args.case == 'all' else [args.case]
    if args.case != 'all' and args.case not in [c['name'] for c in config['cases']]:
        parser.error('case is absent from frozen configuration')
    if not 1 <= args.intervals <= 96:
        parser.error('intervals must be in [1,96]')
    cv2.setNumThreads(4)
    cv2.ocl.setUseOpenCL(False)
    args.output.mkdir(parents=True, exist_ok=False)
    summaries, allrows = [], []
    for split in splits:
        for name in names:
            rows = run_case(config, split, name, args.intervals)
            allrows.extend(rows)
            case = next(c for c in config['cases'] if c['name'] == name)
            for method in ['M0', 'M1', 'M2']:
                summary = summarize([r for r in rows if r['method'] == method], case['family'] in ['zero', 'blank'])
                summary.update(split=split, case=name, method=method)
                summaries.append(summary)
            print(f'{split}/{name}: {args.intervals} intervals')
    fields = list(dict.fromkeys(k for r in allrows for k in r))
    with (args.output / 'intervals.csv').open('x', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(allrows)
    (args.output / 'summary.json').write_text(json.dumps(summaries, indent=2, allow_nan=False), encoding='utf-8')
    print('Subset runs do not reproduce the full-suite selection gate.' if args.intervals != 96 or args.case != 'all' or args.split != 'all' else 'All frozen cases executed; compare against retained tables and method-selection gates.')


if __name__ == '__main__':
    main()
