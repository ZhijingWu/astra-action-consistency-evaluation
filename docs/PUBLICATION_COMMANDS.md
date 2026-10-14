# Review-only GitHub publication commands — DO NOT EXECUTE YET

Proposed repository: `ZhijingWu/astra-action-consistency-evaluation`.

Run these only from this repository root after the final analysis workflow is confirmed complete, every blocker is reconciled, and the owner explicitly approves public publication of the reviewed commit. Approval is currently absent. Nothing below was executed during preparation. No remote has been configured.

First update the status text in README/readiness/blockers, audit the changed bytes, regenerate the file inventory and SHA manifest, and commit those changes locally. Re-run the CPU tests and these checks:

```bash
python -m unittest discover -s tests -v
python tools/release_audit.py
python tools/release_audit.py --verify-manifest
git status --short
git ls-files
git log -1 --oneline
```

The following are the exact proposed creation/push commands for an approved candidate. If a repository with this name already exists, stop and reconcile it; do not force-push or overwrite.

```bash
gh repo create ZhijingWu/astra-action-consistency-evaluation --public --description "Independent Astra image-motion estimator diagnostics, bounded synthetic validation, and explicit coverage abstention; model-level result inconclusive."
git remote add origin https://github.com/ZhijingWu/astra-action-consistency-evaluation.git
git push -u origin main
```

There is no GitHub Pages, release, archive or public-gist command. CLI authentication must already be available through the owner's normal setup; never put tokens into repository files or remote URLs.
