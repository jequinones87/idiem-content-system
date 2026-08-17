# CLAUDE.md — IDIEM Content System

## Mission

Build a deterministic, auditable content-planning and drafting system for IDIEM LinkedIn using the supplied 2A.2 knowledge package.

## Non-negotiable rules

1. The supplied IDIEM library is the factual source of truth.
2. Do not use general model knowledge to fill factual gaps about IDIEM services, projects, clients, methods, results, accreditations, rankings, legal mechanisms or current capabilities.
3. Every concrete IDIEM claim in a brief/draft must trace to:
   - one or more `knowledge_id`, or
   - an allowed `auxiliary_id`.
4. Always enforce `generation_policy` and `usage_instruction`.
5. `NAME_ONLY_DO_NOT_EXPAND` means exactly that: the term may be named, not explained.
6. `USE_TECHNICAL_CORE_BLOCK_CLAIMS` allows the technical core but blocks the attached rankings/superlatives/claims.
7. Never turn auxiliary evidence into a technical capability.
8. Never use excluded relations as evidence.
9. Never move knowledge across cells merely to satisfy a content quota.
10. When evidence is insufficient, return `CONTENT_GAP` or `EXPERT_INPUT_REQUIRED`.
11. Keep cell rules external/configurable. The team is validating definitions in parallel, so future cell adjustments must not require code rewrites.
12. Do not implement publishing or design automation in the first milestone.
13. Preserve auditability: never mutate canonical source files in `data/`.

## Cell rules that must be enforced

- `INFRA HOSPITALARIA Y ASISTENCIAL` takes priority over Infra Pública when the project is health infrastructure.
- `INFRA CRÍTICA TRANSPORTE` is restricted to Metro/EFE. The current library has zero active technical knowledge items for this cell; treat technical content as `CONTENT_GAP`.
- In mining, client type does not determine the cell.
  - integrity / diagnosis / engineering / reliability / continuity -> `INFRA OPERACIÓN MINERA`
  - laboratory / testing / inspection / technical control / evidence -> `LAB MINERO DIGITAL`
- “Digital” does not determine Lab Minero Digital.
- Triaxial Gigante is treated as mining-related per explicit 2A.2 decision.

## Required output sequence for every content item

1. select cell
2. retrieve evidence
3. enforce policies
4. create fact sheet
5. choose editorial angle
6. build structured brief
7. run factual QA
8. draft copy
9. run editorial QA
10. leave status as `DRAFT` until human approval

## Engineering expectations

- Prefer simple, explicit data transformations.
- Add tests for policy enforcement and coverage.
- Fail closed, not open.
- Use schemas for structured outputs.
- Log reasons for every blocked or gap state.
- Do not duplicate the knowledge base into prompt text when structured retrieval is available.
- Keep future visual/assets integration behind an interface.
