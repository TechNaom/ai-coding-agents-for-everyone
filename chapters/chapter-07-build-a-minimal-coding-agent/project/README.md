# Chapter 7 Project: The Reference Minimal Agent

This isn't a fill-in-the-blank project yet — the real Level 2 (Assisted)
project, "extend a provided minimal agent with one new tool, partial
scaffold," unlocks after Chapter 8, once you've also covered file/shell/
git tools in depth. What's here now is the reference implementation
itself: read it, run it, and get comfortable with it before Chapter 8
and before pairing with an AI assistant on `ai-paired.html`.

## Files

- **`starter.py`** — the exact minimal agent built across the lesson:
  a system prompt, three tools (`read_file`, `write_file`,
  `run_shell_command`), and the plan/act/observe/repeat loop with a step
  cap. This is the reference implementation, not something with blanks
  to fill in.
- **`solution.py`** — `starter.py` plus one addition: a fourth tool,
  `list_files`, in the shape an AI coding assistant might hand back if
  you asked it to add one. It runs, but it has three deliberate, findable
  flaws — see `ai-paired.html` for the guided critique using Chapter 3's
  five-question checklist, or the top of `solution.py`'s own docstring
  for a spoiler-tagged answer key.

## How to run

Both files need a local Ollama server with a tool-calling-capable model
pulled.

```bash
pip install openai
ollama pull llama3.2       # ~2GB download, see the lesson for hardware notes
ollama serve                # if it isn't already running
python3 starter.py
python3 solution.py
```

If Ollama isn't running, both scripts detect the connection failure,
print a clear message explaining what to install/start, and exit 0
instead of crashing — this is intentional so the files never fail CI or
a fresh clone with nothing set up yet.

Each run creates a small `workspace/` directory next to the script and
has the agent write and read/list a file inside it — safe to delete
between runs (`rm -rf workspace`).

## What's next

Once Chapter 8 covers file/shell/git tools in real depth, the Level 2
project unlocks: you'll extend this same reference agent with a new
tool of your own, from a partial scaffold, with your own diff to review
against Chapter 3's checklist — not someone else's.
