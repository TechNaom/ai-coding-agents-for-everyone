# AI Coding Agents for Everyone Templates

These templates define the standard chapter flow. Use them for every new
chapter so the course stays consistent and fast to build.

The reference is `python-for-everyone` for structure and UI pattern only. The
content must always be original to RAG, GenAI systems, prompt testing,
retrieval, evaluation, and production AI engineering.

## Standard Chapter Flow

1. `lesson.html`
2. `quiz.html`
3. `exercises/index.html`
4. `practice/index.html`
5. `interview-questions.html`
6. `project/index.html`

Supporting source files:

- `README.md`
- `thinking-journal.md`
- `interview-questions.md`
- `exercises/README.md`
- `exercises/starter.py`
- `exercises/solution.py`
- `practice/README.md`
- `practice/starter.py`
- `practice/solution.py`
- `project/README.md`
- `project/starter.py`
- `project/solution.py`
- `diagrams/architecture.txt`
- `diagrams/architecture.mmd`
- `diagrams/architecture.svg`

## How To Use

1. Copy the relevant template into a new chapter folder.
2. Replace placeholders like `{{CHAPTER_ID}}`, `{{CHAPTER_TITLE}}`, and
   `{{CHAPTER_SLUG}}`.
3. Keep the navigation flow unchanged unless there is a strong reason.
4. Add original RAG/GenAI content.
5. Stop after the chapter is complete and wait for review before building the
   next chapter.

## Required Page Pattern

Every learner-facing page should have:

- Sidebar navigation.
- Top navigation.
- Back link to previous step.
- Page metadata.
- Conversational opening.
- Clear next-step chapter navigation.
- Footer.

## Content Experience Pattern

Each topic should feel like a guided mentor conversation, not documentation.
Use this structure when building lessons, exercises, practice banks, and
interview preparation:

1. Title.
2. Why this topic matters.
3. Simple explanation.
4. Real-life analogy.
5. Technical explanation.
6. Architecture view.
7. Code or practical example.
8. Production considerations.
9. Common mistakes.
10. Interview questions.
11. Mini assignment.
12. Summary.

Keep the surface simple and the engineering depth strong. The learner should be
able to read comfortably, but a senior engineer should still see production
judgment, trade-offs, evaluation thinking, and failure-mode awareness.

## Exercise and Interview Minimums

- Exercises: at least 8 tasks per chapter.
- Practice bank: at least 10 real scenarios per chapter.
- Interview questions: at least 15 per chapter.
- Each interview question should include strong answer, red flag, follow-up, and
  what the question proves.
- At least 5 exercises or scenarios must be production-gear problems involving
  risk, access, evaluation, latency, cost, compliance, operations, or rollout.

## Relative Paths

For files directly under a chapter folder:

- CSS/assets root: `../../assets/...`
- Course root: `../../index.html`

For files inside nested folders such as `exercises/`, `practice/`, and
`project/`:

- CSS/assets root: `../../../assets/...`
- Course root: `../../../index.html`
