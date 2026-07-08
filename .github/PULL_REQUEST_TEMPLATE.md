## Summary

## Checklist

- [ ] Tests or fixtures cover the change.
- [ ] `ruff check .` passes.
- [ ] `ruff format --check .` passes.
- [ ] `python -m pytest -q` passes.
- [ ] `python -m mypy` passes.
- [ ] `rrdoctor scan . --profile standard --fail-on none` still reports no blocking findings.
- [ ] Rule docs were updated if rule behavior changed.
- [ ] No network dependency was added to the core scanner.
- [ ] Dynamic verification changes keep `--run` trusted-only and timeout-bounded.
