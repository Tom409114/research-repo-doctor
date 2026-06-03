# Security Policy

## Supported versions

The project is pre-1.0. Security fixes will target the latest released version and the default branch.

## Reporting a vulnerability

Please do not open a public issue for suspected credential exposure, secret masking bypasses, or report-generation leaks. Email the maintainer contact listed on the GitHub repository through the repository security contact.

Include:

- A minimal reproduction or fixture.
- The affected rule or report format.
- Whether any real credential was exposed.

## Scanner safety expectations

Research Repo Doctor should not make network calls during normal scans, should not require API keys, and should mask possible secrets in evidence.
