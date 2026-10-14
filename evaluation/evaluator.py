"""External synthetic scoring; estimator inputs remain images only.

Scoring functions are extracted without algorithm changes from the frozen
independent Stage A evaluator. See provenance/sources.json.
"""
import numpy as np


def median(v):
    return float(np.median(v)) if len(v) else None


def m0_row(record, index):
    dx = record['median_horizontal_displacement_over_width']
    valid = record['eligible']
    count, grid = record['surviving_tracks'], record['grid_cells']
    reasons = []
    if count < 20:
        reasons.append('COUNT')
    if grid < 4:
        reasons.append('GRID')
    row = {'method': 'M0', 'from_frame': index, 'to_frame': index + 1,
           'incoming': record['incoming_tracks'], 'accepted': count,
           'refreshed_features': 0, 'grid_cells': grid,
           'acceptance_fraction': count / record['incoming_tracks'] if record['incoming_tracks'] else 0.,
           'valid': valid, 'abstention_reason': '+'.join(reasons),
           'signed_dx_pixels': dx * 832 if dx is not None else None,
           'signed_dx_over_width': dx,
           'direction': int(np.sign(dx)) if dx is not None and abs(dx * 832) > .25 else 0 if valid else None,
           'track_age_median_intervals': index + 1 if count else None,
           'track_age_max_intervals': index + 1 if count else None,
           'median_FB_pixels': median(record.get('forward_backward_errors', [])),
           'median_patch_NCC': None, 'dx_IQR_pixels': None}
    detail = {'from_xy': np.asarray(record.get('from_xy', [])).reshape(-1, 2),
              'to_xy': np.asarray(record.get('to_xy', [])).reshape(-1, 2)}
    return row, detail


def truth_augment(row,detail,scene,i,oracle):
 row.update({'oracle_valid_grid_fraction':oracle['fraction'],'oracle_valid_grid_cells':oracle['cells'],'truth_adequate':oracle['adequate'],'truth_direction':oracle['direction'],'oracle_median_dx_pixels':oracle['median_dx']})
 if len(detail['from_xy']):
  truth=scene.truth(detail['from_xy'],i); e=np.linalg.norm(detail['to_xy']-truth['to_xy'],axis=1)
  correct=truth['support']&(e<=1.5); frac=float(np.mean(correct))
  ref=median(truth['flow'][truth['support'],0]); error=row['signed_dx_pixels']-ref if row['valid'] and ref is not None else None
  row.update({'truth_supported_correspondence_fraction':frac,'matched_support_truth_median_dx_pixels':ref,'signed_error_pixels':error,'median_correspondence_error_pixels_on_truth_support':median(e[truth['support']])})
 else: row.update({'truth_supported_correspondence_fraction':0.,'matched_support_truth_median_dx_pixels':None,'signed_error_pixels':None,'median_correspondence_error_pixels_on_truth_support':None})
 row['false_valid_inadequate_evidence']=bool(row['valid'] and not oracle['adequate'])
 row['unsupported_claim']=bool(row['valid'] and row['truth_supported_correspondence_fraction']<.8)
 row['direction_correct']=bool(row['valid'] and row['direction']==oracle['direction']) if oracle['adequate'] else None
 return row

def summarize(rows,zero=False):
 adequate=[r for r in rows if r['truth_adequate']]; valid=[r for r in rows if r['valid']]; both=[r for r in adequate if r['valid']]; invalidtruth=[r for r in rows if not r['truth_adequate']]
 errors=[abs(r['signed_error_pixels']) for r in both if r['signed_error_pixels'] is not None]
 jitter=[]
 for a,c in zip(rows,rows[1:]):
  if a['valid'] and c['valid'] and a['signed_error_pixels'] is not None and c['signed_error_pixels'] is not None: jitter.append(abs(c['signed_error_pixels']-a['signed_error_pixels']))
 reasons={r['abstention_reason']:sum(s['abstention_reason']==r['abstention_reason'] for s in rows) for r in rows if not r['valid']}
 s={'intervals':len(rows),'valid_intervals':len(valid),'coverage_all_intervals':len(valid)/len(rows),'abstention_rate':1-len(valid)/len(rows),'truth_adequate_intervals':len(adequate),'coverage_on_truth_adequate':len(both)/len(adequate) if adequate else None,
 'conditional_direction_accuracy':sum(r['direction_correct'] for r in both)/len(both) if both else None,'correct_direction_over_all_truth_adequate':sum(r['direction_correct'] for r in both)/len(adequate) if adequate else None,
 'signed_error_absolute_median_pixels':median(errors),'signed_error_absolute_p95_pixels':float(np.percentile(errors,95)) if errors else None,
 'truth_inadequate_intervals':len(invalidtruth),'false_valid_count_on_inadequate':sum(r['false_valid_inadequate_evidence'] for r in rows),'false_valid_fraction_on_inadequate':sum(r['false_valid_inadequate_evidence'] for r in rows)/len(invalidtruth) if invalidtruth else None,
 'unsupported_claim_count':sum(r['unsupported_claim'] for r in valid),'unsupported_claim_fraction':sum(r['unsupported_claim'] for r in valid)/len(valid) if valid else 0.,
 'zero_abs_estimate_p95_pixels':float(np.percentile([abs(r['signed_dx_pixels']) for r in both],95)) if zero and both else None,
 'adjacent_valid_pairs':len(jitter),'truth_residual_temporal_change_median_pixels':median(jitter),'abstention_reasons':reasons,
 'accepted_count_min':min(r['accepted'] for r in rows),'accepted_count_median':median([r['accepted'] for r in rows]),'accepted_count_max':max(r['accepted'] for r in rows)}
 failures=[]
 if adequate:
  for key,threshold,mode in [('coverage_on_truth_adequate',.85,'min'),('conditional_direction_accuracy',.98,'min'),('signed_error_absolute_median_pixels',.5,'max'),('signed_error_absolute_p95_pixels',1.5,'max')]:
   v=s[key]
   if v is None or (v<threshold if mode=='min' else v>threshold): failures.append(key)
 if invalidtruth and s['false_valid_fraction_on_inadequate']>.02: failures.append('false_valid_fraction_on_inadequate')
 if s['unsupported_claim_fraction']>.02: failures.append('unsupported_claim_fraction')
 if zero and (s['zero_abs_estimate_p95_pixels'] is None or s['zero_abs_estimate_p95_pixels']>.1): failures.append('zero_abs_estimate_p95_pixels')
 s['prospective_gate_failures']=failures; s['prospective_case_pass']=not failures
 return s
