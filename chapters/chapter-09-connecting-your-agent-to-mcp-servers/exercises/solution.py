"""
Chapter 9 Exercises: The MCP Integration Logic, Testable Without a Real
MCP Server or a Live Model -- Worked Solution

This is `starter.py` with TODO 1 through TODO 3 filled in. See
`starter.py`'s module docstring and each function's docstring for the
full task description -- nothing else in this file differs.
"""


def strip_injected_args(schema, injected_keys):
    """See starter.py for the full docstring."""
    properties = {
        k: v for k, v in schema.get("properties", {}).items() if k not in injected_keys
    }
    required = [r for r in schema.get("required", []) if r not in injected_keys]
    return {**schema, "properties": properties, "required": required}


def classify_tool_call(name, tool_functions, mcp_tool_names):
    """See starter.py for the full docstring."""
    if name in tool_functions:
        return "local"
    if name in mcp_tool_names:
        return "mcp"
    return "unknown"


def mcp_result_to_text(result, name):
    """See starter.py for the full docstring."""
    if result.is_error:
        text = result.content[0].text if result.content else "unknown MCP error"
        return f"error: MCP tool {name!r} failed: {text}"
    if result.content:
        return result.content[0].text
    return str(result.structured_content)


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
