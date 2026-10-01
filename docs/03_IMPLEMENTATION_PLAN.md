# 03 — Implementation plan

## Milestone 0 — Repository bootstrap

- inspect environment/repository;
- choose a simple stack appropriate to the existing repo;
- create config, schema and test structure;
- add a CLI or minimal local interface only if useful;
- do not build publishing/design integrations.

Deliverable: project can load and validate the supplied package.

## Milestone 1 — Knowledge loader and validation

Implement:
- JSON/CSV loading;
- schema validation;
- uniqueness checks;
- source coverage checks;
- relation partition checks;
- policy enum validation;
- cell definition loading.

Acceptance:
- reproduces the known closure totals;
- fails on missing/duplicate IDs or invalid policy.

## Milestone 2 — Retrieval layer

Filters:
- cell
- service
- capability
- application
- policy
- document
- relation
- keyword over retrieval key/evidence

Must return:
- knowledge item;
- source traceability;
- policy;
- compatible auxiliary evidence.

No LLM is required for deterministic filtering.

## Milestone 3 — Fact sheet engine

Input:
- cell;
- optional topic/goal/audience.

Output:
- selected knowledge IDs;
- allowed facts;
- mandatory caveats;
- blocked claims;
- content gaps;
- source relations/docs.

The fact sheet must be generated before copy.

## Milestone 4 — Brief generator

Produce output matching `schemas/content_brief.schema.json`.

Enforce:
- same-cell evidence;
- content type;
- approval state;
- visual brief contract;
- QA fields.

## Milestone 5 — Monthly planner

Produce a configurable monthly grid.

Inputs:
- month;
- target post count;
- cadence;
- cell weights;
- optional campaign priorities;
- recent content history.

Constraints:
- do not exceed factual coverage;
- avoid consecutive reuse of same main knowledge ID;
- vary angle/application where possible;
- emit `CONTENT_GAP` when a target cell cannot be safely populated;
- do not silently rebalance unless configuration allows it.

## Milestone 6 — Drafting adapter

Only after the structured brief is factual and policy-compliant:
- generate hook/body/CTA;
- never add IDIEM facts not in the fact sheet;
- keep status `DRAFT`;
- retain traceability.

## Milestone 7 — Visual interface placeholder

Implement types/interfaces only:
- requested format;
- main visual message;
- supporting points;
- evidence to visualize;
- desired image metadata query.

Do not select actual images yet.

## Milestone 8 — Tests and export

Tests must cover:
- blocked claims;
- `NAME_ONLY_DO_NOT_EXPAND`;
- Transporte content gap;
- cross-cell leakage;
- excluded relations;
- Lab vs Operación Minera rules;
- brief schema;
- monthly repetition controls.

Exports:
- JSON brief;
- JSON monthly plan;
- optional CSV grid for human review.

## Later milestones — not part of this handoff

- Design System ingestion.
- Image library catalog and matching.
- Design/template rendering.
- Metricool integration.
- n8n orchestration.
- Publishing.
