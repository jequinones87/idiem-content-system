# 10 — Estrategia editorial y control de sesgos de generación

> **Estado:** vigente. **Aplica a la generación desde los contenidos de NOVIEMBRE 2026.**
> Origen: auditoría del sistema del 7–8 de septiembre de 2026 (handoff de MKT, integrado
> el 30-09-2026). Configuración ejecutable: `config/editorial_diversity.json`.
> Este documento **manda sobre** cualquier regla anterior que fije una estructura,
> arquetipo o CTA único (ver §12 "Qué reemplaza").

## Objetivo en una frase

No producir "12 posts sobre 12 temas", sino **12 posts suficientemente distintos en
tema, argumento, estructura, hook, intención y CTA**, con una voz institucional
coherente. **Consistencia de marca: sí. Repetición editorial: no.**

## 1. El problema: diversidad taxonómica ≠ diversidad editorial

Cambiar el servicio, la célula, el `knowledge_id` o el subtema **no basta**. En octubre
los posts eran técnicamente distintos pero narrativamente iguales:
`hook → problema → "En #IDIEM…" → impacto → CTA`, casi siempre en formato
"servicio / insight técnico".

Hay que evitar repetir también: **el argumento, la promesa, el pain point, el tipo de
hook, el arquetipo narrativo, el tipo de CTA y la estructura del post.**

## 2. Sesgos medidos en el calendario de octubre

| Sesgo | Medición |
|---|---|
| CTA de tipo `contact` | 9 de 12 posts |
| Arquetipo `problem_solution` | 5 posts |
| Hooks `insight` / `risk` | 5 / 4 posts |
| Arquetipos distintos en uso | ~4 |
| CTA textual repetido | "Contáctanos y conversemos sobre tu caso" (~5) y "Contáctanos a través de nuestros canales oficiales" (~5) |

Conclusión: el sistema cambiaba el contenido técnico sin cambiar la lógica editorial.

## 3. Principio fundamental

No basta preguntar **"¿ya hablamos de este servicio?"**. Hay que preguntar
**"¿ya contamos algo parecido de esta misma manera?"**

## 4. Editorial Fingerprint (huella editorial)

Cada post registra una huella para compararlo con los recientes. Campos mínimos:
célula · servicio/capacidad · temática · **pain point** · **claim principal** ·
enfoque · **arquetipo** · **hook_type** · **cta_type** · estructura narrativa.
La comparación es **multidimensional** (varias dimensiones a la vez, no una sola).

## 5. Novelty Engine

No busca contenido idéntico: detecta **proximidad editorial**. Dos posts de servicios
distintos que siguen ambos `riesgo → consecuencia → IDIEM tiene la capacidad →
contáctanos` tienen **baja novedad**: el segundo se reasigna antes de redactarse.

## 6. Lección de arquitectura (la más importante)

> El sistema **detectaba** la repetición mejor de lo que la **evitaba**.

Fingerprint, Novelty y QA encuentran problemas *después* de escribir. La diversidad
tiene que decidirse **antes del drafting**: el planner (`select_diverse`) asigna
**arquetipo, hook_type, cta_type, ángulo y enfoque**, y el drafter los recibe como
**restricciones**, no los decide libremente. **QA es la última barrera, no el
mecanismo principal.**

## 7. Arquetipos: 6–8 lógicas narrativas realmente distintas

No variaciones cosméticas: cada arquetipo cambia la lógica del relato. Familias
(detalle y límites en `config/editorial_diversity.json`):

1. problema → impacto → capacidad
2. riesgo → prevención / gestión
3. pregunta técnica → explicación
4. dato / insight → implicancia
5. proceso → resultado
6. desafío de proyecto → solución técnica
7. evidencia / caso → aprendizaje
8. capacidad técnica → aplicación concreta

**No todos los posts comienzan hablando del servicio.**

## 8. Narrativa comercial: desde la necesidad del cliente

Evitar el patrón sistemático `servicio → explicación del servicio → CTA`.
Priorizar: **problema del cliente → consecuencia/impacto → necesidad técnica →
capacidad IDIEM → servicio → evidencia.** Clave en continuidad operacional,
infraestructura y servicios, donde el comprador piensa primero en su problema y no
en el nombre técnico del servicio.

## 9. Hooks

Rotación obligatoria: sin concentración en `insight`, `risk`, preguntas, cifras ni
afirmaciones técnicas. **Un hook NO es un pain point** (bug detectado en la auditoría:
`recent_hooks` se poblaba con `pain_point`). Se registran por separado.

## 10. CTA por intención

El CTA **no es una frase fija al final**: primero se elige la **intención**
(`cta_type`), después se redacta. Intenciones: contacto comercial · conversación
técnica · profundización · conocimiento (sin venta) · evento · descarga ·
descubrimiento de servicio. **`contact` NO es el default.** Hay memoria de CTAs
recientes para no repetir formulaciones. **No todo post termina en venta explícita.**

## 11. Historial disponible al redactar

El drafter conoce los posts recientes (hooks, claims, pain points, arquetipos, CTAs,
estructuras, servicios) **mientras escribe**, no solo en QA.

## 12. Longitud (regla única, ejecutable)

Se elimina la contradicción anterior (110–170 palabras / 1–4 emojis vs 900 caracteres).
**Regla vigente, validada en caracteres:** máximo **900 caracteres**, objetivo
habitual **820–880**; emojis **1–2 por párrafo como máximo**. Vive solo en
`config/editorial_diversity.json` → `length`.

**Excepción (MKT, 30-09-2026):** los posts de evento (webinars: inscripción, recordatorio,
día del evento) llevan URL larga y quedan **exentos del máximo de 900 caracteres**
(contador de referencia 1300), procurando igual la mayor brevedad.

## 13. Tono

Institucional, técnico, profesional, editorial y **comprensible para un público no
necesariamente especialista**. No debe parecer una secuencia de avisos: **el
conocimiento técnico aporta valor antes de introducir lo comercial.**

## 14. Fuente única de memoria

Una sola memoria rica: **el archivo mensual consolidado** (copies definitivos del mes).
De él se derivan fingerprints, estadísticas, recent hooks, recent CTAs, temas
recientes y QA. **No mantener memorias manuales paralelas que puedan divergir.**

**División acordada (MKT, 30-09-2026):** `docs/09_EDITORIAL_MEMORY.md` guarda solo **reglas y
correcciones del equipo**; hooks, CTAs, pain points, arquetipos y estadísticas recientes se
**derivan del consolidado mensual**.

## 15. Flujo objetivo

```
Planner → consulta historial reciente → select_diverse → asigna arquetipo
→ asigna hook_type → asigna cta_type → selecciona tema/conocimiento
→ Drafter → Novelty check → QA → Archive / Editorial Fingerprint
```

## 16. QA editorial (última barrera)

- **Temática:** servicios, capacidades, células, knowledge IDs.
- **Narrativa:** arquetipos, estructuras.
- **Hooks:** tipo, formulación, argumento inicial.
- **Comercial:** cta_type y redacción del CTA.
- **Conceptual:** pain points, claims, beneficios.
- **Repetición textual:** frases o construcciones demasiado cercanas a posts anteriores.

## 17. Jerarquía de fuentes y clasificación de datos

`reglas oficiales de células → reglas editoriales → brochures → Sales Intelligence →
casos/evidencias`. Sales Intelligence **complementa**, no reemplaza, a las oficiales.
Todo dato recuperado se clasifica: **`SAFE`** (publicable) · **`VERIFY`** (validar antes
de publicar) · **`INTERNAL`** (uso interno) · **`DO_NOT_PUBLISH`** (nunca llega al copy).
Esto se suma — no reemplaza — a las reglas factuales de 2A.2 (GR-01…GR-14, CLAUDE.md).

## 18. Decisión de septiembre y cierre de octubre

- Octubre **no se regenera**: se cerró por edición manual y ya está programado.
- Pasos de cierre para convertir octubre en memoria: consolidar copies definitivos →
  consolidar CTAs y enfoques → generar fingerprints → actualizar archive → QA →
  usar octubre definitivo como memoria editorial.
- **La generación preventiva por diversidad empieza en noviembre.**

---

## Estado de implementación en ESTE repo (al 30-09-2026)

| Concepto | Estado |
|---|---|
| Principios, arquetipos, hooks, CTA por intención, tono, longitud | **Integrado** como regla (este doc + `config/editorial_diversity.json` + CLAUDE.md) |
| Contradicción de longitud/emojis | **Resuelta** (fuente única en caracteres) |
| Estructura única / CTA fijos en memoria previa | **Corregido** (pasan a ser *un* arquetipo / ejemplos no default) |
| `select_diverse` en el planner | **Pendiente (código)** — hoy el planner solo diversifica por subtema y el ledger por `knowledge_id` |
| Editorial Fingerprint + archive | **Pendiente (código)** |
| Novelty Engine | **Pendiente (código)** |
| `recent_hooks` / `recent_ctas` (hook ≠ pain point) | **Pendiente (código)** — el bug no existe aquí porque el campo aún no existe; nacer separado |
| Validador automático de caracteres | **Parcial** — contador en la workstation; falta validación en el pipeline |
| Clasificación SAFE/VERIFY/INTERNAL/DO_NOT_PUBLISH | **Pendiente** — no hay Sales Intelligence ni brochures en este repo aún |
| Octubre consolidado como memoria | **Pendiente** — los copies definitivos de octubre viven en el artefacto, no en el repo |

## Cómo lo aplico al redactar (checklist operativo, desde noviembre)

Mientras el código no exista, **lo aplico manualmente en cada grilla**:

1. Antes de escribir, armo la **tabla de asignación** del mes: por post, arquetipo ·
   hook_type · cta_type · pain point · claim, respetando los límites de
   `config/editorial_diversity.json`. Se la muestro a MKT **antes** de redactar.
2. Reviso el mes consolidado anterior (memoria) para no repetir hooks, CTAs ni
   argumentos.
3. Redacto cada post **con su arquetipo/hook/CTA asignados como restricción**.
4. Valido: ≤ 900 caracteres, 1–2 emojis/párrafo, CTA no repetido textual, no todos
   con "En #IDIEM" en el mismo lugar.
5. Registro la huella de cada post en el consolidado del mes.
