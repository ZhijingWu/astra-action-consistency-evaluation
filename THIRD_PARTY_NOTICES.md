# Third-party attribution and license boundaries

The independent implementation files are original work from the existing study, hash-checked against frozen records. They invoke public NumPy/OpenCV APIs. No upstream Astra implementation, example media, model weights or paper PDF is redistributed. An exact function/class AST-body comparison against 173 cached upstream Python files found no exact matches; this supports origin review but is not a proof of ownership. See `provenance/origin_review.json`.

The pinned Astra repository's LICENSE was fetched from its immutable revision and compared with the cached notice. It is MIT, copyright (c) 2025 Yixuan. The complete notice is retained in `third_party/ASTRA_LICENSE.txt` as attribution and to preserve the upstream terms. This license is not applied to model weights or media.

| Separately installed dependency | Reviewed declared license | Boundary |
| --- | --- | --- |
| NumPy 2.1.3 | BSD-3-Clause; bundled component notices may differ | Installed dependency; no wheel/native libraries copied |
| OpenCV / opencv-python-headless 4.10.0.84 | OpenCV Apache-2.0; Python packaging MIT; bundled third-party notices retained by distribution | Installed dependency; no binary redistribution |
| Matplotlib 3.10.0 | Matplotlib license based on PSF agreement; other notices may apply | Optional figure dependency; no library/assets copied |

These are package-level provenance observations, not a relicensing of bundled components. The exact installed metadata and license-document hashes are recorded in `provenance/dependencies.json`. Python's standard library is used without redistribution. A future binary distribution must review all bundled dependency notices anew.

The repository's MIT license covers its original software, documentation, numerical tables and derived plots to the extent owned by its contributors. The upstream notice remains upstream-owned. Citation metadata and factual result summaries provide attribution. No permission is asserted for third-party reference media, raw generated outputs, model assets, user annotation declarations or reviewer-only evidence.
