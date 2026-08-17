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

# Primer demo funcional (los 4 requisitos del handoff)
PYTHONPATH=src python -m idiem.cli demo
```

## Tests

```bash
python -m pytest
```

Cubren: reproducción del cierre y fail-closed ante IDs duplicados/política
inválida; retrieval por célula sin fuga cruzada; fact sheet; brief schema-valid;
y los **tests obligatorios A–F** de `docs/04_ACCEPTANCE_CRITERIA.md`
(Transporte→`CONTENT_GAP`, `NAME_ONLY`, Triaxial núcleo/claims, frontera minera,
evidencia excluida, trazabilidad de IDs).

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
| B — Content Planner | 🟡 En implementación | M0–M4 listos; M5 (grilla mensual) pendiente |
| C — Editorial Drafting | 🟡 En implementación | fact sheet + brief; M6 (copy) pendiente |
| D — Design System | ⏳ Handoff futuro | **interfaz** `DesignSystemProvider` (placeholder) |
| E — Image Library | ⏳ Handoff futuro | **contrato** `ImageAsset` + `AssetQuery` (placeholder) |
| F–I — Visual/Approval/Metricool/n8n/Publishing | ⏳ Futuras | interfaces `VisualAssetProvider` / `Publisher` (placeholder) |

Decisiones visuales (paleta, tipografías, templates, clasificación de fotos,
publicación) **no** se toman aquí: llegan por handoffs específicos. `interfaces.py`
deja los contratos listos sin implementarlos ni hard-codear nada visual.

## Fuera de alcance en este hito

Generación gráfica final, selección automática de fotos, publicación social,
enriquecimiento externo de hechos, verificación normativa en vivo, scraping,
integraciones CRM/ads. La capa visual/publicación entra en handoffs posteriores
detrás de las interfaces de `src/idiem/interfaces.py`.
