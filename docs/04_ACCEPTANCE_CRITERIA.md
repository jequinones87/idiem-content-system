# 04 — Acceptance criteria

## Library integrity

The implementation must reproduce:

- total relations: 292
- assigned to cells: 137
- technical source relations: 102
- auxiliary relations: 35
- reserve: 150
- excluded: 5
- active knowledge items: 116
- source documents: 29

Expected cell knowledge item counts:
- Infra Pública Resiliente: 24
- Hospitalaria y Asistencial: 6
- Infra Crítica Transporte: 0
- Infra Operación Minera: 65
- Lab Minero Digital: 21

## Mandatory policy tests

### Test A — Transporte
Request a technical post for Infra Crítica Transporte using only current library.

Expected:
- no technical draft;
- status `CONTENT_GAP`;
- reason: no active technical knowledge items specific to Metro/EFE.

### Test B — Modelamiento preventivo
Any retrieved item carrying `NAME_ONLY_DO_NOT_EXPAND`.

Expected:
- may be named;
- must not invent definition, method, deliverable or equivalence.

### Test C — Triaxial
Use technical core.

Expected:
- laboratory/testing description allowed when supported;
- world ranking, exclusivity or superlatives blocked.

### Test D — Mining boundary
Request Lab Minero Digital content around BIM/asset monitoring.

Expected:
- do not classify as Lab merely because it is digital;
- return Operación Minera knowledge when the service is integrity/engineering/continuity and the requested cell permits it;
- never leak it into a Lab brief.

### Test E — excluded evidence
Request content based on an excluded relation.

Expected:
- hard block.

### Test F — source traceability
Every concrete IDIEM factual statement in a generated brief must expose supporting IDs.

## Definition of done for handoff implementation

A local run can:
1. load all canonical data;
2. pass integrity checks;
3. retrieve by cell/topic;
4. create a policy-compliant fact sheet;
5. create a schema-valid brief;
6. create a monthly plan with gaps instead of inventions;
7. export machine-readable output for later visual/design steps.
