# Agent Skill Templates

This directory contains copyable agent-skill templates for using `rrdoctor` as a
deterministic grader inside coding-agent workflows.

The templates do not require an API key and do not change how rrdoctor scans a
repository. They teach an agent to:

1. create a baseline scan,
2. generate a fix plan,
3. make changes without weakening rrdoctor checks, and
4. stop only when the baseline gate passes.

## Claude Code / Agent Skills

Copy the `rrdoctor-verify` skill into a project-level or user-level skills
directory supported by your agent, then invoke it as the agent's review or
definition-of-done workflow.

## Cursor

Copy `../cursor/rrdoctor-verify.mdc` into `.cursor/rules/` in the research
repository you want Cursor to edit.

Keep the skill/rule in the target research repository, not in rrdoctor itself,
when you want the agent to grade that repository.
