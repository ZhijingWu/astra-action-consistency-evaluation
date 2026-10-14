# Derived coverage figure

Question: how much of each retained rollout is eligible under each estimator's original rules?

`astra_coverage.png` and `astra_coverage.svg` plot exact M0/M2 valid-interval counts from `results/astra_coverage.csv`, divided by 96. The y-axis begins at zero. The dashed 85% line is the frozen M2 video-level coverage requirement. A17_repeat is marked as an exact duplicate. Counts and percentage bars are descriptive; no error bars, confidence intervals or physical action-fidelity measurement are implied.

Only numerical aggregates are used. No source image, generated frame, paper screenshot or annotation overlay is embedded. Both rendered formats were created with Matplotlib; the PNG was visually inspected for readable labels, denominator accuracy, legend and lack of clipping. Recreate in a new directory with `python tools/plot_coverage.py --output scratch/figures` after installing `requirements-figures.txt`.
