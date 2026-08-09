# Maintenance Guide (Solo-Maintained Project)

This repo is maintained solely by its owner — it is **not open to
external contributions**. Issues and pull requests from outside
contributors are not reviewed or merged. If you found this repo
useful, feel free to fork it for your own use per the license
(`LICENSE` for code, `LICENSE-CONTENT` for lesson content), but please
don't open issues or PRs here.

This doc is a working reference for how content gets added or updated,
so nothing drifts from the repo's conventions as it grows.

## The non-negotiable rule: test before you write

This rule is inherited from `mcp-for-everyone`, where it caught real,
non-obvious SDK bugs repeatedly (see that repo's `PROJECT_STATE.md` for
the full list) — it applies here from day one, not just once it's
proven itself in this repo too. Every code example in every chapter
must be installed and run against the real `openai` client pointed at
a real local Ollama server with a real model pulled (or `mcp[cli]` for
the tool-connection chapter) before being written into a lesson —
never written from memory or copied from older tutorials. **Do not
relax this for any edit, however small it seems.** If you're adding or
changing a code sample:

```bash
python3 -m venv /tmp/acafe-test-env
/tmp/acafe-test-env/bin/pip install openai "mcp[cli]"
# ollama pull <model>  -- see PROJECT_STATE.md for the current
# recommended tool-calling-capable model; requires a running local
# Ollama server (https://ollama.com), no API key or account needed.
# The openai client points at it via base_url="http://localhost:11434/v1".
/tmp/acafe-test-env/bin/python your_new_example.py
```

Only write the example into the lesson once you've seen its real
output.

## Adding or updating a chapter

1. Follow the page set established in `mcp-for-everyone`'s Chapter 4
   as the template: `lesson.html`, `quiz.html`,
   `interview-questions.html`,
   `exercises/{index.html,starter.py,solution.py}`,
   `practice/index.html`, `project/{index.html,starter.py,solution.py}`.
   This course's own Chapter 7 becomes the reference chapter once
   built.
2. Test every code sample per the rule above before writing it into
   the lesson.
3. Wire the chapter into `assets/chapters-data.js` — give it a `path`
   only once its `lesson.html` actually exists (see that file's header
   comment for why a premature `path` breaks the site).
4. Update `docs/curriculum/index.html` (the styled roadmap) and the
   root `index.html`'s chapter count in `hero-stats`.
5. Write a quality audit at `quality-audits/chapter-0N-audit.md`
   following the format of existing audits.
6. Run the local checks below before pushing.

## Local checks before pushing

```bash
bash scripts/local_check.sh
```

This runs the same checks CI runs: folder structure, placeholder-text
scan, Python syntax + actual execution of every `solution.py`, JS
syntax, chapter-path validation against `chapters-data.js`, and a
secret scan. If it fails, CI will fail too — fix locally first.

## File naming convention

```
chapters/chapter-NN-kebab-slug/lesson.html
chapters/chapter-NN-kebab-slug/quiz.html
chapters/chapter-NN-kebab-slug/interview-questions.html
chapters/chapter-NN-kebab-slug/exercises/{index.html,starter.py,solution.py}
chapters/chapter-NN-kebab-slug/practice/index.html
chapters/chapter-NN-kebab-slug/project/{index.html,starter.py,solution.py}
assessments/written-exams/module-N-exam.md
quality-audits/chapter-0N-audit.md
```

- Chapter numbers are two-digit, zero-padded: `chapter-01`,
  `chapter-02`, ... `chapter-13`.
- Slugs are lowercase, hyphenated, no special characters.

## Content standards

- **No placeholder text** in anything merged to `main` — no `[insert
  X]`, no Lorem ipsum. CI blocks these. (Bare `TODO 1:`, `TODO 2:` etc.
  inside `exercises/starter.py` and `project/starter.py` are
  intentional learner tasks, not placeholders — CI does not flag
  those.)
- **No API keys or secrets** committed anywhere, ever. CI scans for
  common secret patterns.
- **Cross-chapter Python imports** must use
  `importlib.util.spec_from_file_location`, never a `sys.path.insert`
  + `import solution` trick — multiple files across chapters share the
  name `solution.py`, and the naive approach breaks depending on
  invocation method. See any `_load_chapter_4_module()`-style docstring
  for the full explanation.
- **Every file with a top-level `asyncio.run(main())`** must guard it
  with `if __name__ == "__main__":` — a bare top-level call crashes if
  the file is ever imported from inside a running event loop. This was
  a real bug found and fixed across 17 files in `mcp-for-everyone`'s
  build; apply the lesson here from the start rather than rediscovering
  it.
- **Long-running or live-server-dependent solution.py files** need a
  `# CI: LONG_RUNNING_SERVER` or `# CI: NEEDS_LIVE_SERVER=<path>`
  marker comment (see `ci.yml`'s comments) so CI knows not to treat a
  non-zero exit as a failure.
- **Chapters that call the model via Ollama** must check for a running
  local Ollama server (e.g. a connection error to `localhost:11434`)
  and skip/degrade gracefully with a clear message if it's absent,
  rather than crashing — CI runners don't have Ollama running or a
  model pulled, so this path is exercised on every CI run.
- **Every chapter needs**: a hook grounded in a real problem, tested
  code (not illustrative pseudocode), a production scenario, common
  mistakes, a builder thought-process box, 6+ exercises (3+
  production-gear), 6+ practice scenarios, 8+ interview questions
  across all 4 levels, and a project — per
  `quality-audits/chapter-audit.template.md`.
