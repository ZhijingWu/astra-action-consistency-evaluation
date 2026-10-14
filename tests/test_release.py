"""Bounded CPU regression tests against retained independent evidence."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import sys
import unittest
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evaluation'))
from geometry import Scene
from estimators import Estimator
from synthetic import run_case
from evaluator import summarize
from controls import run as geometry_controls


def read_csv(name):
    with (ROOT / 'results' / name).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cv2.setNumThreads(4)
        cv2.ocl.setUseOpenCL(False)
        cls.config = json.loads((ROOT / 'configs/synthetic_frozen.json').read_text(encoding='utf-8'))

    def test_frozen_source_hashes(self):
        provenance = json.loads((ROOT / 'provenance/sources.json').read_text(encoding='utf-8'))
        for record in provenance['sources']:
            if record.get('transformation') == 'byte-identical':
                self.assertEqual(hashlib.sha256((ROOT / record['public_file']).read_bytes()).hexdigest(), record['source_sha256'])

    def test_independent_geometry_controls(self):
        result = geometry_controls(self.config)
        self.assertTrue(result['all_passed'], result)
        self.assertLess(result['evidence']['max_projection_error_pixels'], 1e-9)

    def test_bounded_M0_M2_numerical_regression(self):
        expected = {(r['split'], r['case'], r['method'], int(r['from_frame'])): r
                    for r in read_csv('synthetic_smoke_reference.csv')}
        observed = []
        for split in self.config['splits']:
            for name in ['slow_positive', 'slow_negative', 'zero']:
                observed.extend(run_case(self.config, split, name, intervals=2, methods=('M0', 'M2')))
        self.assertEqual(len(observed), 24)
        for row in observed:
            ref = expected[(row['split'], row['case'], row['method'], row['from_frame'])]
            for field in ['valid', 'direction', 'accepted', 'grid_cells', 'incoming', 'truth_adequate']:
                self.assertEqual(str(row[field]), ref[field], (row['split'], row['case'], field))
            for field in ['signed_dx_pixels', 'signed_error_pixels', 'truth_supported_correspondence_fraction']:
                self.assertAlmostEqual(row[field], float(ref[field]), delta=1e-4, msg=str((row['split'], row['case'], field)))

    def test_evidence_poor_abstention(self):
        for split, seed in self.config['splits'].items():
            for name, index in [('blank_control', 32), ('changing_texture_control', 0)]:
                case = next(c for c in self.config['cases'] if c['name'] == name)
                scene = Scene(seed, case)
                a = cv2.cvtColor(scene.render(index)[0], cv2.COLOR_RGB2GRAY)
                b = cv2.cvtColor(scene.render(index + 1)[0], cv2.COLOR_RGB2GRAY)
                row, _ = Estimator('M2').update(a, b, index)
                self.assertFalse(row['valid'])
                self.assertIsNone(row['signed_dx_pixels'])
                self.assertIsNone(row['direction'])
                self.assertTrue(row['abstention_reason'])

    def test_retained_synthetic_summaries_and_selection(self):
        rows = read_csv('synthetic_per_interval.csv')
        typed = []
        for row in rows:
            typed.append({k: (None if v == '' else ast.literal_eval(v) if v in ['True', 'False'] else
                          float(v) if k in ['signed_error_pixels', 'signed_dx_pixels', 'truth_supported_correspondence_fraction', 'time_start_seconds', 'accepted', 'incoming', 'grid_cells'] else v)
                          for k, v in row.items()})
        # All fields used by summarize are typed explicitly.
        for row in typed:
            row['direction_correct'] = None if row['direction_correct'] is None else row['direction_correct']
        retained = read_csv('synthetic_case_summary.csv')
        self.assertEqual(len(rows), 7488)
        self.assertEqual(len(retained), 78)
        checked = 0
        for ref in retained:
            group = [r for r in typed if all(r[k] == ref[k] for k in ['split', 'case', 'method'])]
            case = next(c for c in self.config['cases'] if c['name'] == ref['case'])
            summary = summarize(group, case['family'] in ['zero', 'blank'])
            for field in ['intervals', 'valid_intervals', 'coverage_all_intervals', 'coverage_on_truth_adequate',
                          'conditional_direction_accuracy', 'signed_error_absolute_median_pixels',
                          'signed_error_absolute_p95_pixels', 'false_valid_count_on_inadequate',
                          'unsupported_claim_count', 'prospective_case_pass']:
                if summary[field] is None:
                    self.assertEqual(ref[field], '')
                elif isinstance(summary[field], bool):
                    self.assertEqual(str(summary[field]), ref[field])
                else:
                    self.assertAlmostEqual(summary[field], float(ref[field]), delta=1e-12)
                checked += 1
        for method in ['M1', 'M2']:
            self.assertEqual(sum(r['prospective_case_pass'] == 'True' for r in retained if r['method'] == method), 26)
            negative = [r for r in typed if r['method'] == method and not r['truth_adequate']]
            self.assertEqual(sum(r['false_valid_inadequate_evidence'] for r in negative), 0)
        self.assertEqual(sum(r['prospective_case_pass'] == 'True' for r in retained if r['method'] == 'M0'), 12)
        self.assertEqual(checked, 780)

    def test_real_coverage_and_abstention_denominators(self):
        rows = read_csv('astra_M2_per_interval.csv')
        coverage = read_csv('astra_coverage.csv')
        self.assertEqual(len(rows), 480)
        for ref in coverage:
            group = [r for r in rows if r['video'] == ref['video']]
            self.assertEqual(len(group), 96)
            valid = sum(r['valid'] == 'True' for r in group)
            self.assertEqual(valid, int(ref['M2_valid']))
            self.assertLess(valid / 96, .85)
            for row in group:
                if row['valid'] == 'False':
                    self.assertEqual(row['signed_dx_pixels'], '')
                    self.assertEqual(row['direction'], '')
        for video in ['A17', 'A17_repeat']:
            group = [{k: v for k, v in r.items() if k != 'video'} for r in rows if r['video'] == video]
            if video == 'A17':
                first = group
            else:
                self.assertEqual(first, group)


if __name__ == '__main__':
    unittest.main()
