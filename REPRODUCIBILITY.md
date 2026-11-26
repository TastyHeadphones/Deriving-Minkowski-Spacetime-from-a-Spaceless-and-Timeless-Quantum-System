# Reproduce the research

Run commands from the repository root. The Lean toolchain is pinned in lean-toolchain, and lake-manifest.json pins Mathlib and its dependencies. Install Elan from its official project or put the corresponding Lean release's bin directory on PATH. Python 3.12 is required and .python-version records the CI patch release. The browser uses plain ECMAScript modules and the unit tests require Node.js 20 or later, with the CI release recorded in .node-version. Pandoc with MathML rendering is needed for the HTML paper, and pdflatex with the standard LaTeX packages and Latin Modern is needed for PDF output.

## Lean and the semantic audit

Optional precompiled Mathlib cache and the required local checks:

    lake exe cache get
    lake build
    python3 scripts/verify_proofs.py

If the official cache service is unavailable, omit the cache command and build from the pinned source. An uncached first build takes several minutes. Keep the committed Lake manifest, and avoid updating dependencies during verification.

The audit compiles generated Lean commands that check declarations, print their kernel axioms, and compute their direct project constants. It checks the permitted kernel set and registry completeness and acyclicity. A clean checkout binds the report to a commit. The resulting registry, Lean output and dependency graph are in artifacts/proof. A dirty working tree can be audited, but its result is not assigned a verification commit.

The formal graph result uses tokens and an abstract relation. The quantum entropy argument identifying the token intersection with mutual information is analytic. Path-cost laws instantiate reversible walks on connected components. The clock shift is selected in advance and conditional step numbers remain mathematical. The boost test deliberately supplies the target interval as a comparison. No geometric or physical postulate is introduced as a Lean kernel axiom. The static graph check does not decide scientific circularity. Review the working paper whenever assumptions or reconstruction rules change.

## Science and static site

    python3 -m unittest discover -s tests -v
    python3 -m experiments.run
    python3 scripts/reproduce.py
    node --test tests/website.test.mjs
    python3 scripts/build_site.py --pdf
    python3 -m http.server 8765 --directory _site

Open the generated site's index from the local server. Omitting --pdf builds HTML only. For deployment add --require-verification after producing the audited reports from a clean checkout. The website reads commit-specific report data, with a source-only display when proof artifacts are unavailable. CI artifacts include the concrete random seed, selected sweep parameters, tool versions, commit and checksums. The reproducibility job regenerates the science files independently of the original job and compares their content. It records the corresponding Lean audit and its artifact checksums.

The GitHub Pages source setting is GitHub Actions. Pull requests and branch pushes exercise the read-only verification pipeline. Only a successful workflow on the repository's default branch can reach the official Pages deployment job. The snapshot links to its own run and to the current Actions history. The deploy job uses the GitHub Pages environment so its branch and approval protections apply.
