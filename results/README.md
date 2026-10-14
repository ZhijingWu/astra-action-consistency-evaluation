# Public numeric evidence

All data here are source-free numeric records or whitelisted aggregate facts from preserved executed evidence. They contain no scene pixels, checkpoint bytes, reviewer identities, annotation declarations or private paths.

| File | Scope |
| --- | --- |
| synthetic_per_interval.csv | 7,488 rows: 26 cases x 96 intervals x 3 methods, including abstentions/failures |
| synthetic_case_summary.csv | 78 retained case/method summaries; original values preserved |
| synthetic_smoke_reference.csv | 24 original M0/M2 records selected for release regression, not newly fitted targets |
| synthetic_selection.json | Historical bounded gates, control results and original versions |
| astra_M2_per_interval.csv | 480 saved M2 interval records; no raw pixels or real ground truth |
| astra_coverage.csv | Five M0/M2 coverage rows with all 96 intervals in each denominator |
| pilot_controls.json | Historical checkpoint/execution/conditioning/noise checks; not a new run |
| annotation_exploratory_aggregate.csv | Four aggregate method/scope rows; source linkage/concordance, not accuracy |
| annotation_status.json | Reference limitations, zero common linked proposals and inconclusive status |

Empty CSV numerical cells mean unavailable/abstained, never zero. Boolean validity fields control interpretation. The repeat is a duplicate output, not an independent sample. Private originals are hash-linked by logical identifiers in `provenance/sources.json`; their source paths and raw context are excluded. Aggregate extraction is documented there.
