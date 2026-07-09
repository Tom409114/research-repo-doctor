# Agent workflows

Research Repo Doctor is deterministic, but its output is designed to drive a
coding agent. The result is a closed loop where the scanner is the source of truth
and the agent does the editing, with no lock-in to any particular tool.

## The loop

1. **Audit**: `rrdoctor scan .` produces deterministic findings.
2. **Plan**: `rrdoctor plan .` turns findings into a tool-agnostic work order.
3. **Apply**: run `rrdoctor fix --write` for the mechanical items, and hand the
   remaining tasks to any coding agent (or do them yourself).
4. **Verify**: `rrdoctor scan . --baseline before.json --fail-on-new error`
   confirms the changes resolved findings without introducing new ones.

Because step 4 is deterministic and needs no API key, it works as an honest grader
for changes made by any agent.

## Generate a fix plan

```bash
rrdoctor plan . --output fix-plan.md
```

The plan is a Markdown prompt. Each task names the rule, the files to touch, the
change to make, and the deterministic check that verifies it. Paste it into your
agent of choice, attach it to an issue, or commit it for contributors to pick up.

A JSON form is available for programmatic use:

```bash
rrdoctor plan . --format json --output fix-plan.json
```

You can also emit the plan directly from a scan:

```bash
rrdoctor scan . --format agent --output fix-plan.md
```

## AGENTS.md

The plan pairs naturally with an `AGENTS.md` file at the repository root: a short,
machine-readable guide describing setup, test and lint commands, and conventions.
`rrdoctor fix` can scaffold one (rule RRD014), and rule RRD014 flags repositories
that lack one under the strict profile.

## GitHub Copilot instructions

GitHub Copilot also supports repository-wide custom instructions at
`.github/copilot-instructions.md`. Research Repo Doctor keeps one in this
repository so Copilot Chat, Copilot code review, and Copilot cloud agent see the
same deterministic verify loop:

```bash
rrdoctor scan . --format json --output baseline.json
rrdoctor plan . --output plan.md
rrdoctor scan . --baseline baseline.json --fail-on-new error
```

For your own research repository, copy the same loop into `AGENTS.md`,
`.github/copilot-instructions.md`, or the equivalent instruction file for your
agent so rrdoctor remains the grader and the agent remains the editor.

## Copyable agent templates

Ready-to-copy templates live under `integrations/`:

- `integrations/agent-skills/rrdoctor-verify/SKILL.md` for Agent Skills /
  Claude Code-style skill workflows.
- `integrations/cursor/rrdoctor-verify.mdc` for Cursor project rules.
- `integrations/github-copilot/copilot-instructions.md` for GitHub Copilot
  Chat, Copilot code review, and Copilot coding agent.

Copy the relevant template into the research repository you want the agent to
edit. The template tells the agent to create a baseline, work through
`rrdoctor plan`, and treat `rrdoctor scan --baseline baseline.json
--fail-on-new error` as the definition of done.

## Why deterministic plus agent

A deterministic checker is reproducible, auditable, and trustworthy, but it cannot
write prose or judge intent. A coding agent is great at editing but needs a clear
specification and an objective way to know it succeeded. Combining them gives you
both: a precise work order and a verifiable definition of done.
