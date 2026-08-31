# 07 — First run prompt for Claude Code

Use this as the first instruction after opening the handoff directory:

---

Read `CLAUDE.md` and the documentation under `docs/` in numeric order.

Then inspect the canonical files under `data/`.

Do not write production code immediately. First:

1. summarize the architecture and source-of-truth hierarchy;
2. verify the library counts against `docs/04_ACCEPTANCE_CRITERIA.md`;
3. identify the existing repository/runtime constraints;
4. propose a concrete implementation plan for Milestones 0–4;
5. list any genuine blockers.

Do not reinterpret IDIEM facts, do not use outside knowledge to fill gaps, and do not modify files under `data/`.

After the plan, implement Milestones 0–4 with automated tests. Keep the design/assets and publishing layers as interfaces/placeholders only.

The first working demo must:
- retrieve technical knowledge by cell;
- return a `CONTENT_GAP` for a technical Transporte request;
- generate a structured fact sheet;
- generate one schema-valid `DRAFT` content brief with full evidence traceability.

---
