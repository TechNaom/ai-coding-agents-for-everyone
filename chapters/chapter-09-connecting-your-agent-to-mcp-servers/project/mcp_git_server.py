"""
Chapter 9 Project: A Small MCP Server Exposing Chapter 8's Git Tools

This is NOT part of the agent -- it's a separate, standalone MCP server
process. It re-implements exactly the two read-only git tools Chapter 8
built by hand (git_status, git_diff) as MCP tools instead, using the
`mcp` Python SDK's server-side decorator API. The point of this file
existing at all is the chapter's central argument made concrete: the
SAME two tools, with the SAME behavior, can live behind a protocol
instead of a local Python function -- and a client (this chapter's
agent) that speaks MCP gets them "for free" without hand-writing the
subprocess-calling code again.

Verified against the actually-installed `mcp` package this session
(`pip show mcp` reported version 2.0.0, the current release as of this
build). Note for anyone following older MCP material (including
`mcp-for-everyone`, whose lessons were written against an earlier `mcp`
release): the decorator-based server class most MCP tutorials call
`FastMCP`, importable as `from mcp.server.fastmcp import FastMCP`, was
renamed in this installed version to `MCPServer`, importable as `from
mcp.server.mcpserver import MCPServer` -- same decorator API
(`@mcp.tool()`), same `.run(transport=...)` method, just a different
import path. This file uses the current, live-verified import. If
you're on an older `mcp` release, swap the import for
`mcp.server.fastmcp.FastMCP` and everything else here is unchanged.

Run it standalone (rarely useful on its own -- it just sits and waits
for a client to speak MCP over stdin/stdout):

    pip install "mcp[cli]"
    python3 mcp_git_server.py

In practice you won't run this by hand -- `solution.py` launches it as
a subprocess automatically via MCP's stdio transport. See that file's
`connect_git_tools()` for how.
"""
import subprocess

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("git-tools")


@mcp.tool()
def git_status(workspace: str) -> str:
    """Show the working tree's status (which files are modified, staged,
    or untracked) inside the given workspace directory. Read-only --
    makes no changes. `workspace` must be an absolute path to a git
    repository's working directory."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=workspace,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        return f"error: git status failed: {result.stderr.strip()}"
    return result.stdout or "(clean -- no changes)"


@mcp.tool()
def git_diff(workspace: str, path: str = "") -> str:
    """Show unstaged changes inside the given workspace directory,
    optionally limited to one file. Read-only -- makes no changes.
    `workspace` must be an absolute path to a git repository's working
    directory; `path`, if given, is relative to `workspace`."""
    cmd = ["git", "diff"]
    if path:
        cmd += ["--", path]
    result = subprocess.run(
        cmd, cwd=workspace, capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return f"error: git diff failed: {result.stderr.strip()}"
    return result.stdout or "(no changes)"


if __name__ == "__main__":
    mcp.run(transport="stdio")
