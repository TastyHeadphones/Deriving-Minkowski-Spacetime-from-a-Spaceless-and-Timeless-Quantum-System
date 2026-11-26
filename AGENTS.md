# Research and repository rules

Use the existing checkout in the isolated workspace. Load README.md and REPRODUCIBILITY.md first. No worktree is needed unless requested.

- Treat microscopic labels, clock indices and modular parameters as mathematical objects until an operational interpretation is established.
- State the microscopic assumptions, extra model structure, reconstruction rule and comparison geometry in each result. Audit for hidden space, time, dimension, cone or speed assumptions.
- Prefer explicit countermodels. Keep hypotheses, analytic proofs, Lean results and numerical evidence distinguishable.
- Do not use proof placeholders, new unexplained axioms or unsafe proof mechanisms. Build with Lake, run the project audit and inspect the reported dependencies before claiming verification.
- Keep the registries and paper tied to each changed theorem. Preserve negative results in the counterexample catalogue and milestones. Include limitations and correction history.
- Run the documented experiment and website checks when changing those components. Work with pinned tools and record versions and Git SHA in generated reports.
- CI runs deterministic builds and experiments. Publication uses the authorized default branch and Pages environment. Treat external publication and repository settings as user-governed.
