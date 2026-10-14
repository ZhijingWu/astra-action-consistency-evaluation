# Frozen methodology and interpretation

The primary M0 source is byte-identical to the existing pilot implementation. Its initial mask is the union of five frozen rectangles in `configs/synthetic_frozen.json`. It never reseeds. M1/M2 are the unchanged independent synthetic-validation implementation, not Astra's own evaluation code.

M0's fixed initial left-side support is unsuitable as a symmetric directional instrument when landmarks leave the frame or lose appearance support. M2 resamples the full tiled image at each pair. This changes feature locations and quality rules as well as survival requirements. No ablation isolates those individual changes.

## Geometry and convention

Images are 832 x 480 at 20 FPS. Synthetic K has fx=fy=600, cx=416, cy=240. Coordinates are X right, Y down, Z forward. The world-to-camera rotation is R_y(theta); physical camera heading is minus theta. Positive theta transports a central static projection to the right. Its central displacement is 600 tan(theta), so image displacement sign is not a universal direct physical-yaw label.

The renderer ray-casts a distant plane at Z=12 and a bounded nearer textured rectangle at Z=7. An optional untextured foreground slab at Z=3 moves sinusoidally, deliberately creating visibility transitions. The slab is excluded from trustworthy textured static support. A finite world bounds field-of-view departures. Textures are procedural, deterministic and world-anchored; no external image is used. Attrition removes predefined hashed patches in four stages. Blank/changing texture cases can retain geometric surfaces while removing usable image evidence.

Exact support within this renderer requires an in-bounds next projection, nearest-surface identity agreement, world residual below 1e-6, textured appearance at both frames and unchanged texture epoch. The truth grid has stride 8. Adequacy requires at least 10% supported grid samples covering six cells. Accepted-point correctness for synthetic scoring additionally uses 1.5-pixel endpoint tolerance; at least 80% truth-supported correspondences are required for a supported claim. These oracle labels are never passed to the image-only trackers.

## Prospective synthetic gates

On each truth-adequate case: coverage >=0.85, conditional direction accuracy >=0.98, median absolute signed error <=0.50 px, 95th percentile <=1.50 px. Zero/blank controls require 95th-percentile absolute estimate <=0.10 px. False-valid fraction on inadequate evidence is <=0.02 per case and <=0.01 overall; fraction of unsupported claims is <=0.02. Repeated renders/measurements must be exact, reversed renders must match reversed sequence hashes, and all geometry controls must pass. These are this study's declared instrument requirements, not calibrated universal thresholds.

The original development/held-out instances each contain 13 cases, not 13 independent populations; repeat and reversal cases are related. M2 precedes M1 in the frozen selection priority; M0 is ineligible for replacement. No threshold search or new configuration is performed by release preparation.

## Real outputs and annotations

Real-output eligibility is evaluated without oracle geometry. The frozen M2 aggregate rule requires >=85% of all 96 intervals and >=90% internal direction agreement conditional on valid intervals. Every real output fails coverage. Missing intervals remain abstentions; neither conditional medians nor coverage alone establish physical action following.

V2's 3-pixel linkage radius is a source-location proximity rule, not an identity or correctness test. Its 0.25-pixel direction deadband is descriptive. AI-generated proposals share Lucas-Kanade and forward/backward mechanisms with the evaluated trackers, and patch filtering with M2. Source supports are disjoint, endpoints are not manually remeasured, and background identity is unclear. No inference about relative accuracy, causal failure contributions, independent truth or physical yaw is supported.
