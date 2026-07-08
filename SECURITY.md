# Security Policy

## Supported versions

The project is pre-1.0. Security fixes will target the latest released version and the default branch.

## Reporting a vulnerability

Please do not open a public issue for suspected credential exposure, secret
masking bypasses, report-generation leaks, or unsafe dynamic-verification
behavior.

Use GitHub private vulnerability reporting instead:

<https://github.com/Tom409114/research-repo-doctor/security/advisories/new>

Include:

- A minimal reproduction or fixture.
- The affected rule or report format.
- Whether any real credential was exposed.
- Whether the issue affects static scanning, generated reports, the GitHub
  Action, MCP integration, or trusted-only `verify --run`.

## Scanner safety expectations

Research Repo Doctor should not make network calls during normal scans, should
not require API keys, and should mask possible secrets in evidence. Dynamic
verification with `verify --run` is different: it resolves dependencies and
executes target repository code, so it must be used only on repositories the
operator trusts and only under an explicit timeout.
