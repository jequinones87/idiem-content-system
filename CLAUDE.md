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
- **Voz de marca:** gancho con emoji → problema → "En #IDIEM…" (solución, a veces con
  viñetas `*`) → cierre ✅ → CTA con https://idiem.cl 👉 → hashtags. Sin superlativos.
- **Largo máximo del copy: 900 caracteres** (cuerpo completo, incluidos emojis, saltos y
  hashtags). Regla dura de MKT (2026-08-31): si excede, recortar antes de aprobar.
- **Saludos institucionales** (Fiestas Patrias, etc.) NO trazan a knowledge_id: mensaje
  general, sin proyectos/fechas/cifras no respaldadas por 2A.2.
- **Efemérides del sector:** al armar la grilla de CADA mes, revisa `config/efemerides.json`
  y suma la pieza conmemorativa si el mes cae en una fecha clave (adicional a los 12 posts,
  como el saludo de Fiestas Patrias). Las que tienen respaldo técnico en 2A.2 (arquitectura,
  geología, suelos, integridad estructural) pueden trazar a knowledge_id; **Transporte
  Sostenible (26-nov) NO** — la célula INFRA CRÍTICA TRANSPORTE es CONTENT_GAP, así que va
  como institucional general sin afirmar capacidades técnicas.
- **Memoria de contenidos mensual (NO repetir):** el contenido de cada mes se archiva en
  `content/archive/AAAA-MM.json` + `.md` con `design_system/archive_month.py`. Antes de armar
  un mes nuevo: (1) **archiva el mes anterior** si aún no está; (2) **lee los archivos previos**
  y NO repitas los mismos `knowledge_id`, subtemas ni ángulos editoriales del mes anterior
  —rota células/temas—; (3) **actualiza hechos** si cambiaron respecto de lo publicado. El
  archivo del mes anterior es la fuente de contexto obligatoria para el mes nuevo.
  - **No basta con rotar el knowledge_id: evita también CLAIMS, GANCHOS y CTAs parecidos entre
    meses** (aprendizaje MKT 2026-09-04). Dos posts pueden trazar a items distintos y aun así
    "sentirse iguales" si repiten el mismo problema-solución, la misma evidencia o el mismo CTA.
    Reglas: (a) no reutilizar el mismo claim técnico que ya salió el mes anterior; (b) **variar el
    CTA** —rotar las 3 variantes de la voz de marca en vez de repetir "¿Necesitas…? Conversemos
    en idiem.cl 👉" en todos—; (c) variar el gancho (fecha/efeméride, escenario, pregunta, dato);
    (d) si 2A.2 no tiene material fresco bien documentado, es preferible **menos posts sólidos**
    o pedir insumos, antes que rellenar con versiones parecidas (fail closed).
- **Workstation — historial de cambios OBLIGATORIO** (MKT 2026-09-04): cada tarjeta de cualquier
  artefacto de workstation debe mostrar el bloque "Historial de cambios aplicados (N)" (poblar
  `APPLIED_LOG` en `gen_workstation.py`; si el log está vacío el `<details>` no se renderiza). Se
  actualiza en cada ronda aplicada y republicada.
- **Fotos siempre desde la librería de Drive de IDIEM.** Archivos > ~6 MB fallan al descargar por
  el conector (la sesión expira); pedir a MKT una versión comprimida (≤5 MB). El anillo rojo de la
  pieza estática es configurable por post (`SIDE`): moverlo al lado contrario a la cara/sujeto para
  no taparlo.
- **Sales Intelligence (capa complementaria).** Al idear/redactar, consulta también
  `knowledge/sales_intelligence/` vía `idiem.sales_intelligence` (ver `docs/10_SALES_INTELLIGENCE.md`):
  dolores, necesidades, propuestas de valor, ángulos y casos por célula/segmento. **Precedencia:**
  reglas oficiales de células > editoriales > servicios/brochures > Sales Intelligence > casos >
  fuentes externas. Es **autoridad 4/6**: NO clasifica servicios ni redefine células (la célula se
  resuelve antes con las reglas oficiales). Respeta los estados: `SAFE` alimenta copy; `VERIFY`
  requiere validación humana antes de publicar (cifras, %, fechas, proyectos, coberturas,
  certificaciones, 24/7, plazos, legal); `INTERNAL` es solo razonamiento; `DO_NOT_PUBLISH` nunca
  llega al copy final. Metro/EFE son subsegmentos de Transporte (que sigue siendo CONTENT_GAP
  técnico); Operación Minera y Lab Minero Digital permanecen separados.
- **Diversidad editorial (motor).** Al planificar/redactar/QA un mes, usa el motor de
  diversidad (ver `docs/11_EDITORIAL_DIVERSITY.md`): huella editorial por pieza
  (`editorial_fingerprint`), novedad vs historial (`editorial_novelty`), historial en el
  drafting, QA editorial (`editorial_qa`, PASS/WARNING/FAIL) y cobertura
  (`content_coverage`). Objetivo: no repetir claim/pain/hook/arquetipo/CTA aunque cambie
  el knowledge_id. **Umbrales configurables en `config/editorial_diversity.json`.**
  Ante conflicto, **FACTUALIDAD > DIVERSIDAD** (no inventar casos/cifras/clientes, no
  convertir Sales Intelligence ni performance en hechos, no relajar CONTENT_GAP).
- **Longitud — precedencia:** la fuente de verdad EJECUTABLE de la longitud es
  `config/editorial_style.json → length` (en **caracteres**: tope duro 900, preferido
  650-850). Si este documento (`docs/09`) discrepa con ese archivo, **manda el archivo**.
