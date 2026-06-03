# FAQ

## Does rrdoctor use AI?

No. The user-facing scanner is deterministic and local-first. Maintainers may use AI-assisted tools for project maintenance, but scans do not require API keys.

## Does rrdoctor prove a paper is reproducible?

No. It finds repository hygiene and reproducibility risks. Scientific validity still requires review, reruns, and domain expertise.

## Can I disable a noisy rule?

Yes. Use `.rrdoctor.yml`:

```yaml
rules:
  RRD060:
    enabled: false
```

## Why is SARIF experimental?

The v0.1.0 SARIF output is valid JSON with SARIF-compatible structure, but deeper code scanning integration will be refined after early feedback.
