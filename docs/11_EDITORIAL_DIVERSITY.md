# Diversidad editorial — arquitectura

El sistema controla simultáneamente **factualidad + trazabilidad + cobertura + frescura
+ diversidad editorial + consistencia de marca**, sin debilitar ninguna garantía factual
previa. Esta capa responde no solo *"¿puedo respaldar esto?"* sino *"¿aporta algo
editorialmente distinto de lo publicado recientemente?"*.

## Tres capas (separación explícita)

- **Knowledge Base** (`data/`, `loader`, `retrieval`, `cells`): qué podemos **afirmar**.
  Fuente factual de verdad. Intacta.
- **Sales Intelligence** (`knowledge/sales_intelligence`, `sales_intelligence.py`): desde
  qué **necesidad/ángulo** contar algo. Enriquece; **no** es fuente factual.
- **Editorial Engine** (esta capa): **cómo** lo contamos y cómo **no** nos repetimos.

Ante conflicto: **FACTUAL SAFETY > EDITORIAL DIVERSITY**, siempre.

## Flujo

```
Knowledge Base
  ↓
Candidate Pool            (planner: _candidates por célula, cooldown por knowledge_id)
  ↓
Novelty scoring           (editorial_novelty.select_diverse / novelty_score)  ← reutilizable
  ↓
Planner  (compose)        (review.compose_month / design_system.compose_current)
  ↓
Drafting + Editorial      (drafting.build_drafting_request: allowed_facts + estilo +
History                    Sales Intelligence + editorial_history)
  ↓
Factual QA                (drafting: fuga de hechos, claims bloqueados, CONTENT_GAP)
  ↓
Editorial QA              (editorial_qa.check_month: concentración/similitud/diversidad)
  ↓
Monthly Archive           (design_system/archive_month.py → content/archive/<mes>.json,
                           con editorial_fingerprint por pieza + fingerprint_index)
  ↓
Renderer                  (design_system: workstation/carrusel)
```

## Editorial fingerprint (`src/idiem/editorial_fingerprint.py`)

Huella estructurada por pieza (determinista, auditable) con enums normalizados:

- `hook_type`: risk · question · insight · statistic · misconception · explanation ·
  consequence · opportunity · checklist · case
- `cta_type`: contact · learn_more · self_assessment · question · conversation ·
  visit_service · save_reference · no_cta
- `editorial_archetype`: problem_solution · technical_insight · explainer ·
  case_or_experience · method_or_evidence · sector_question · checklist ·
  institutional_or_occasion
- `visual_theme`: people · laboratory · field · infrastructure · equipment · detail ·
  aerial · graphic
- más `service`, `subtheme`, `primary_claim`, `pain_point`, `pain_category`, `angle`,
  `format`, `evidence_ids`, `knowledge_id`, `photo_id`.

La huella **DESCRIBE** la pieza; **no autoriza** contenido: que algo se clasifique
`case_or_experience` no habilita inventar un caso — eso lo impide la gobernanza factual
(allowed_facts / evidence / CONTENT_GAP). Se archiva por pieza (`editorial_fingerprint`)
y agregada (`fingerprint_index`).

## Novelty engine (`src/idiem/editorial_novelty.py`)

Distingue diversidad **taxonómica** (knowledge_id/servicio/subtema) de la **editorial**
(claim/pain/hook/arquetipo/CTA/enfoque). Sin embeddings ni dependencias externas:
similitud local (Jaccard de tokens normalizados) + comparación de dimensiones +
**equivalencia estructural** (mismo `pain+hook+arquetipo+CTA` ⇒ editorialmente cercano,
aunque cambie el vocabulario — el "principio final" del encargo).

- `novelty_score(fp, history)` → `[0,1]` + razones; `novelty_band` (high/medium/low).
- `near_duplicates` / `pairwise_near_duplicates`.
- `select_diverse(candidates, k, history)` → selección greedy pool→k (reutilizable por el
  planner; nunca inventa candidatos).
- `load_history(month, window)` lee `content/archive/` (ventana configurable).

## Historial editorial → drafting

`drafting.build_drafting_request(brief, month="YYYY-MM")` adjunta `editorial_history`
(subtemas, claims, pains, hooks, hook_types, arquetipos, cta_types, `recent_phrases_to_avoid`).
Instrucción explícita: **diferenciarse conceptual y editorialmente** (no sinónimos); el
historial sirve para **EVITAR REPETICIÓN**, **nunca** es fuente de hechos.

## Editorial QA (`src/idiem/editorial_qa.py`)

Separado del QA factual. Por pieza (tope de caracteres, fingerprint completo, cta/arquetipo
válidos) y por mes (concentración de arquetipo/cta/hook/pain/subtema/visual, diversidad
mínima, foto repetida intra-mes y en cooldown, near-duplicates). Devuelve
**PASS/WARNING/FAIL con motivos** + reporte mensual legible.

## Cobertura (`src/idiem/content_coverage.py`)

Por célula: items totales / en cooldown / **frescos** + STATUS (OK/MEDIUM/LOW/CONTENT_GAP).
Responde qué célula necesita nuevas PPT/brochures/insumos antes de planificar. Respeta
CONTENT_GAP (Transporte sin ítems técnicos activos).

## Memoria unificada

`content/archive/<mes>.json` es el registro **rico** (copy, foto, fingerprint, etc.). El
`state/published_ledger.json` es un **índice derivado** de cooldown: `ledger.build_ledger_from_archive()`
lo reconstruye desde el archivo para que ambas memorias **no diverjan**.

## Performance (andamiaje, `src/idiem/performance.py`)

`content/performance.csv` + loader. Estructura preparada para asociar métricas a
`content_id`. **No** altera el sistema editorial ni es fuente factual; uso futuro = señal
de priorización.

## Configuración (`config/`)

- `editorial_style.json` → **longitud (fuente de verdad ejecutable, en caracteres)** +
  voz/estructura/emoji/hashtags/pains.
- `editorial_diversity.json` → **todos los umbrales**: cooldown, ventana, pool multiplier,
  diversidad (min arquetipos, máximos por arquetipo/cta/hook/pain/subtema/visual),
  similitud, novelty weights/bands, coverage. El límite de caracteres **no** se duplica
  aquí (vive en `editorial_style`).

### Precedencia de reglas
`config/editorial_style.json` (ejecutable) **manda** sobre `docs/09_EDITORIAL_MEMORY.md`
(narrativo) si discrepan — en particular la **longitud** (900 caracteres, no palabras).

## Comandos

```bash
# Tests (incluye QA/diversidad)
PYTHONPATH=src python -m pytest -q

# Archivar un mes (con fingerprints)
PYTHONPATH=src python design_system/archive_month.py --month 2026-10 --out-dir content/archive

# QA + reporte editorial de un mes
PYTHONPATH=src python -m idiem.editorial_qa --month 2026-10          # reporte legible
PYTHONPATH=src python -m idiem.editorial_qa --month 2026-10 --json   # QAReport JSON

# Cobertura editorial (frescura por célula) para planificar el mes siguiente
PYTHONPATH=src python -m idiem.content_coverage --month 2026-11

# Contexto de Sales Intelligence por célula
PYTHONPATH=src python -m idiem.sales_intelligence --cell "INFRA OPERACIÓN MINERA"
```

## Gaps documentados (ver §26.3 del encargo)

- **Selección pool→óptimo en el planner en vivo**: `select_diverse` existe y está
  testeado, pero `design_system.compose_current` (octubre) sigue fijando `MONTH_PICKS`
  exactos para no desestabilizar la parrilla ya aprobada. Integración del pool en el
  planner mensual queda como dirección (usar `select_diverse` sobre `_candidates`).
- **Separación content/renderer (Fase 7)**: `content/archive/<mes>.json` ya es el registro
  editorial canónico; el renderer de `design_system` todavía usa `COPY`/`GRAPHIC` como
  fuente viva. La migración a que el renderer consuma el JSON mensual queda como dirección.
- **visual_theme** se clasifica best-effort desde `photo_id`/detalle; fotos sin metadata
  clara quedan `null` y no penalizan.
