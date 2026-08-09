# Chapter 7 Interview Questions: Build: A Minimal Coding Agent

These mirror `interview-questions.html` exactly. Grouped by level. Each
includes a strong answer, a red flag, and a natural follow-up an
interviewer might ask next.

---

### 1. (Beginner) What are the three pieces you need to build even the most minimal working coding agent?

**Strong answer:** A system prompt describing the agent's rules and
available tools in plain language, a set of real tools (each a schema
the model sees plus an actual function that runs), and a loop that
calls the model, checks for tool calls, dispatches them to real
functions, appends the results back into the conversation, and repeats
until a clean stop or a step cap.

**Red flags:** Describes "the agent" as a single black-box call to a
model, without separating the tool layer (real functions with real side
effects) from the loop (the control flow deciding when to call the
model again).

**Follow-up:** "Which of those three pieces actually executes a file
write or shell command — the model, or something else?"

---

### 2. (Beginner) In this chapter's agent, what's the difference between a tool's schema and a tool's function?

**Strong answer:** The schema (in the `TOOLS` list) is a name,
description, and argument shape shown to the model so it knows the tool
exists and how to call it — it's plain data, not code. The function
(like `read_file`) is the real Python code that actually runs when the
harness dispatches a tool call, with real side effects like opening a
file on disk.

**Red flags:** Treats the schema as if it "runs" something, or can't
explain why a tool needs both a description in the schema and a
separate implementation.

**Follow-up:** "If you changed a tool's description in the schema but
not its underlying function, what would break, and what wouldn't?"

---

### 3. (Intermediate) Walk through what happens, mechanically, from the moment `run_agent` gets a tool call back from the model to the moment the model sees the result.

**Strong answer:** The raw response message (including its
`tool_calls`) is appended to `messages`. For each tool call,
`dispatch_tool_call` parses its JSON arguments, looks up the matching
Python function, and calls it, catching any JSON or missing-argument
errors along the way. Whatever string comes back — a real result or a
descriptive error — gets appended as a new message with `role: "tool"`
and the matching `tool_call_id`. The next call to
`chat.completions.create` re-sends the entire conversation, including
that new tool message, and the model reads it fresh.

**Red flags:** Skips the JSON-parsing and dispatch step, or thinks the
model "sees" the function execute rather than reading a text message
about its result on the next call.

**Follow-up:** "Why does the tool message need a matching
`tool_call_id` instead of just being appended as plain text?"

---

### 4. (Intermediate) Why does `dispatch_tool_call` catch both `json.JSONDecodeError` and `KeyError` separately, instead of one broad `except Exception` around everything?

**Strong answer:** They're different, genuinely observed failure modes
with different causes: `JSONDecodeError` means the model's
`tool_calls[i].function.arguments` string wasn't even valid JSON;
`KeyError` means the JSON parsed fine but a required argument the
schema demanded was missing. Both were worth naming explicitly because
this chapter directly observed a small local model produce incomplete
tool-call arguments during real testing — not a hypothetical. A single
broad catch-all would still prevent a crash, but naming the specific
failure gives the model (and a human debugging the transcript) a much
clearer signal about what actually went wrong.

**Red flags:** Says the separate catches don't matter because "it all
gets caught anyway," missing that the specific error message returned
to the model is itself useful, actionable information for its next
turn.

**Follow-up:** "What would the agent's next turn probably look like if
it got back a generic 'something went wrong' instead of 'missing
required argument path'?"

---

### 5. (Senior) A teammate wants to swap this chapter's agent from Ollama to a hosted provider "for better reliability" but is worried it'll require rewriting the tool layer. How do you respond?

**Strong answer:** It shouldn't, and if it does, that's worth
investigating rather than accepting as necessary. Because the agent is
built against the plain `openai` client's request/response shape — not
anything Ollama-specific — swapping to OpenAI, Anthropic's
OpenAI-compatible endpoint, or Gemini's OpenAI-compatible endpoint is a
three-line change: `base_url`, `api_key`, and `model`. `TOOLS`, every
tool function, `dispatch_tool_call`, and the loop itself are
provider-agnostic by construction. If a teammate's swap needs more than
that, the tool layer probably has an Ollama-specific assumption baked
in somewhere worth finding and removing.

**Red flags:** Assumes switching providers always requires a new SDK or
a meaningfully different code path, without knowing about the shared
OpenAI-compatible shape this chapter's design leans on deliberately.

**Follow-up:** "What's one thing that actually might behave differently
after that swap, even though the code doesn't change?" (Acceptable
answers: cost per call, rate limits, subtle differences in how
reliably the new model fills tool-call arguments, or provider-specific
compatibility caveats like Anthropic's documented limitations on this
layer.)

---

### 6. (Senior) The `list_files` tool added in this chapter's `project/solution.py` doesn't call `_safe_path()` the way the other three tools do. Why is that a real problem, and how would you catch it in review?

**Strong answer:** Every other tool in the file confines its path
argument to the workspace directory via `_safe_path()`, which is a
harness-enforced boundary, not a model-trusted instruction.
`list_files` calling `os.listdir(path)` directly means a call with a
path like `"../../etc"` or an absolute path silently returns real
contents from outside the intended workspace — no crash, no obvious
error, just a boundary quietly not being enforced for one specific
tool. Chapter 3's review checklist catches this under "did it touch
anything outside the stated boundary" and "is it consistent with the
rest of the codebase's patterns" — reading the diff for what it does
differently from the established pattern nearby, not just whether it
runs.

**Red flags:** Says it's fine because "it still works" or because
nothing crashes when they mentally run it, without checking whether
the new code follows the same safety pattern as the code right next to
it.

**Follow-up:** "What kind of test would catch this bug automatically,
versus what only a manual code review would catch?"

---

### 7. (Architect) You're deciding whether a new internal tool (say, a CI-troubleshooting agent) should be built with a hand-rolled loop like this chapter's, or with a heavier agent framework. What factors would actually drive that decision?

**Strong answer:** The loop's control flow itself is genuinely small
(well under 50 lines here) and rarely the source of real engineering
cost — the real cost is in the tool layer (how many tools, how
carefully they're scoped and sandboxed) and in operational concerns a
framework might actually help with: retries, observability/tracing
across many concurrent agent runs, structured logging of tool calls
for audit, or built-in support for more complex planning strategies
than plan-per-turn. A hand-rolled loop is the right call when the
toolset is small and the team wants to understand and control every
line (this course's own reason for teaching it this way); a framework
earns its complexity when the operational surface — many tools, many
concurrent runs, compliance/audit requirements — genuinely outgrows
what a team wants to maintain by hand.

**Red flags:** Treats "framework vs. hand-rolled" as purely a matter of
taste or team seniority, without naming concrete operational factors
(observability, retries, audit, concurrency) that actually
differentiate the two options.

**Follow-up:** "What's the first operational problem you'd expect to
hit with a hand-rolled loop like this one at ten times the usage?"

---

### 8. (Architect) How would you explain to a security-conscious stakeholder why this chapter's `_safe_path` function matters more than the system prompt's instruction that "paths are relative to the workspace"?

**Strong answer:** The system prompt is a request made to the model,
evaluated the same probabilistic way every other prediction is —
nothing guarantees the model always honors it, especially under an
adversarial or malformed input, or simply an off turn from a smaller
model (Section 6's reliability caveat generalizes here too).
`_safe_path` is a check the harness runs on every single tool call
regardless of what the model asked for or claimed — a path that tries
to escape the workspace is rejected by code, not by hoping the model
behaved. The security posture of an agent should be evaluated by what
the harness enforces unconditionally, not by what its prompt asks
nicely for — this is exactly the distinction Module 5 (Chapters 11-12)
builds a full security and CI-integration treatment around.

**Red flags:** Treats the system prompt's instruction and the
code-level check as roughly equivalent safeguards, or can't articulate
why a probabilistic model output is a weaker guarantee than a
deterministic code check.

**Follow-up:** "If you had to remove one of the two — the prompt
instruction or the code-level check — which would you keep, and why?"

## Strategy Tips

- If you're asked to whiteboard the loop, draw the three pieces
  separately (system prompt/tools, the loop's control flow, the tool
  functions) before writing any code — interviewers are usually
  checking whether you understand the mechanism, not whether you
  remember exact syntax.
- If you get a question wrong, walk through what a real, concrete
  failure looked like (the missing-key tool-call argument this chapter
  actually observed) rather than answering in the abstract — concrete
  examples recover a lot of partial credit.
