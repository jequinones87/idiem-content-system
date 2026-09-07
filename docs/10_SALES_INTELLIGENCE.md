# Sales Intelligence v2 — capa complementaria

Capa de conocimiento **comercial** derivada de las PPT de venta por célula/segmento.
Enriquece la ideación y redacción (dolores del mandante, necesidades, propuestas de
valor, capacidades, casos, ángulos), **sin** reemplazar ni degradar las reglas
existentes.

- Paquete (fichas, reglas, casos): `knowledge/sales_intelligence/`
- Módulo: `src/idiem/sales_intelligence.py`
- Ruteo/precedencia configurables: bloque `sales_intelligence` en `config/cell_rules.json`
- Tests: `tests/test_sales_intelligence.py`

## Precedencia (autoridad, de mayor a menor)

1. reglas oficiales de células y clasificación
2. reglas editoriales
3. servicios/brochures validados
4. **Sales Intelligence** (esta capa)
5. casos/evidencias
6. fuentes externas

Ante contradicción, **prevalece la fuente superior**. Sales Intelligence **jamás**
clasifica un servicio ni redefine una célula: por eso el módulo no expone ninguna
función de clasificación. La célula se resuelve SIEMPRE con las reglas oficiales
(`cells.py` / `cell_rules.json`) **antes** de consultar esta capa.

## Retrieval contextual (perezoso)

```python
from idiem.sales_intelligence import load_sales_intelligence
si = load_sales_intelligence()

# La célula ya viene resuelta por las reglas oficiales:
ctx = si.context_for("INFRA OPERACIÓN MINERA")          # una ficha
ctx = si.context_for("INFRA CRÍTICA TRANSPORTE")        # Metro + EFE
ctx = si.context_for("INFRA CRÍTICA TRANSPORTE", "metro")  # solo Metro

enrichment = ctx.to_drafting_enrichment()  # material listo para el redactor
```

- Solo se parsea(n) la(s) ficha(s) de la célula pedida (nunca las seis).
- **Metro** y **EFE** son subsegmentos de **INFRA CRÍTICA TRANSPORTE** (que conserva su
  regla oficial: sin knowledge_items técnicos activos → `CONTENT_GAP`; esta capa no la
  habilita).
- **Operación Minera** y **Laboratorio Minero Digital** permanecen separados: cada uno
  recupera únicamente su propia ficha.
- **Salud Pública** es una fuente dentro de **Hospitalaria y Asistencial**; **MOP** dentro
  de **Infraestructura Pública Resiliente** (respetando exclusiones existentes).

Demo por consola:

```
PYTHONPATH=src python -m idiem.sales_intelligence --cell "INFRA OPERACIÓN MINERA"
```

## Estados de publicación (fail closed)

Cada sección de una ficha lleva un estado; los elementos se exponen con él:

| Estado | Significado | En el output |
|---|---|---|
| `SAFE` | concepto general utilizable | puede alimentar copy (respetando reglas editoriales) |
| `VERIFY` | dato que requiere validación humana/fuente vigente | se conserva la idea, el claim va **marcado pendiente**; no se convierte en hecho |
| `INTERNAL` | contexto de razonamiento | no se copia literalmente como mensaje público |
| `DO_NOT_PUBLISH` | placeholder/contradicción/no validado | **excluido** del output final |

Un estado **compuesto** (p.ej. `VERIFY / INTERNAL`, `SAFE as concepts / VERIFY …`)
resuelve al **más restrictivo** para publicar: nunca asciende silenciosamente a `SAFE`.
Un estado desconocido nunca es `SAFE`.

- `element.publishable_without_validation` → solo `SAFE`.
- `element.needs_validation` → `VERIFY`.
- `element.is_excluded` → `DO_NOT_PUBLISH`.
- `ctx.to_drafting_enrichment()` entrega SAFE como afirmable, VERIFY como
  `verify_flags` (pendientes) y **omite** DO_NOT_PUBLISH.

## Guardrails de seguridad editorial

`si.assert_publishable(text)` falla cerrado si el copy final contiene:
- lenguaje de garantía causal (`garantiza`, `elimina`, `evita`, `asegura`, `impide`…),
  con límite de palabra para no chocar con términos válidos (`aseguramiento`);
- placeholders (`Agregar una imagen`, `XXXX`…);
- una frase `DO_NOT_PUBLISH` de las fichas (p.ej. “laboratorio líder en Chile”).

Toda cifra, %, monto, fecha, proyecto en curso, cobertura, certificación, capacidad
24/7, plazo, cantidad de laboratorios/profesionales o afirmación legal (Ley 21.094 /
Ley 19.886 / CGR) es `VERIFY`: no publicar sin validación humana.

## Patrón de contenido recomendado

`problema/necesidad → impacto en el mandante → capacidad IDIEM → evidencia/caso → CTA`

No se fuerza si el formato/objetivo editorial pide otro (p.ej. saludos institucionales).

## Trazabilidad

`ctx.trace()` (y `ficha.trace()`) registran célula, segmento, ficha consultada, PPT de
origen (`source_ppt`), `drive_id` y las secciones VERIFY usadas. No es necesario mostrar
esa trazabilidad en el copy final.

## Integración con el sistema actual

- Es una capa **aditiva**: no muta `data/` (2A.2) ni altera el pipeline de generación
  vigente (`gen_month_grid` / `review` / `drafting`). Se consulta explícitamente al
  idear/redactar un mes (SAFE pains/ángulos + flags VERIFY), en línea con el patrón de
  extensión ya existente (`data/ext_2A3`).
- El mapeo célula-interna → célula-oficial vive en `config/cell_rules.json`
  (`sales_intelligence.cell_map`), configurable sin tocar código (regla 11 de CLAUDE.md).
