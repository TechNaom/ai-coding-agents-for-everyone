/*
  Single source of truth for the AI Coding Agents for Everyone chapter
  roster. Mirrors the mcp-for-everyone pattern: sidebar.js and home.js
  render navigation from this file. A chapter is "live" iff it has a
  `path` -- omit `path` for chapters that don't exist yet, do not set a
  placeholder path, or sidebar/home will link to a 404. The same rule
  applies to a module's `examPath`: set it to null until that module's
  written exam actually exists in assessments/written-exams/.
  No chapters have content yet -- see PROJECT_STATE.md.
*/

window.ACAFE_MODULES = [
  {
    title: "Module 1 — Using Coding Agents Well",
    summary: "The daily-practice layer: prompting, scoping, and reviewing before any internals.",
    examPath: null,
    chapters: [
      {
        id: "chapter-01",
        num: 1,
        title: "Why Coding Agents Aren't Just Autocomplete",
        description: "What actually changed, and why it matters for how you work.",
        path: "chapters/chapter-01-why-coding-agents-arent-just-autocomplete/lesson.html"
      },
      {
        id: "chapter-02",
        num: 2,
        title: "Prompting and Scoping Tasks for an Agent",
        description: "Framing a task so an agent can actually succeed at it.",
        path: "chapters/chapter-02-prompting-and-scoping-tasks-for-an-agent/lesson.html"
      },
      {
        id: "chapter-03",
        num: 3,
        title: "Reading and Reviewing an Agent's Diff Like a Senior Engineer",
        description: "The review habits that catch what a quick glance misses.",
        path: "chapters/chapter-03-reading-and-reviewing-an-agents-diff-like-a-senior-engineer/lesson.html"
      }
    ]
  },
  {
    title: "Module 2 — How Coding Agents Actually Work",
    summary: "Open the hood on the agentic loop.",
    examPath: null,
    chapters: [
      {
        id: "chapter-04",
        num: 4,
        title: "The Agentic Loop: Plan, Act, Observe, Repeat",
        description: "The mental model behind every coding agent's behavior.",
        path: "chapters/chapter-04-the-agentic-loop-plan-act-observe-repeat/lesson.html"
      },
      {
        id: "chapter-05",
        num: 5,
        title: "Why Agents Loop, Stall, or Go Off the Rails",
        description: "Diagnosing the most common agent failure modes.",
        path: "chapters/chapter-05-why-agents-loop-stall-or-go-off-the-rails/lesson.html"
      },
      {
        id: "chapter-06",
        num: 6,
        title: "Context Windows and Codebase-Scale Understanding",
        description: "Why an agent 'forgets' things, and how to work with that."
      }
    ]
  },
  {
    title: "Module 3 — Building a Coding Agent",
    summary: "Hands-on construction with the Claude Agent SDK.",
    examPath: null,
    chapters: [
      {
        id: "chapter-07",
        num: 7,
        title: "Build: A Minimal Coding Agent",
        description: "A real, working agent using the Claude Agent SDK, tested end to end."
      },
      {
        id: "chapter-08",
        num: 8,
        title: "Giving Your Agent File/Shell/Git Tools",
        description: "Extending the minimal agent with real tool access."
      },
      {
        id: "chapter-09",
        num: 9,
        title: "Connecting Your Agent to MCP Servers",
        description: "Swapping hand-rolled tools for MCP-based ones."
      }
    ]
  },
  {
    title: "Module 4 — Reviewing AI-Generated Code Critically",
    summary: "The human half of \"AI proposes, human reviews.\"",
    examPath: null,
    chapters: [
      {
        id: "chapter-10",
        num: 10,
        title: "Detecting Hallucinated APIs and Logical Bugs",
        description: "Building the habit of validating before trusting."
      }
    ]
  },
  {
    title: "Module 5 — Production & Safety",
    summary: "What changes when an agent operates on a live codebase and in CI.",
    examPath: null,
    chapters: [
      {
        id: "chapter-11",
        num: 11,
        title: "Security: Sandboxing, Permissions, Destructive Commands",
        description: "Containing what an agent can actually do to your codebase."
      },
      {
        id: "chapter-12",
        num: 12,
        title: "Putting an Agent in CI",
        description: "PR review bots and CI troubleshooting agents, done safely."
      }
    ]
  },
  {
    title: "Module 6 — Capstone",
    summary: "Architect-level synthesis.",
    examPath: null,
    chapters: [
      {
        id: "chapter-13",
        num: 13,
        title: "Capstone: Design an Agent Workflow for a Real Team",
        description: "A Level 4 architecture challenge closing the course."
      }
    ]
  }
];
