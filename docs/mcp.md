# MCP (Model Context Protocol)

Connect GenIce3 to an AI client (Cursor, Claude Desktop, and other MCP hosts) so the assistant can list lattices/exporters and generate structures in chat.

This is **not** a public web service. The client starts `genice3-mcp` as a local subprocess and talks over stdin/stdout. No always-on HTTP server is required.

**Who this is for:** people who already use an MCP-capable coding agent **and** want ice / clathrate hydrate coordinates without leaving the chat. For CLI recipes and docs for agents, prefer the [agent skill](for-ai-assistants.md) (`npx skills add genice-dev/GenIce3`). Use **both** if you want: skill for how to run `genice3`, MCP when the model should call GenIce3 as a tool.

## Install

```shell
pip install "genice3[mcp]"
which genice3-mcp    # must resolve; the AI client launches this as a subprocess
```

Do not run `genice3-mcp` by hand in a terminal for normal use: it speaks MCP on stdin/stdout and waits for a client. Confirm it is on the **same** `PATH` (or Python env) that the AI client uses.

## Client configuration

Add a server entry so the client can launch GenIce3. Exact file location depends on the host (Cursor MCP settings, Claude Desktop `claude_desktop_config.json`, etc.).

**If `genice3-mcp` is on PATH:**

```json
{
  "mcpServers": {
    "genice3": {
      "command": "genice3-mcp"
    }
  }
}
```

**If you prefer not to rely on PATH** (example with `uvx`):

```json
{
  "mcpServers": {
    "genice3": {
      "command": "uvx",
      "args": ["--from", "genice3[mcp]", "genice3-mcp"]
    }
  }
}
```

Restart or reload MCP servers in the client after editing. Then ask something concrete, e.g. “List GenIce3 unit cells” or “Generate ice Ih as GROMACS GRO”.

## Tools

| Tool | Role |
|------|------|
| `list_unitcells` | Lattice / framework names and short descriptions |
| `list_exporters` | Output formats |
| `get_unitcell_options` | Option schema for one unit cell |
| `get_exporter_options` | Metadata for one exporter (including `media_type`) |
| `generate` | Build a structure; `config` is the same YAML / TOML / JSON (or object) as CLI `-Y` |

Typical flow: list → inspect options → `generate`. Omitted `seed` defaults to `1`. Success payload shape matches the Web API wrap: `{meta, content, media_type}`.

## Limits

- Same surface as CLI YAML / the HTTP API: **not** protonic or Bjerrum topological defects (those remain Python-API-only).
- Remote / HTTP MCP transport is not provided; stdio only for now.
- Design notes (Japanese): [WebAPI.md](https://github.com/genice-dev/GenIce3/blob/main/WebAPI.md) in the repository.

## Skill vs MCP

| | Agent skill | MCP (`genice3-mcp`) |
|--|-------------|---------------------|
| What it gives the AI | Docs and workflow for running `genice3` | Direct tool calls into GenIce3 |
| Install | `npx skills add genice-dev/GenIce3` | `pip install "genice3[mcp]"` + client JSON |
| Best when | Teaching the agent the CLI / options | Generating structures from chat without shell steps |
