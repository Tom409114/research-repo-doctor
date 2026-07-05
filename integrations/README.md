# Integrations

Copyable integration templates for using rrdoctor outside the plain CLI.

- [Agent skill templates](agent-skills/) package the rrdoctor baseline -> plan ->
  verify loop for Agent Skills / Claude Code-style workflows.
- [Cursor project rule](cursor/rrdoctor-verify.mdc) gives Cursor the same
  deterministic definition of done.

The core scanner remains deterministic, local-first, and key-free. These
templates only teach an agent how to run rrdoctor; they do not require a hosted
service or an AI API.
