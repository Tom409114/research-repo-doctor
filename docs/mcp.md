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

## Registry metadata

The repository versions its official MCP Registry metadata in
[`server.json`](../server.json). The PyPI package remains lightweight by keeping
the MCP SDK in the `mcp` extra; the registry launch metadata therefore resolves
to the same explicit command shown above instead of adding the SDK to every CLI
installation.

The official MCP Registry is currently a preview service. Version `0.2.24` is
published with active status under
[`io.github.Tom409114/rrdoctor`](https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.Tom409114/rrdoctor).
That public record is a distribution mechanism, not an endorsement or evidence
of user adoption. The direct client configuration below remains the most
portable setup path.

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
| `scan(path=".", profile=null)` | Return the Markdown reproducibility audit; an omitted profile uses repository config or `standard`. |
| `verify(path=".", profile=null, run=false, command=null, timeout=300)` | Return the L1/L2/L3 verification ladder; an omitted profile uses repository config or `standard`. |
| `appendix(path=".", profile="acm")` | Return the ACM-style Artifact Appendix plus checklist mapping. |

## Safety

`scan` and static `verify` are deterministic local analysis. They do not require
an API key and do not install or execute the target repository.

`verify(run=true, timeout=600)` creates a temporary isolated environment and
installs declared dependencies for supported Python repositories, then runs the
detected entrypoint under an explicit timeout. Dependency installation may run
project build hooks; other ecosystems retain a resolver preflight. Pass
`command="python train.py config/default.py"` to pin the artifact's official
quickstart command as the L3 gate. Use dynamic verification only on repositories
you trust, just like `rrdoctor verify --run` on the command line.

## Agent prompt

Paste this into Claude Code, Cursor, GitHub Copilot, or another MCP-capable
coding agent:

```text
Use the rrdoctor MCP server as the deterministic grader for this repository.
First call scan(path=".", profile="standard") and summarize the highest-impact
findings. Make changes without weakening rrdoctor checks. Then call scan again
and stop only when no new error-level findings remain. If this repository is
trusted, call verify(path=".", profile="standard", run=true, timeout=600) as the
final run-path gate.
```
