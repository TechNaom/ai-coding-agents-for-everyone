"""
Chapter 8 Exercises: A Safer Edit Tool and a Shell Command Denylist

These exercises don't require a running Ollama server. They test the two
pieces of this chapter's tool layer that don't need a live model to
verify: edit_file's ambiguous-match-refusal logic, and the denylist
check run_shell_command uses before executing anything.

Run this file directly to see PASS/FAIL for each exercise:

    python3 solution.py

This is the reference solution -- compare it against your own starter.py
once you've filled in edit_file_stub and is_command_blocked.
"""
import re

# ---------------------------------------------------------------------------
# A tiny in-memory "filesystem", same pattern Chapter 7's exercises used --
# these tests run instantly and deterministically, with no real disk I/O.
# ---------------------------------------------------------------------------
FAKE_DISK = {
    "config.py": "TIMEOUT = 30\nRETRIES = 3\n",
    "dup.py": "return None\nreturn None\n",
}


# ---------------------------------------------------------------------------
# Exercise 1: edit_file_stub
# ---------------------------------------------------------------------------
def edit_file_stub(path, find, replace):
    """
    A stand-in for the lesson's real edit_file, operating on FAKE_DISK
    instead of the real filesystem, so it's fast and needs no I/O.

    TODO 1: If `path` isn't a key in FAKE_DISK, return the string:
                f"error: no such file: {path}"

    TODO 2: Count how many times `find` appears in FAKE_DISK[path]
            (use str.count()). If it's 0, return the string:
                f"error: text not found in {path}: {find!r}"

    TODO 3: If it appears more than once, return the string:
                f"error: text {find!r} appears {count} times in {path} -- ambiguous"
            (where `count` is the actual number of occurrences).

    TODO 4: Otherwise, replace the ONE occurrence (use str.replace with
            a count of 1), store the new content back into
            FAKE_DISK[path], and return the string:
                f"replaced 1 occurrence in {path}"

    This function must never raise -- every case above returns a string.
    """
    if path not in FAKE_DISK:
        return f"error: no such file: {path}"

    content = FAKE_DISK[path]
    count = content.count(find)
    if count == 0:
        return f"error: text not found in {path}: {find!r}"
    if count > 1:
        return f"error: text {find!r} appears {count} times in {path} -- ambiguous"

    FAKE_DISK[path] = content.replace(find, replace, 1)
    return f"replaced 1 occurrence in {path}"


# ---------------------------------------------------------------------------
# Exercise 2: is_command_blocked
# ---------------------------------------------------------------------------
DENYLIST = [
    (r"rm\s+-rf\s+/(\s|$)", "recursive delete of the filesystem root"),
    (r"\bsudo\b", "privilege escalation"),
    (r"git\s+push\b.*--force", "force-push"),
]


def is_command_blocked(command):
    """
    Check `command` against every (pattern, reason) pair in DENYLIST.

    TODO 1: Walk through DENYLIST in order. For each (pattern, reason)
            pair, use re.search(pattern, command) to check for a match.

    TODO 2: If any pattern matches, return that pattern's `reason`
            string immediately (don't keep checking the rest).

    TODO 3: If nothing in DENYLIST matches, return None.
    """
    for pattern, reason in DENYLIST:
        if re.search(pattern, command):
            return reason
    return None


# ---------------------------------------------------------------------------
# Test harness -- do not need to edit anything below this line.
# ---------------------------------------------------------------------------
def _check(label, actual, expected):
    status = "PASS" if actual == expected else "FAIL"
    print(f"[{status}] {label} -> got {actual!r} (expected {expected!r})")
    return status == "PASS"


def main():
    results = []

    # --- edit_file_stub ---
    results.append(_check(
        "well-formed edit",
        edit_file_stub("config.py", "TIMEOUT = 30", "TIMEOUT = 60"),
        "replaced 1 occurrence in config.py",
    ))
    results.append(_check(
        "edit actually changed the content",
        FAKE_DISK["config.py"],
        "TIMEOUT = 60\nRETRIES = 3\n",
    ))
    results.append(_check(
        "text not found",
        edit_file_stub("config.py", "nope", "x"),
        "error: text not found in config.py: 'nope'",
    ))
    results.append(_check(
        "ambiguous match (appears twice)",
        edit_file_stub("dup.py", "return None", "return 0"),
        "error: text 'return None' appears 2 times in dup.py -- ambiguous",
    ))
    results.append(_check(
        "no such file",
        edit_file_stub("missing.py", "x", "y"),
        "error: no such file: missing.py",
    ))

    # --- is_command_blocked ---
    results.append(_check(
        "ordinary command is not blocked",
        is_command_blocked("ls -la"),
        None,
    ))
    results.append(_check(
        "rm -rf / is blocked",
        is_command_blocked("rm -rf /"),
        "recursive delete of the filesystem root",
    ))
    results.append(_check(
        "sudo is blocked",
        is_command_blocked("sudo apt install curl"),
        "privilege escalation",
    ))
    results.append(_check(
        "force-push is blocked",
        is_command_blocked("git push origin main --force"),
        "force-push",
    ))

    passed = sum(results)
    print(f"\n{passed}/{len(results)} checks passed.")
    if passed != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
