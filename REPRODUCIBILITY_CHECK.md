# Reproducibility check

Status: **PASS FOR THE PUBLISHED CPU DIAGNOSTIC SCOPE**. Full original Astra inference is not end-to-end reproducible from this payload and is explicitly outside that status.

Date: 2026-10-14. Tested environment: Windows, Python 3.13.5, NumPy 2.1.3, OpenCV 4.10.0 (`opencv-python-headless` 4.10.0.84), Matplotlib 3.10.0. CPU only, four OpenCV threads, OpenCL disabled in the numerical runners/tests. Dependencies were installed only in the publication task's isolated environment. No existing analysis environment was altered.

| Executed check | Result |
| --- | --- |
| Six release unittest cases | 6 passed, 0 failed in final run; 19.383 seconds |
| Preserved original code/config hashes | Exact matches |
| Original independent geometry controls | 10/10 passed |
| M0/M2 bounded regression | 24 retained interval records matched eligibility/counts exactly and numeric values within 1e-4 px |
| Blank/changing-texture evidence-poor cases | M2 abstains; estimates/directions remain unavailable |
| Retained synthetic interval/summary consistency | 7,488 rows -> 78 summaries; 780 checked fields agree to 1e-12 or exact boolean equality |
| Original synthetic selection | M0 6/13 on each split; M1/M2 13/13 on each; M1/M2 false-valid count 0 |
| Retained real-video denominators and repeat | All 480 M2 rows accounted for; five 96-interval denominators; A17 repeat equal; all five M2 coverage gates fail |
| Four CLI entry-point help/import checks | Passed without model imports |
| User-supplied video input contract | Wrong shape rejected with exit code 2 and no output written |
| Privacy scanner negative fixtures | Private path, dummy token and forbidden model filename detected |
| Manifest negative fixture | Controlled content mutation detected |
| Citation | BibTeX agrees with pinned upstream README |
| Relative Markdown links | No broken local links |
| Coverage figure | Counts traced to table; PNG visually checked for labels, legend and clipping |

An initial test run failed one **test bookkeeping assertion**: it expected 858 comparisons, but 78 summaries x 10 fields gives 780. All numerical comparisons had passed. The assertion was corrected and the complete six-test set passed. No original data, metric parameter, estimator source or scientific conclusion was changed.

The full historical synthetic suite was not re-executed. No real video was re-evaluated, no model checkpoint loaded, no GPU task launched, and no paid API called. Historical result gate failures remain scientific observations rather than release-test failures. The original Linux/NumPy 1.26.4 environment is documented, not asserted to have been recreated.

`verification/cpu_checks.json` contains sanitized machine-readable facts. Final heuristic scan and payload checksum checks are in `verification/release_scan.json` and `SHA256SUMS.txt`; Git index/commit equality is checked by the private handoff receipt. Frozen scientific reports and concurrent results were read only. The public files contain logical provenance labels, with private path mappings retained outside the candidate.
