# IDIEM Content System (2A.2)

Sistema **determinista y auditable** de planificación/redacción de contenido para
el LinkedIn de IDIEM, construido sobre el paquete de conocimiento **2A.2**. La
biblioteca IDIEM bajo `data/` es la **única fuente de verdad**: ninguna afirmación
concreta se genera sin trazar a un `knowledge_id` o `auxiliary_id`.

> Este repositorio implementa **Milestones 0–4** del `docs/03_IMPLEMENTATION_PLAN.md`.
> Las capas de diseño/assets y publicación quedan como **interfaces/placeholders**
> (ver `src/idiem/interfaces.py`). No hay automatización de publicación en este hito.

## Principios innegociables (de `CLAUDE.md`)

- La biblioteca 2A.2 es la fuente de verdad; no se rellenan vacíos con conocimiento general.
- Toda afirmación traza a `knowledge_id` / `auxiliary_id` permitido.
- Se respetan `generation_policy` y `usage_instruction` siempre.
- `NAME_ONLY_DO_NOT_EXPAND` → nombrar, no explicar.
- `USE_TECHNICAL_CORE_BLOCK_CLAIMS` → núcleo técnico sí, rankings/superlativos no.
- Evidencia auxiliar nunca se convierte en capacidad técnica.
- Relaciones excluidas nunca son evidencia.
- Ante evidencia insuficiente → `CONTENT_GAP` / `EXPERT_INPUT_REQUIRED` (**fail closed**).
- `data/` es **inmutable**; el estado generado va a `output/`.
- Reglas de celda **externas/configurables** en `config/cell_rules.json`.

## Estructura

```
data/                canónicos 2A.2 (READ-ONLY, no mutar)
docs/                handoff (01–04)
config/cell_rules.json   reglas de celda externas/configurables (regla 11)
config/planner.json      config del planner (pesos/cadencia/target)
config/editorial_style.json / .md   guía editorial (tono/estructura/hashtags/emojis)
data/ext_2A3/evidence_2A3.json   extensión aditiva de evidencia (no muta 2A.2)
schemas/content_brief.schema.json   JSON Schema del brief
src/idiem/
  loader.py          M1  carga canónicos -> KnowledgeBase indexada
  models.py          modelos tipados (dataclasses)
  policies.py        vocabulario y enforcement de políticas
  integrity.py       M1  checks de cierre (fail closed)
  retrieval.py       M2  filtros deterministas (sin LLM)
  cells.py           reglas de celda (consume config)
  factsheet.py       M3  motor de fact sheet
  brief.py           M4  generador de brief (schema-valid)
  planner.py         M5  planner mensual (cuotas, cobertura, gaps)
  drafting.py        M6  drafting adapter (esqueleto determinista + copy publicable acotado)
  review.py          Vista de revisión mensual (plan -> brief anclado -> copy -> HTML)
  interfaces.py      placeholders diseño/publicación (rule 12)
  cli.py             CLI de demo local
tests/               pytest (integridad, retrieval, fact sheet, brief, tests A–F)
output/              estado generado (git-ignored)
```

## Setup

```bash
pip install -r requirements.txt
```

## Uso

```bash
# Checks de integridad (reproduce el cierre 2A.2)
PYTHONPATH=src python -m idiem.cli integrity

# Retrieval por célula
PYTHONPATH=src python -m idiem.cli retrieve "INFRA OPERACIÓN MINERA"

# Fact sheet
PYTHONPATH=src python -m idiem.cli factsheet "LAB MINERO DIGITAL" --topic Triaxial

# Brief (schema-valid, DRAFT) y escritura a output/
PYTHONPATH=src python -m idiem.cli brief "INFRA PÚBLICA RESILIENTE" --write

# Plan mensual (JSON + CSV a output/)
PYTHONPATH=src python -m idiem.cli plan 2026-09 --target 12 --write

# Drafting adapter: brief + copy acotado al fact sheet (sigue DRAFT)
PYTHONPATH=src python -m idiem.cli draft "INFRA OPERACIÓN MINERA"

# Vista de revisión mensual (HTML interno + CSV + JSON a output/)
PYTHONPATH=src python -m idiem.cli review 2026-09 --target 12 --write

# Demo funcional (M0–M6)
PYTHONPATH=src python -m idiem.cli demo
```

## Tests

```bash
python -m pytest
```

Cubren (97 tests): reproducción del cierre y fail-closed ante IDs duplicados/
política inválida; retrieval por célula sin fuga cruzada; fact sheet; brief
schema-valid; planner mensual (cuotas, cobertura, sin préstamo entre células,
sin reuso consecutivo, historial reciente); drafting adapter (sin hechos nuevos,
sigue `DRAFT`, conserva trazabilidad); interfaces de handoff; y los **tests
obligatorios A–F** de `docs/04_ACCEPTANCE_CRITERIA.md` (Transporte→`CONTENT_GAP`,
`NAME_ONLY`, Triaxial núcleo/claims, frontera minera, evidencia excluida,
trazabilidad de IDs).

## Integridad verificada vs `docs/04`

292 relaciones · 137 asignadas · 102 técnicas · 35 auxiliares · 150 reserva ·
5 excluidas · 116 ítems activos · 29 documentos. Por célula: IPR 24 · IHA 6 ·
ICT 0 · IOM 65 · LMD 21. **Todos reproducidos.**

## Encuadre en el roadmap (`docs/08`)

Dominios mantenidos **desacoplados** (roadmap §11): Knowledge → Editorial →
Planner producen el brief aprobado; Visual / Assets / Integrations solo
**consumen** output aprobado. La evidencia IDIEM es la capa más estable.

| Fase | Estado | En este repo |
|---|---|---|
| A — Knowledge System | ✅ Completa (handoff 2A.2) | consumida en `data/` (inmutable) |
| B — Content Planner | 🟡 En implementación | M0–M4 + **M5 planner mensual** (`planner.py`) |
| C — Editorial Drafting | 🟡 En implementación | fact sheet + brief + **M6 drafting adapter** (`drafting.py`) |
| D — Design System | ⏳ Handoff futuro | **interfaz** `DesignSystemProvider` (placeholder) |
| E — Image Library | ⏳ Handoff futuro | **contrato** `ImageAsset` + `AssetQuery` (placeholder) |
| F–I — Visual/Approval/Metricool/n8n/Publishing | ⏳ Futuras | interfaces `VisualAssetProvider` / `Publisher` (placeholder) |

Decisiones visuales (paleta, tipografías, templates, clasificación de fotos,
publicación) **no** se toman aquí: llegan por handoffs específicos. `interfaces.py`
deja los contratos listos sin implementarlos ni hard-codear nada visual. La ruta
gráfica elegida para el futuro es **Claude Artifacts (HTML/SVG)**, a la espera del
handoff de Design System oficial.

### Redacción de copy (M6): dos caminos, mismos guardrails

- **Esqueleto determinista** (`DeterministicDrafter`): sin credenciales; recombina
  los hechos del brief como material de trabajo interno.
- **Copy publicable**: `build_drafting_request` genera un encargo **acotado** (solo
  `allowed_facts` + ángulo + matices + claims/términos bloqueados) e incorpora la
  **guía editorial** (`config/editorial_style.json`) — tono, estructura
  (hook→problema→solución IDIEM→impacto→CTA), longitud objetivo (~110–170 palabras),
  emojis medidos y hashtags recomendados por célula. El texto final lo produce
  `LLMDrafter` (credential-agnostic, modo automático) o `ingest_draft` (redacción
  asistida en sesión, **sin API key**). Ambos validan **fuga de `knowledge_id`** y
  **términos bloqueados** (rankings/superlativos, GR-04), mantienen `DRAFT` y
  conservan trazabilidad.
- **Profundidad técnica sin inventar**: los briefs por-post se construyen con
  `enrich_same_service=True` — al ítem ancla se suman los ítems de la **misma célula
  y mismo servicio**, más la **extensión de evidencia 2A.3** (`data/ext_2A3/`):
  capacidades técnicas citadas del texto fuente de los brochures, con política por
  registro y **superlativos/rankings bloqueados** (GR-04). Es una **capa aditiva** que
  no muta 2A.2. Si la evidencia sigue delgada: post corto honesto o `EXPERT_INPUT_REQUIRED`.

### Variedad temática: selección diversa + subtemas + de-dup por mes

Para evitar que los posts repitan el mismo tema, el planner **no toma los primeros
N por código**. `planner._diversify` reordena con tres criterios deterministas:

1. **Servicio primero** (Fase A): el primer tramo del mes recorre servicios
   distintos, así dos posts nunca comparten la evidencia de un mismo servicio.
2. **Subtema** (Fase D, `config/subthemes.json`): dentro de un servicio agrupa las
   `capability` en **temas editoriales** (p. ej. tres tipos de "Monitoreo" → un
   solo tema), y un **de-dup de subtema a nivel mes** hace que los 12 posts abarquen
   temas distintos incluso entre células.
3. **Evidencia primero**: como representante de cada tema elige el ítem **mejor
   documentado** (más evidencia 2A.3 + fuentes propias), no el de menor código.

Además, `compose_month` comparte un `used_enrichment_ids`: cada registro **2A.3
aparece a lo más una vez al mes**, por lo que credenciales o atributos (ISO, HSEC…)
no se repiten post a post. Todo es determinista y trazable.

La capa **2A.3** (`data/ext_2A3/`) fue profundizada (Fase E) curando más
capacidades técnicas de los brochures para servicios antes sin cobertura
(ingeniería contra incendios, sustentabilidad y arquitectura, ensayos de
especialidades, gestión de vulnerabilidad, laboratorio de rocas…), siempre
grounded al texto fuente y con superlativos/rankings bloqueados (GR-04).

### Anulaciones auditadas de política (2A.3 `policy_overrides`)

Un cambio de `generation_policy` sobre un `knowledge_id` de 2A.2, **autorizado por
la fuente de verdad**, se registra en `data/ext_2A3/` como `policy_overrides`
(aditivo; nunca muta 2A.2). Ejemplo: **GREEN HOSPITAL** pasa de
`NAME_ONLY_DO_NOT_EXPAND` a núcleo técnico (`USE_TECHNICAL_CORE_BLOCK_CLAIMS`):
se habilitan los hechos definicionales/técnicos declarados en el override y los
superlativos/rankings o logros de cliente puntual **permanecen bloqueados**
(GR-04). El factsheet aplica el override en vez de la política canónica y lo
registra en el log; la vista "Ver fuente" muestra su procedencia.

### Planner: sustitución de célula sin cobertura

`config/planner.json` permite `substitutions`: cuando una célula tiene cuota pero
**cero cobertura** (p. ej. Transporte), su cuota se reasigna a las células fallback
configuradas (Salud/Pública) que sí tienen cobertura. Es una regla **explícita y
logueada**, no un rebalanceo silencioso; el conocimiento nunca cambia de célula.

### Vista de revisión: "Ver fuente"

Cada post expone un botón **Ver fuente** que abre un popup con el **texto exacto
verificado** (evidencia + documento + página) de cada knowledge item y registro 2A.3,
para chequear veracidad. No se muestran códigos internos de relación.

## Fuera de alcance en este hito

Generación gráfica final, selección automática de fotos, publicación social,
enriquecimiento externo de hechos, verificación normativa en vivo, scraping,
integraciones CRM/ads. La capa visual/publicación entra en handoffs posteriores
detrás de las interfaces de `src/idiem/interfaces.py`.
