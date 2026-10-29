# 14 — Playbook de producción (método vigente por formato)

> Un solo lugar para saber **cómo se produce hoy** cada pieza. Datos ejecutables en
> `config/production_registry.json` (workstations publicados y métodos); los tests de
> `tests/test_production_registry.py` fallan si una pieza se sale de estos métodos.
> Origen (28-10-2026): los extras de aluviones se propusieron sin mirar lo hecho en oct–dic
> porque ese trabajo estaba en ramas sin fusionar.

## 0. Antes de producir (obligatorio, también para extras y pedidos sueltos)

1. Correr `PYTHONPATH=src python -m idiem.preflight` (el hook de inicio de sesión muestra el resumen).
   - Si lista ramas con trabajo **no integrado**: fusionarlas en la rama de trabajo (o preguntar) **antes**
     de proponer nada. Ahí suelen estar decisiones de MKT que todavía no ves.
   - Usar los **siguientes IDs libres** que informa para fuentes `SRC-*` y temas `TOP-*` (cuenta todas las ramas).
2. Abrir el **workstation de los 2 últimos meses** (URLs en el registro) y sus archivos
   `state/plans/AAAA-MM_{asignacion,copies,graficas}.json`: reutilizar sus estructuras, no inventar.
3. Leer `docs/09_EDITORIAL_MEMORY.md` (memoria y checklist ✅) y la sección de videos de `CLAUDE.md`.
4. Si el pedido no calza con ningún método de abajo: **preguntar a MKT** (fail closed), no improvisar un formato.

## 1. Métodos por formato

| Formato | Método vigente | Código / datos | Referencia aprobada |
|---|---|---|---|
| Post estático | Plantilla 01 Servicios (foto + anillo rojo + mensaje; anillo al lado contrario del sujeto) | `gen_month_ws.py → static_canvas` · `graficas.posts[k].{svc,msg,base}` | posts estáticos de nov/dic |
| Carrusel | **Plantilla 02**: misma foto en todas las láminas; portada con degradado (kicker + título con palabra roja); intermedias con velo, número rojo, ícono PNG, barra roja, título con caja roja y bajada; cierre de marca sin foto | `gen_month_ws.py → carousel_slides` + `carousel.CAROUSEL_CSS` · `graficas.posts[k].carousel.{portada,intermedias,cierre}` · íconos `design_system/assets/icon_<nombre>.png` | carruseles de nov/dic |
| Pieza conmemorativa / saludo | foto + velo + kicker + título + bajada | `gen_month_ws.py → special_canvas` | efemérides nov/dic |
| Video de carrusel (en capas) | skill `.claude/skills/video-carrusel-idiem` | config JSON → build → render → QA | SIM 11-nov |
| Video gráfico (más gráfico que texto, cortes rápidos, formatos no 1:1) | **Remotion** en `jequinones87/motion-graphics-ia` (un proyecto por video) | escenas de ~4 s, barridos rojos entre escenas, íconos trazo a trazo, cierre sobre el logo; música con `music.py` | `idiem-controversias` (dic #4), `idiem-aluviones` (extra nov A) |
| Entrega | **Workstation** con los botones compartidos (`design_system/workstation_shared`): estado, aprobar, agenda, LinkedIn, PNG/PDF/MP4, notas, historial | `gen_month_ws.py --month AAAA-MM` (mes) · `--set <prefijo>` (extras) · capacidades `db`, `user`, `downloads` | todos los meses desde nov |

Reglas que no se negocian:
- **Sin variantes de diseño por post.** Si una pieza necesita algo que la plantilla no tiene, se propone a MKT
  como cambio de plantilla (para todos), no como excepción silenciosa.
- **Nunca entregar solo texto en el chat**: siempre el workstation, y en el chat un resumen + el enlace.
- Videos: textos literales del workstation; música = aprobación auditiva de una persona.
- Un workstation nuevo se agrega a `config/production_registry.json` en el mismo commit en que se publica.

## 2. Flujo de un juego de piezas fuera de grilla (extras)

1. Datos en `state/plans/<prefijo>_{asignacion,copies,graficas}.json` (mismo esquema que el mes).
2. `PYTHONPATH=src python design_system/gen_month_ws.py --month AAAA-MM --set <prefijo> --build <dir> --emit`
3. `node design_system/render_bundle.cjs <dir>/manifest.json`
4. `... --assemble --out <dir>/site/index.html --label "· <nombre>" --title "Workstation <Nombre>" --ws-url <url>`
5. Publicar con los MP4 en `media/` y registrar la URL en el registro.

## 3. Ramas

- Rama de integración: `claude/file-reading-nsposu` (el PR #1 la lleva a `main`, que sigue vacía).
- Cada sesión trabaja en su rama `claude/*` y la devuelve a la integración por PR. Una rama que queda
  sin fusionar deja sus decisiones invisibles para las sesiones siguientes: el preflight lo avisa.
