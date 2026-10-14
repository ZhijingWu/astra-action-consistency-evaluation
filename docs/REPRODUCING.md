# Reproduction scope

All commands below run from the repository root. Use an activated isolated environment and a new output path. No command automatically obtains media, models, credentials or GPU allocation.

| Workflow | CPU only | Official Astra checkpoints | Private evidence required | Preparation execution |
| --- | --- | --- | --- | --- |
| Import/help and release smoke tests | Yes | No | No | Executed |
| Arithmetic reconstruction of saved result summaries | Yes | No | No | Executed |
| Plot retained coverage | Yes | No | No | Executed |
| Full original synthetic suite | Yes | No | No | Not executed again |
| M0/M2 diagnostics on supplied frame array | Yes | No | User-supplied lawful array | Help/input-contract checks only |
| New Astra generation | No | Yes | Conditioning media and inference controls | Not executed |
| Exact original five-video generation | No | Yes | Withheld wrapper and scene media | Not supported end to end by this release |

`requirements.txt` pins the tested CPU libraries. Original experiments used Python 3.11.17 / NumPy 1.26.4 / OpenCV 4.10.0 on Linux; `requirements-historical.txt` records those library versions. That historical environment was not recreated during preparation. Runtime, platform and floating-point differences can affect corner selection and last-bit measurements; compare eligibility/counts exactly and numerical smoke displacements to 1e-4 px. This tolerance is only a software portability check, not a changed scientific gate.

## Bounded release test

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The tests run two intervals of slow-positive, slow-negative and zero controls on both seeds and compare 24 M0/M2 records with preserved values. They additionally test blank/changing-texture abstention and the original ten geometry controls. Saved synthetic rows are aggregated into 78 summaries with 780 numeric/boolean comparisons; all 480 saved M2 Astra intervals are counted without opening a video. This is a bounded software test, not a new experiment or a fresh real-video validation.

## Optional full synthetic reproduction

```bash
python evaluation/synthetic.py --split all --case all --output scratch/full-synthetic-suite
```

The runner streams scene construction, retains M0's 97 frames for one case (about 111 MiB of RGB arrays), and writes only numerical records. It does not save a raw dataset. Compare its JSON summaries against `results/synthetic_case_summary.csv` for each split/case/method. `evaluation/evaluator.py` preserves the original `truth_augment` and `summarize` function bodies.

Full selection reproduction requires all case gates on both splits, overall false-valid rate <=0.01, the geometry controls, exact repeats and reversed renders. The portable runner reports case summaries; it does not emit a new historical freeze receipt or automatically declare a validated replacement. Historical selection and controls are recorded in `results/synthetic_selection.json`. Exact byte equality can depend on matching the original environment. Full-suite repeat/reversal execution was not run during this preparation.

## Evaluate supplied real frames

```bash
python evaluation/video.py frames.npy --output scratch/video-diagnostics.json
```

Create the `scratch` directory first. The `.npy` must be a native RGB uint8 `[97,480,832,3]` array you are permitted to use. The script refuses output overwrite, pickle loading, different shape/dtype and implicit resizing. It never loads a model. Mask coordinates are those of the original single-scene pilot; they are not a general semantic background selector for new scenes. New-scene outputs need a separately justified protocol and reference before physical interpretation.

## Recreate the derived figure and inspect payload

```bash
python -m pip install -r requirements-figures.txt
python tools/plot_coverage.py --output scratch/figures
python tools/release_audit.py
python tools/release_audit.py --verify-manifest
```

SHA256SUMS covers every payload file except itself and the scan receipt, which embeds payload hashes. Git internals and ignored caches are excluded. Any release change requires a fresh file audit, inventory and manifest; do not use a successful old check to approve changed bytes.
