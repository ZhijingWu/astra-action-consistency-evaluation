# License and privacy audit

Decision: the selected original code, prose, numeric tables and source-free figure are releasable under MIT within the user's authorized independent-project scope. Uncertain assets are excluded. This audit does not transfer third-party rights or certify legal ownership.

## File-level provenance

`PUBLIC_FILE_INVENTORY.md` lists every intended file with an origin, transformation and license disposition. `provenance/sources.json` binds selected preserved sources to SHA-256; frozen geometry, estimators, controls, M0 and configuration are byte-identical. The historical scoring functions are extracted without algorithm changes into a portable evaluator; portable drivers, tests and figure/audit scripts are newly written. All original sources remain unchanged.

The supplied project identifies these as independent original study code. Manual source review found procedural rendering and ordinary NumPy/OpenCV API usage, with no imported Astra source implementation or third-party media. Frozen hashes were verified. Exact function/class AST comparisons to 173 cached Astra Python files found no matches. This comparison is evidence for provenance review, not a complete originality or ownership proof. No ambiguous inherited code has been silently relicensed.

The source revision's MIT LICENSE was verified directly at the immutable upstream URL; its exact notice is retained. No model-weight or media right is inferred from that source license. NumPy, OpenCV and Matplotlib are separately installed dependencies with their own notices; no wheels/native runtimes/fonts are bundled as dependencies. The derived plot is original numeric rendering of the preserved counts. It contains no raw scene pixels.

## Selection and exclusions

| Material | Disposition | Reason |
| --- | --- | --- |
| Procedural synthetic generator and geometry controls | Include | Original code; no external textures or reference images |
| Frozen independent M0/M1/M2 estimator code and config | Include | Original study implementation, hashes verified; known limitations documented |
| Historical synthetic and M2 interval numeric tables | Include | Source-free records, all failures retained, under 2 MiB per file |
| Five-output aggregate coverage and control summaries | Include | Whitelisted derived facts with private paths/log context removed |
| V2 four-row aggregate concordance and status | Include | No coordinates, notes, identities, declarations, pair key or frame identifiers |
| Coverage PNG/SVG | Include | New plot from numeric counts only; visually verified |
| Upstream MIT license text | Include | Copyright attribution and immutable source hash |
| Astra/Wan model checkpoints | Exclude | Asset-specific redistribution permission not established; size and source license do not confer permission |
| Reference images/videos and original generated videos/frame arrays | Exclude | Capture/media rights not independently established; raw pixels unnecessary for public numeric diagnostic |
| Full synthetic preview/ground-truth arrays | Exclude | Avoid raw datasets; generator can reconstruct the bounded suite |
| Blinded archive, crops, index and internal unblinding key | Exclude | Reviewer-only and blinding material; includes underlying media |
| V1/V2 raw annotations and provenance declarations | Exclude | Reviewer/user identity, notes, declarations and unresolved reference/media scope |
| Original/private research reports, logs and receipts | Exclude | Private paths/context; public prose rewritten from supported facts |
| Original inference wrapper and GPU driver scripts | Exclude | Private paths/logging and upstream initialization context; exact generation reproduction limitation explicitly documented |
| Accepted paper PDF/screenshots | Exclude | Redistribution rights not established; citation/link suffices |
| Credentials, SSH/proxy settings and other workloads | Exclude | Not copied or inspected for this release |
| CV/outreach material | Exclude | Outside requested scope; untouched |

## Checks and bounds

Offline heuristic checks cover token patterns, private keys, credential assignments, authenticated URLs, absolute local/server paths, restricted filenames, annotation identity fields, prohibited raw/model/archive file types, UTF-8 decoding and a 5 MiB per-file cap. Findings report file/type rather than secret values. The intended staged inventory is checked independently of ignored caches. `verification/release_scan.json` records results.

No heuristic scanner can guarantee that arbitrary secrets are absent. Manual file selection/provenance review and the staged-file comparison are part of this review. No private absolute path is present in the public payload; private mapping receipts stay outside it. Copyright-holder names and Astra paper authors appear only for required public attribution, not as annotation identities or declarations.
