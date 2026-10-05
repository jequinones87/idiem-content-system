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

## Editorial memory (aprendizajes del equipo)

Antes de escribir o corregir cualquier copy/pieza, lee `docs/09_EDITORIAL_MEMORY.md`.
Ahí se acumulan las correcciones de tono, estilo y hechos que el equipo valida; son de
aplicación obligatoria en posts futuros. Reglas factuales críticas ya fijadas:

- **Green Hospital es certificación PROPIA de IDIEM.** NO mencionar a "Salud sin Daño".
  Se complementa con ISO 50001.
- **Soldaduras (END):** la soldadura se **inspecciona** (por muestreo, según plan de
  inspección), no "cada soldadura verificada". Se **califica al soldador** y al
  procedimiento, NO la soldadura.
- **Acústica:** norma D.S. 38/2011 MMA (futuro D.D. 14/24).
- **Voz de marca:** técnica, institucional, sobria, comprensible para no especialistas; sin
  superlativos. La secuencia gancho → problema → "En #IDIEM…" → ✅ → CTA es **un** arquetipo,
  no la plantilla por defecto (ver sección siguiente).
- **Saludos institucionales** (Fiestas Patrias, etc.) NO trazan a knowledge_id: mensaje
  general, sin proyectos/fechas/cifras no respaldadas por 2A.2.
- **Efemérides del sector:** al armar la grilla de CADA mes, revisa `config/efemerides.json`
  y suma la pieza conmemorativa si el mes cae en una fecha clave (adicional a los 12 posts,
  como el saludo de Fiestas Patrias). Las que tienen respaldo técnico en 2A.2 (arquitectura,
  geología, suelos, integridad estructural) pueden trazar a knowledge_id; **Transporte
  Sostenible (26-nov) NO** — la célula INFRA CRÍTICA TRANSPORTE es CONTENT_GAP, así que va
  como institucional general sin afirmar capacidades técnicas.

## Diversidad editorial y control de sesgos (OBLIGATORIO desde noviembre 2026)

Fuente: `docs/10_ESTRATEGIA_EDITORIAL_Y_SESGOS.md` + `config/editorial_diversity.json`
(mandan sobre `config/editorial_style.*` y sobre la memoria editorial). Origen: auditoría
de sept 2026 — octubre tuvo CTA `contact` en 9/12 posts y ~4 arquetipos.

- La unidad de diversidad **no es el tema**: es tema + argumento + pain point + claim +
  **arquetipo** + **hook_type** + **cta_type** + estructura. Pregunta obligatoria:
  *"¿ya contamos algo parecido de esta misma manera?"*.
- **La diversidad se decide ANTES de redactar.** Para cada grilla mensual, primero armar y
  mostrar a MKT la **tabla de asignación** (por post: arquetipo, hook_type, cta_type, pain
  point, claim) respetando los límites de `editorial_diversity.json`; después redactar con
  esas asignaciones como restricción. QA es la última barrera, no el mecanismo principal.
- 6–8 arquetipos por mes; no repetir arquetipo/hook_type/cta_type en posts consecutivos.
- **CTA por intención**; `contact` **no** es default; no repetir textual un CTA reciente.
- **Hook ≠ pain point**: registrarlos por separado.
- Narrativa desde la necesidad del cliente; valor técnico antes que lo comercial.
- **Longitud única: ≤ 900 caracteres (objetivo 820–880), máx. 1–2 emojis por párrafo.**
  Excepción: posts de evento (webinars) llevan URL y quedan exentos del tope (ref. 1300).
- Límites de diversidad de `editorial_diversity.json`: **aprobados por MKT** (30-09-2026).
- Datos de fuentes: jerarquía células → reglas editoriales → brochures → Sales
  Intelligence → casos; clasificar `SAFE` / `VERIFY` / `INTERNAL` / `DO_NOT_PUBLISH`
  (`VERIFY` se valida antes; `DO_NOT_PUBLISH` nunca llega al copy).
- Memoria única = archivo mensual consolidado (no memorias paralelas).
- Octubre 2026 cerrado manualmente: **no regenerar**.
