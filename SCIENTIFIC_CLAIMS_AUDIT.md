# Scientific claims audit

Audit date: 2026-10-14. Original model-level result: **INCONCLUSIVE**.

| Claim | Decision | Evidence and allowed wording |
| --- | --- | --- |
| Official checkpoint load and five-output inference succeeded | Supported historical observation | Preserved execution record; whitelisted checks in `results/pilot_controls.json`; no inference rerun |
| Opposite yaw and matched-noise controls passed | Supported historical observation | Action tensor/index, serialized noise and latent/embedding checks; commands are not physical reference truth |
| M0 tracking shows severe asymmetric attrition | Supported algorithmic observation | 96/96 A support versus 21/96 and 9/96 B support; source has no reseeding |
| M2 passed the synthetic suite | Supported, bounded | 13/13 cases on each fixed instance, ten geometry controls, all declared original selection gates; scope and dependency versions disclosed |
| M2 is state of the art or generally validated pose estimation | Unsupported; excluded | Only horizontal pixel motion in a narrow procedural suite; no external pose benchmark |
| M2 improved Astra performance | Unsupported; excluded | Changing an estimator does not modify or improve the model |
| All five M2 real outputs fail 85% coverage | Supported | Counts 75,38,75,73,56 out of 96; original denominators preserved |
| High conditional direction agreement means full-video action accuracy | Unsupported; excluded | Informative missingness; internal direction consistency is not independent truth |
| V2 is independent blinded human ground truth | False; excluded | AI-assisted proposals reviewed by the user; no manual coordinate remeasurement or independently confirmed identity |
| V2 gives more source-linked proposals for M2 | Supported descriptive concordance | 28/120 versus 4/120; eligibility-restricted counts 20/120 and 4/120; linkage is not correctness |
| M2 is more accurate than M0 from V2 | Unsupported; excluded | Zero common linked proposals; method-specific supports are disjoint; shared tracking mechanisms |
| Zero correct matches or zero false-match rates | Unsupported; excluded | Independent correctness, false-match and rejected-valid rates are unavailable, not zero |
| Visibility loss or a model defect is the sole cause | Unsupported; excluded | Wrong correspondences, FOV/visibility and appearance change are unresolved possible contributors |
| Physical yaw fidelity or an Astra control defect is established | Unsupported; excluded | No calibrated real-video physical trajectory or independent geometric reference |
| This study reproduces/refutes the paper's action-following benchmark | Unsupported; excluded | Different scene/seed/guidance design; published human and MegaSaM evaluations acknowledged |

The final V2 assessment and 27 manifest entries were verified without executing its analysis scripts. Its original conclusion and zero-paired-support finding are preserved. The public annotation table contains only four aggregate rows, not raw coordinates, reviewer information or declarations.

Scientific limitations constrain what can be published, rather than requiring fabricated completion. An independent blinded reference remains unfulfilled; a limitations-focused inconclusive report can be released after the workflow/owner publication gates are resolved. A physical-fidelity or relative-accuracy claim would require new independent evidence and is outside this candidate.
