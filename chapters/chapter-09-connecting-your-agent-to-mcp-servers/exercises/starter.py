"""
Chapter 9 Exercises: The MCP Integration Logic, Testable Without a Real
MCP Server or a Live Model

This file tests the three pieces of `project/solution.py`'s MCP
integration that carry real design risk -- the schema translation that
must correctly hide the harness-injected `workspace` argument from the
model, the dispatch-routing decision that must correctly tell a local
tool apart from an MCP tool, and the result-unpacking logic that must
correctly handle an MCP tool's error vs. success shape -- against small
FAKE stand-ins instead of a real mcp package or a real subprocess. No
`openai`, no `mcp`, no Ollama, no network: just Python.

Fill in TODO 1 through TODO 3 in the three functions below, then run:

    python3 starter.py

The built-in test harness at the bottom runs 11 checks and prints
PASS/FAIL for each. Compare against `solution.py` (`python3 solution.py`,
should print `11/11 checks passed.`) if you get stuck.
"""


def strip_injected_args(schema, injected_keys):
    """
    Given an MCP tool's raw input schema (a dict with "properties" and
    "required" keys, JSON-Schema style) and a set of argument names the
    harness injects itself (never shown to or set by the model), return
    a NEW schema dict with those keys removed from BOTH "properties"
    and "required" -- everything else in the schema unchanged.

    This mirrors exactly what project/solution.py's connect_git_tools()
    does before appending a discovered MCP tool to TOOLS: the model
    should never see `workspace` in a tool's schema, because it has no
    reliable way to supply the right absolute path, and shouldn't need
    to -- the harness injects it back in later, in dispatch_tool_call.

    TODO 1: implement this. Do not mutate the input `schema` -- return
    a new dict. `schema` may be missing "properties" or "required"
    entirely; handle that the same way project/solution.py's real
    version does (treat a missing key as empty).
    """
    raise NotImplementedError("strip_injected_args: TODO 1")


def classify_tool_call(name, tool_functions, mcp_tool_names):
    """
    Given a tool name and the two lookup structures dispatch_tool_call
    actually uses (a dict of local Python functions, and a set of names
    known to be MCP tools), return one of the three strings "local",
    "mcp", or "unknown" -- exactly the three outcomes
    project/solution.py's dispatch_tool_call branches on.

    TODO 2: implement this. Check `tool_functions` first, exactly the
    order project/solution.py's real dispatch_tool_call checks them in
    -- this ordering matters for exercise 4 below, which asks you to
    reason about what happens if a name appears in both.
    """
    raise NotImplementedError("classify_tool_call: TODO 2")


def mcp_result_to_text(result, name):
    """
    Given a fake MCP call_tool() result object with `.is_error` (bool),
    `.content` (a list of objects with a `.text` attribute, or an empty
    list), and `.structured_content` attributes, plus the tool's own
    `name` (a real MCP result object doesn't carry it, so it's passed
    in separately), return the string dispatch_tool_call should
    actually pass back to the model as the tool result -- mirroring
    MCPBridge._worker's real result-unpacking logic in
    project/solution.py exactly:

      - If `result.is_error` is True: return
        f"error: MCP tool {name!r} failed: {text}" where `text` is
        `result.content[0].text` if content is non-empty, otherwise the
        literal string "unknown MCP error".
      - Else, if `result.content` is non-empty: return
        `result.content[0].text`.
      - Else: return `str(result.structured_content)`.

    TODO 3: implement this.
    """
    raise NotImplementedError("mcp_result_to_text: TODO 3")


# ---------------------------------------------------------------------------
# Fakes -- small stand-ins for the real MCP/tool-call shapes, just enough
# to exercise the three functions above without a real mcp package.
# ---------------------------------------------------------------------------
class FakeContentBlock:
    def __init__(self, text):
        self.text = text


class FakeMCPResult:
    def __init__(self, is_error=False, content=None, structured_content=None):
        self.is_error = is_error
        self.content = content or []
        self.structured_content = structured_content


def main():
    checks = []

    def check(label, actual, expected):
        ok = actual == expected
        checks.append(ok)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
        if not ok:
            print(f"       expected: {expected!r}")
            print(f"       actual:   {actual!r}")

    # --- strip_injected_args ---
    schema1 = {
        "type": "object",
        "properties": {
            "workspace": {"type": "string"},
            "path": {"type": "string"},
        },
        "required": ["workspace", "path"],
    }
    result1 = strip_injected_args(schema1, {"workspace"})
    check(
        "strip_injected_args removes workspace from properties",
        "workspace" not in result1.get("properties", {}),
        True,
    )
    check(
        "strip_injected_args removes workspace from required",
        "workspace" not in result1.get("required", []),
        True,
    )
    check(
        "strip_injected_args keeps unrelated properties untouched",
        result1.get("properties", {}).get("path"),
        {"type": "string"},
    )
    check(
        "strip_injected_args does not mutate the original schema",
        "workspace" in schema1["properties"],
        True,
    )

    schema2 = {"type": "object", "properties": {"n": {"type": "integer"}}}
    result2 = strip_injected_args(schema2, {"workspace"})
    check(
        "strip_injected_args handles a schema with no 'required' key at all",
        result2.get("required", []),
        [],
    )

    # --- classify_tool_call ---
    tool_functions = {"read_file": lambda: None, "write_file": lambda: None}
    mcp_tool_names = {"git_status", "git_diff"}
    check(
        "classify_tool_call finds a local tool",
        classify_tool_call("read_file", tool_functions, mcp_tool_names),
        "local",
    )
    check(
        "classify_tool_call finds an MCP tool",
        classify_tool_call("git_status", tool_functions, mcp_tool_names),
        "mcp",
    )
    check(
        "classify_tool_call reports unknown for neither",
        classify_tool_call("delete_everything", tool_functions, mcp_tool_names),
        "unknown",
    )

    # --- mcp_result_to_text ---
    ok_result = FakeMCPResult(is_error=False, content=[FakeContentBlock("?? notes.txt\n")])
    check(
        "mcp_result_to_text returns content text on success",
        mcp_result_to_text(ok_result, "git_status"),
        "?? notes.txt\n",
    )

    err_result = FakeMCPResult(is_error=True, content=[FakeContentBlock("not a git repository")])
    check(
        "mcp_result_to_text formats an error with the tool name",
        mcp_result_to_text(err_result, "git_status"),
        "error: MCP tool 'git_status' failed: not a git repository",
    )

    empty_result = FakeMCPResult(is_error=False, content=[], structured_content={"files": []})
    check(
        "mcp_result_to_text falls back to structured_content when content is empty",
        mcp_result_to_text(empty_result, "git_status"),
        "{'files': []}",
    )

    n_passed = sum(checks)
    print(f"\n{n_passed}/{len(checks)} checks passed.")


if __name__ == "__main__":
    main()
