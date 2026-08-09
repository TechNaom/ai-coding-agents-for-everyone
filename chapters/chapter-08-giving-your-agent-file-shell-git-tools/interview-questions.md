# Chapter 8 Interview Questions: Giving Your Agent File/Shell/Git Tools

These mirror `interview-questions.html` exactly. Grouped by level. Each
includes a strong answer, a red flag, and a natural follow-up an
interviewer might ask next.

---

### 1. (Beginner) What's the real difference between `write_file` and `edit_file`, and when would you use each?

**Strong answer:** `write_file` replaces a file's entire contents; it's
the right tool for a brand-new file or a genuine full rewrite.
`edit_file` replaces one exact, unambiguous occurrence of text inside
an existing file, leaving everything else untouched — the right tool
when only part of a file needs to change, because it doesn't ask the
model to correctly reproduce content it isn't actually changing.

**Red flags:** Says one tool is simply "better" than the other, without
naming the actual trade-off (overwrite risk vs. a new class of
ambiguous-match failure) or a concrete scenario where each is the right
call.

**Follow-up:** "What does edit_file do if the text you're searching for
appears three times in the file?"

---

### 2. (Beginner) Why does `list_directory` need to distinguish "no such directory" from "that path is a file, not a directory," instead of just one generic error?

**Strong answer:** They're different, genuinely actionable situations
for the model's next turn: "no such directory" means the path is wrong
and the model should try a different one or ask; "not a directory"
means the path exists but the model chose the wrong tool for it (it
should call `read_file` instead). One generic error message collapses
two different next actions into one, forcing the model to guess which
correction actually applies.

**Red flags:** Treats both as "just an error" with no difference in
what the model should do next, or thinks the distinction is only about
cleaner logging.

**Follow-up:** "How does this connect to Chapter 4's point about vague
tool descriptions producing wrong tool calls?"

---

### 3. (Intermediate) `git_status` and `git_diff` call `subprocess.run` with a Python list of arguments, while `run_shell_command` still uses `shell=True` with a raw string. Why the difference, and could `run_shell_command` be rewritten the same safer way?

**Strong answer:** A list of arguments to `subprocess.run` is never
passed through a shell interpreter, so shell metacharacters like `;`,
`&&`, or backticks in an argument can't be used to inject a second
command — that's why `git_status`/`git_diff` are structurally safer by
construction. `run_shell_command` can't be rewritten the same way
without losing its entire point: its whole job is to run an arbitrary
command string the model composes itself (pipes, redirects, chained
commands), which fundamentally requires shell interpretation. That's
exactly why it needs a different mitigation (the denylist) instead of
just "also use a list."

**Red flags:** Suggests switching `run_shell_command` to a list of
arguments as a simple fix, without recognizing that would remove the
tool's actual purpose (running arbitrary shell syntax, not one fixed
command).

**Follow-up:** "If a task only ever needed to run one of five known
commands, would you build it as run_shell_command or something more
restricted?"

---

### 4. (Intermediate) A teammate adds `SHELL_DENYLIST` and says "great, now run_shell_command is safe." How do you respond?

**Strong answer:** Not fully, and saying so isn't pedantry — it changes
what you tell a stakeholder about actual risk. The denylist
meaningfully reduces the chance that an off-course or confused model
call does something obviously destructive by accident (the realistic
day-to-day risk for a coding agent you're directing yourself), but it
can only block patterns someone thought to write ahead of time — a
differently-phrased equivalent command, string concatenation, or a
project-specific destructive command (like `git clean -fdx` wiping
wanted untracked files) can still get through. It's a real, honest
mitigation, not solved security; real isolation is a
sandboxing/permissions problem, covered later in this course.

**Red flags:** Agrees it's "safe" without qualification, or can't name
a concrete way the denylist could still be bypassed.

**Follow-up:** "What would you add on top of the denylist if this agent
were about to run against a real, non-throwaway codebase?"

---

### 5. (Senior) Design review: a colleague wants to add a `git_commit` tool with a `confirm: bool` argument, arguing that's sufficient guardrail. What's your assessment?

**Strong answer:** It's not sufficient on its own, and the reason
generalizes past this one tool: a flag the model itself supplies as
part of its own tool call isn't a real guardrail, because nothing stops
the model from simply setting `confirm=true` every time — it's the
same category of mistake as trusting a system-prompt instruction over a
harness-enforced check (Chapter 7's `_safe_path` lesson, applied to a
write-capable git tool instead of a file path). A real guardrail needs
something outside the model's own turn: a human confirmation step the
harness pauses for, a permission scope set before the agent runs at
all, or simply not exposing commit/push as a tool and having a human
run them after reviewing the diff.

**Red flags:** Accepts a model-settable flag as adequate protection, or
doesn't distinguish "the model can decide this" from "the harness
enforces this regardless of what the model decides."

**Follow-up:** "What would an actually-safe version of a confirmation
step look like, mechanically?"

---

### 6. (Senior) Someone argues the agent should just always use `write_file` for every change, since `edit_file` adds complexity for what's "just a simpler case." How do you push back, concretely?

**Strong answer:** On a small file for a small change, `write_file`-only
might genuinely be fine. The concrete failure it invites is on larger
files: the model has to correctly reproduce every unchanged line to use
`write_file` safely, and a wrong reproduction — a dropped comment, a
subtly reformatted block, a truncated section — produces a diff that
silently touches far more than intended, with no error at all; the
tool call "succeeds." `edit_file` converts that into a much smaller,
more reviewable diff and fails loudly (a clear "text not found" or
"ambiguous match" error) exactly in the situations where `write_file`
would otherwise fail silently. The "added complexity" is real, but it's
complexity that turns a silent, hard-to-review failure mode into a
loud, recoverable one — a trade worth making past a certain file size
or change granularity.

**Red flags:** Argues purely from "fewer tools is simpler" without
engaging with the specific silent-failure risk write_file-only creates
on larger files.

**Follow-up:** "At what point — file size, kind of task — would you say
the trade-off tips toward needing edit_file?"

---

### 7. (Architect) You're scoping tool access for three different internal agents: one that only reads code for documentation generation, one that edits code in a scratch branch, and one that's allowed to run CI locally. How would tool selection differ across the three, and why?

**Strong answer:** The documentation agent should get read-only tools
only — `read_file`, `list_directory`, maybe `git_diff` for context —
and explicitly no `write_file`/`edit_file`/`run_shell_command` at all,
because its job never requires state changes and the safest tool is
one that structurally cannot cause the harm you're worried about, not
one that's merely discouraged from it. The scratch-branch editor needs
`write_file`/`edit_file` and probably `git_status`/`git_diff` to
self-check, but still shouldn't get `git_commit` or `git push`
unscoped — the "scratch branch" framing reduces blast radius but
doesn't eliminate the review-bypass problem discussed in this chapter.
The CI-runner agent needs `run_shell_command` but scoped much more
tightly than this chapter's general denylist — realistically an
allowlist of the specific CI commands it's meant to run, since its
command surface is known and narrow, which is exactly the situation
where an allowlist's restrictiveness stops being a real cost.

**Red flags:** Gives all three agents the same toolset "to keep things
simple," or can't articulate why the CI-runner's narrower, more
predictable task makes an allowlist the right call there specifically,
even though a denylist was the right call for this chapter's
general-purpose agent.

**Follow-up:** "Which of these three would you be most comfortable
running fully autonomously, unsupervised, and why?"

---

### 8. (Architect) How would you explain to a non-technical stakeholder why "the agent has more tools now" is not, by itself, either good or bad news?

**Strong answer:** Every tool this chapter added changed the honest
risk profile in a different, specific direction — `git_status`/`git_diff`
are read-only and net-positive for safety (they let the agent and a
human verify its own work); `edit_file` reduces one specific
silent-failure risk while adding a different, loud one; the hardened
`run_shell_command` is meaningfully less risky than Chapter 7's version
but still not "safe" in any complete sense. "More tools" tells you
nothing about direction until you ask, tool by tool: is this read or
write, what's the worst-case bad call, and is that worst case
loud/recoverable or silent/permanent? The stakeholder-facing answer
isn't "we added capability" or "we added risk" — it's a specific
accounting of both, tool by tool, the same discipline this chapter's
own "GenAI Builder Thought Process" section names directly.

**Red flags:** Answers only in terms of total capability ("the agent
can now do more") without breaking down the actual safety direction of
each individual addition.

**Follow-up:** "If you had to cut this chapter's toolset down to just
two tools for a first production rollout, which two, and why those?"

## Strategy Tips

- If you're asked to design a new tool live, narrate the same four
  checks this chapter's tools all pass: does it route paths through
  `_safe_path()` (or the equivalent boundary for a non-file resource),
  what's the worst-case bad call, is that failure loud and recoverable
  or silent and permanent, and does its description clearly
  distinguish it from every other tool nearby.
- If asked about "AI agent security" broadly, resist answering as if
  one mitigation (a denylist, a confirm flag, a sandboxing layer) fully
  solves it — naming what a given mitigation actually covers, and what
  it explicitly doesn't, reads as far more senior than claiming
  something is "safe" without qualification.
