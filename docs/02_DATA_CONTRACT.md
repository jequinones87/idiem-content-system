# 02 — Data contract

## Canonical data sources

### `04_base_produccion_IDIEM_2A2.json`
Primary runtime knowledge base.

Important top-level keys:
- `metadata`
- `cell_definitions`
- `generation_rules`
- `knowledge_items`
- `knowledge_sources`
- `auxiliary_evidence`
- `reserve_outside_prioritized_cells`
- `excluded_relations`
- `source_documents`

### `05_reglas_editoriales_generacion_IDIEM_2A2.json`
Editorial policy and workflow.

Important keys:
- `rule_layers`
- `cell_editorial_guidance`
- `content_types`
- `generation_workflow`
- `approval_states`
- `qa_checks`
- `content_brief_schema`

### `03_taxonomia_maestra_2A2.json`
Human-readable/structured taxonomy reference.

### `02_mapa_contenidos_2A2_CERRADO.csv`
Audit-level traceability. Do not use this as the first retrieval source if the production base already contains the needed knowledge.

## `knowledge_item` semantics

Each item carries:
- `knowledge_id`
- `cell`
- `service`
- optional `capability`
- optional `application`
- `generation_policy`
- `usage_instruction`
- `taxonomy_statuses`
- notes
- source relation IDs
- document IDs
- retrieval key

The content engine must never ignore the policy fields.

## Auxiliary evidence

Auxiliary evidence is supporting context, not a technical service.

Examples:
- claim
- value proposition
- credential
- coverage
- sector evidence
- contracting mechanism
- R&D prototype
- lifecycle stage

Use only when `production_policy` allows it.

## Reserve

`reserve_outside_prioritized_cells` is valid IDIEM information but inactive for the five-cell content strategy.

Do not discard it. Do not activate it without a deliberate future rule change.

## Excluded

`excluded_relations` must never be used as evidence.

## Immutability

Treat all files under `data/` as read-only canonical inputs.
Generated state belongs in a separate application data/output directory.
