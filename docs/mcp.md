# MCP Integration

Research Repo Doctor can run as a Model Context Protocol (MCP) server so coding
agents can call the same deterministic checks you run locally. This keeps the
agent loop honest: the agent can edit, but rrdoctor remains the offline,
key-free grader.

## Install

Install the optional MCP extra:

```bash
python -m pip install "rrdoctor[mcp]"
```

Or run it without a permanent install from an MCP client that supports command
and arguments:

```bash
uvx --from "rrdoctor[mcp]" rrdoctor mcp
```

## Smoke test

Check that the optional dependency is visible:

```bash
rrdoctor doctor
```

The JSON output should include:

```json
{
  "optional_dependencies": {
    "mcp": true
  }
}
```

For a local build from source, the same check is:

```bash
python -m pip install -e ".[mcp]"
python - <<'PY'
from rrdoctor.mcp_server import build_server

build_server()
print("rrdoctor MCP server builds successfully")
PY
```

## Generic stdio server config

Most MCP clients accept a command-plus-args block. Use this shape and adapt the
file location to your client:

```json
{
  "mcpServers": {
    "rrdoctor": {
      "command": "uvx",
      "args": ["--from", "rrdoctor[mcp]", "rrdoctor", "mcp"]
    }
  }
}
```

If you installed rrdoctor into the environment already, use:

```json
{
  "mcpServers": {
    "rrdoctor": {
      "command": "rrdoctor",
      "args": ["mcp"]
    }
  }
}
```

## Exposed tools

| Tool | Purpose |
| --- | --- |
| `scan(path=".", profile="standard")` | Return the Markdown reproducibility audit. |
| `verify(path=".", profile="standard", run=false)` | Return the L1/L2/L3 verification ladder. |
| `appendix(path=".", profile="acm")` | Return the ACM-style Artifact Appendix plus checklist mapping. |

## Safety

`scan` and static `verify` are deterministic local analysis. They do not require
an API key and do not install or execute the target repository.

`verify(run=true)` resolves dependencies and runs the detected entrypoint under
the normal rrdoctor timeout. Use it only on repositories you trust, just like
`rrdoctor verify --run` on the command line.

## Agent prompt

Paste this into Claude Code, Cursor, GitHub Copilot, or another MCP-capable
coding agent:

```text
Use the rrdoctor MCP server as the deterministic grader for this repository.
First call scan(path=".", profile="standard") and summarize the highest-impact
findings. Make changes without weakening rrdoctor checks. Then call scan again
and stop only when no new error-level findings remain.
```
