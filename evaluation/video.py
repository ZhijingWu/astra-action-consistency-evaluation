"""CPU evaluation of a user-supplied, lawfully held native RGB frame array."""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from estimators import Estimator
import motion_controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frames', type=Path, help='.npy RGB uint8 array [97,480,832,3]')
    parser.add_argument('--output', type=Path, required=True, help='New JSON file')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output exists; choose a new file')
    frames = np.load(args.frames, mmap_mode='r', allow_pickle=False)
    if frames.shape != (97, 480, 832, 3) or frames.dtype != np.uint8:
        parser.error('expected native RGB uint8 shape [97,480,832,3]; no resizing/truncation is performed')
    cv2.setNumThreads(4)
    cv2.ocl.setUseOpenCL(False)
    config = json.loads((Path(__file__).resolve().parents[1] / 'configs/synthetic_frozen.json').read_text(encoding='utf-8'))
    m0 = motion_controls.track(frames, motion_controls.make_mask(config['M0']['mask']))
    estimator = Estimator('M2')
    rows = []
    for i in range(96):
        a = cv2.cvtColor(np.asarray(frames[i]), cv2.COLOR_RGB2GRAY)
        b = cv2.cvtColor(np.asarray(frames[i + 1]), cv2.COLOR_RGB2GRAY)
        row, _ = estimator.update(a, b, i)
        rows.append(row)
    valid = [r for r in rows if r['valid']]
    coverage = len(valid) / 96
    center = float(np.median([r['signed_dx_pixels'] for r in valid])) if valid else None
    direction = int(np.sign(center)) if center is not None and abs(center) > .25 else 0 if center is not None else None
    agreement = sum(r['direction'] == direction for r in valid) / len(valid) if valid else None
    reportable = bool(coverage >= .85 and agreement is not None and agreement >= .90)
    result = {'classification': 'APPARENT_IMAGE_MOTION_DIAGNOSTIC', 'physical_yaw_ground_truth': None,
              'M0': m0, 'M2': {'intervals': rows, 'valid_intervals': len(valid), 'denominator': 96,
              'coverage': coverage, 'conditional_median_dx_pixels': center,
              'conditional_internal_direction_agreement': agreement,
              'aggregate_reportable': reportable, 'video_direction': direction if reportable else None}}
    with args.output.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, allow_nan=False)
    print(f'M2 coverage {len(valid)}/96; aggregate reportable={reportable}; no physical-fidelity result')


if __name__ == '__main__':
    main()
