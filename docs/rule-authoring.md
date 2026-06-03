# Rule Authoring

Rules live in `src/rrdoctor/rules/`. Each rule class provides metadata and a deterministic `check(context)` method.

## Contract

- No network calls.
- No API keys.
- Respect configured excludes by using `context.files`.
- Avoid binary file reads except size checks.
- Mask secret-like values in evidence.
- Return actionable remediation.
- Keep false positives explainable.

## New rule checklist

- [ ] The rule has a clear research reproducibility or release-readiness risk.
- [ ] The evidence can be detected deterministically without network access.
- [ ] The finding message is specific and avoids moralizing.
- [ ] The remediation tells a maintainer what to change next.
- [ ] Secret-like evidence is masked before it reaches reports.
- [ ] The rule respects configured excludes.
- [ ] The default severity is justified.
- [ ] The rule belongs to the right profile or is configurable.
- [ ] A fixture or focused test covers the positive case.
- [ ] A healthy fixture or focused test covers the non-finding case when feasible.
- [ ] `docs/checks.md` is updated.

## Testing expectations

Add a focused unit test and, when useful, a tiny fixture under `tests/fixtures/`.

Good tests check:

- The rule emits a finding for the risky case.
- The rule stays quiet for a healthy fixture.
- Evidence is masked or stable when relevant.

## Documentation

Update `docs/checks.md`, the README rule category list if needed, and `AGENTS.md` if the architecture changes.
