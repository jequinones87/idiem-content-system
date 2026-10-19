# 09 — Memoria editorial (antecedentes para futuros posts)

> Este archivo es **memoria acumulada** de las decisiones de tono, estilo y hechos
> que el equipo de IDIEM valida sobre los posts. Cada corrección aprobada se guarda
> aquí para que los posts futuros la respeten **sin volver a pedirla**. Es fuente de
> verdad editorial y complementa a `CLAUDE.md` y al paquete 2A.2 (fuente factual).
>
> Regla: si una corrección de un revisor contradice algo de aquí, se actualiza este
> archivo (con fecha) — no se ignora.

## Reglas factuales (NO negociables)

Estas nacen de correcciones del equipo. Son de aplicación obligatoria.

### Green Hospital (célula IHA)
- **Green Hospital es una certificación PROPIA de IDIEM.** No es un esquema de un
  tercero que IDIEM "apoya": IDIEM la impulsa y la otorga (existe "Nivel Oro").
- **NO mencionar a "Salud sin Daño" / "Salud sin Daños"** ni presentarla como socia.
  Esa organización **ya no** forma parte del programa. (Corrección 2026-08-28.)
- Green Hospital **se complementa con otras certificaciones**, p. ej. **ISO 50001**
  (gestión de la energía). Escribir "ISO 50001" (no "ISO 50.0001").
- Su evaluación abarca: eficiencia energética y reducción de emisiones, gestión de
  residuos clínicos, uso sostenible de agua y materiales, compras responsables y
  promoción de la salud ambiental.

### Ensayos no destructivos / soldaduras (célula LMD)
- **La soldadura se INSPECCIONA, no se "verifica/certifica" una por una.** La
  inspección es por **muestreo, según el plan de inspección**. Evitar titulares como
  "cada soldadura verificada".
- **Lo que se CALIFICA es el soldador** (y el procedimiento de soldadura), **no la
  soldadura**. No hablar de "calificación de soldaduras". Sí es correcto: "asesoría
  en la calificación de procedimientos y de soldadores". (Corrección 2026-08-28.)

### Acústica (célula IPR)
- Norma vigente de ruido: **D.S. 38/2011 MMA** (referible como "D.S. 38-11 MMA");
  mencionar cuando aplique el **futuro D.D. 14/24**.

### Temas y personas sensibles (MKT, 30-09-2026)
- **Centro Cultural GAM:** tema sensible hoy. **No usarlo como caso** (KB-IPR-023) hasta nuevo aviso.
- **David Silva (Jefe División Aceros Control):** no le gusta compartir contenido. **No publicar
  aprendizajes, contenidos ni resúmenes de sus charlas o webinars.** La logística de eventos
  donde es relator sí se puede comunicar.
- Regla general: todo post que **nombre un proyecto o caso** se marca para que MKT valide su
  sensibilidad antes de redactar.
- **Asesoría a la inspección técnica de obras (AITO):** **no publicar** este tema (MKT, 19-10-2026). Las
  afirmaciones del servicio en el banco de temas quedan en `DO_NOT_PUBLISH` y su tema, descartado.
- **Un caso/proyecto nombrado va en UN solo post por mes** (MKT, 01-10-2026). Si otro post toca el
  mismo servicio, se redacta como servicio genérico, sin repetir el caso. Ej.: nov-2026, el Aeropuerto
  AMB queda solo en el post de laboratorio en obra; el de incendios va sin mencionarlo.
- **Laboratorio en obra:** el foco es el concepto (laboratorio dentro de la obra, junto a los frentes
  de trabajo) ilustrado con el caso, no el material (hormigones). (MKT, 01-10-2026.)

### Operación minera (célula IOM) — MKT, 05-10-2026
- **Depósitos de relaves:** infraestructura crítica que requiere **control 24/7** por seguridad y que
  **nunca está terminada** (crece mientras la operación continúa): el monitoreo es un proceso que no
  termina. Explicar *por qué* se monitorea, no solo nombrar el servicio. (Input experto MKT: se usa como
  característica de la infraestructura; la capacidad IDIEM sigue siendo literal: monitoreo a distancia
  para resguardar de manera permanente la seguridad.)
- **SIM (gestión de integridad estructural):** la secuencia es planificación → antecedentes → inspecciones
  → instrumentación/**monitoreo**. El **monitoreo siempre va al final**.
- **Control de productividad (KB-IOM-019/020):** ⛔ no usar hasta nuevo aviso — MKT no tiene certeza del
  servicio. Los servicios de productividad del sitio web (área Productividad, pérdida de productividad en
  controversias, industrialización) **sí están disponibles en VERIFY** (MKT, 19-10-2026): se verifican y
  corrigen cuando aparezcan en un post, sin apoyarse en KB-IOM-019/020.
- **HDPE:** los ensayos "verifican el cumplimiento del proyecto" (formulación preferida por MKT).

### Contenidos desde fuentes expertas (MKT, 14-10-2026)
- Los posts basados en charlas/presentaciones de especialistas **no nombran ni citan al expositor ni a la
  charla**: el foco es el tema. Ver `docs/11_FUENTES_EXPERTAS_Y_BANCO_DE_TEMAS.md`.

### Ingeniería contractual (célula IHA)
- Ámbitos que IDIEM atiende de forma explícita en el sector Salud: **análisis de
  programación**, **análisis ante término anticipado de contrato**, respaldo técnico
  para gestión de contratos y **reclamaciones**.

## ⚠️ Estrategia editorial y control de sesgos (desde noviembre 2026) — MANDA

La auditoría de sept 2026 detectó que los posts eran técnicamente distintos pero
**narrativamente iguales** (octubre: CTA `contact` 9/12, ~4 arquetipos, dos fórmulas de
CTA repetidas ~5 veces cada una). Regla vigente: **`docs/10_ESTRATEGIA_EDITORIAL_Y_SESGOS.md`**
+ **`config/editorial_diversity.json`**. En resumen:

- Preguntar **"¿ya contamos algo parecido de esta misma manera?"**, no solo "¿ya hablamos
  de este servicio?".
- **Antes de redactar** se asigna a cada post: arquetipo (6–8 por mes), `hook_type`,
  `cta_type`, pain point y claim. El texto se escribe **con esas restricciones**.
- **CTA por intención** (contacto, conversación técnica, profundización, conocimiento,
  evento, descarga, descubrimiento). **`contact` NO es default.** No repetir textual.
- Narrativa **desde la necesidad del cliente**, valor técnico **antes** que lo comercial;
  no todo post termina en venta explícita.
- **Longitud: referencia 900 caracteres, flexible desde 19-10-2026 (objetivo 820–880), 1–2 emojis por párrafo máximo.**
- Octubre **no se regenera** (cerrado manualmente); su versión definitiva debe
  consolidarse como memoria.

## ✅ Checklist de aprendizajes para planificar cada mes (desde diciembre 2026)

Destilado de las rondas MKT de septiembre a noviembre 2026 (detalle y fechas en la bitácora). Octubre y
noviembre ya están publicados/programados y **no se retocan**; lo que sigue es lo que esos meses dejaron
como regla para **diciembre en adelante**. Se recorre **antes** de presentar la grilla a MKT.

**A. Antes de proponer temas**
1. Archivar el mes anterior en `content/archive/` y leer los **2 meses previos**: no repetir
   `knowledge_id`, subtema, claim, pain point, gancho ni CTA (09-04 · 30-09).
2. Revisar `config/efemerides.json` (incluye saludos de Navidad y Año Nuevo), el banco de temas
   (`config/topic_bank/`) y Sales Intelligence (`knowledge/sales_intelligence/`).
3. Si una célula no tiene material fresco (hoy **Lab Minero Digital** y **Hospitalaria**), **pedir insumos**
   a MKT o hacer menos posts; no rellenar con versiones parecidas (09-04 · 05-10).
4. Excluir lo bloqueado: control de productividad (KB-IOM-019/020), Centro Cultural GAM como caso,
   contenidos de charlas de David Silva, asesoría a la inspección de obras (AITO); no nombrar expositores ni charlas de origen (30-09 · 05-10 · 14-10).
5. Un caso/proyecto nombrado va en **un solo post por mes**, y todo post que nombre un caso se marca
   para que MKT valide su sensibilidad **antes** de redactar (30-09 · 01-10).

**B. Tabla de asignación (antes de redactar, la aprueba MKT)**
6. Por post: arquetipo · hook_type · cta_type · pain point · claim, con los límites de
   `config/editorial_diversity.json` (6–8 arquetipos, sin repetir en posts consecutivos, `contact` no es
   default). Después correr `python -m idiem.editorial_qa --month AAAA-MM`.

**C. Al redactar el copy**
7. Explicar **por qué** importa (la necesidad del cliente), no solo nombrar el servicio (relaves, 05-10).
8. Nombrar el servicio **exacto** que presta IDIEM, sin ampliarlo: IDIEM **instrumenta** el tranque para su
   monitoreo, no "monitorea" (19-10); en SIM el monitoreo va al final (05-10); HDPE: los ensayos
   "verifican el cumplimiento del proyecto"; la soldadura se inspecciona y se califica al soldador.
9. En cumplimiento normativo, hablar de **detectar brechas**; nunca insinuar que la norma se puede saltar (09-07).
10. Ítems `NAME_ONLY_DO_NOT_EXPAND` o con poco detalle en 2A.2 van a alto nivel, sin inventar ensayos ni
    cifras (09-04). Sin superlativos ni rankings (Triaxial, 09-03).
11. **Las ediciones de MKT son "oro":** se respetan literal. El largo de 900 es **referencia flexible**
    (MKT 19-10-2026): se puede escribir más o menos si el contenido lo necesita. Si un copy pasa de 900,
    se deja anotado el motivo (`length_override`) para que el QA lo registre; no recortar textos de MKT.

**D. Al diseñar la pieza**
12. Bajadas de carrusel con valor (por qué importa · qué aporta IDIEM · qué gana el cliente), no
    repetir el título (01-10).
13. La foto debe mostrar **el objeto real del servicio** (peritaje de componentes → piezas o ensayos
    mecánicos, no estructura ni pavimento; 09-24). Fotos de la librería de Drive; no repetir una foto usada
    en los **3 meses previos** (el QA lo avisa); anillo rojo al lado contrario de la cara (09-04); al dividir
    una foto, igualar la exposición de ambas mitades (09-21). Sin siglas de célula en la pieza.
14. Videos: solo con la skill `video-carrusel-idiem` (el método propio fue rechazado, 13-10).

**E. Antes de programar**
15. **Ningún post se programa con un `VERIFY` abierto.** El #8 de noviembre quedó programado con la vigencia
    de ISO 9001:2015 sin confirmar; desde diciembre, el VERIFY se cierra con MKT o el dato sale del copy.
16. Workstation con el historial de cambios poblado en cada ronda (09-04); cada ronda MKT se registra en la
    bitácora y, al cerrar el mes, se archiva con estados (`design_system/archive_month_plan.py`).

## Estilo y tono del copy (voz de marca, según ediciones aprobadas por MKT)

El equipo de MKT (Kike) es la autoridad de tono. Patrones observados en sus reescrituras
(**válidos como voz, NO como plantilla fija** — ver sección anterior):

- **Largo: referencia de 900 caracteres, flexible** (fijado como regla dura el 2026-08-31; **flexible desde
  el 2026-10-19**, MKT: "podemos hacer más o menos caracteres si es necesario"). Cuenta el copy completo
  (gancho + desarrollo + CTA + hashtags, incluidos emojis y saltos). Objetivo 820–880 (MKT 30-09-2026);
  si se supera 900, registrar el motivo. Excepción: posts de evento con URL (ver `config/editorial_diversity.json`).
- **Estructura** *(solo arquetipo `problem_impact_capability`, no default)*: gancho →
  problema/contexto → solución **"En #IDIEM ..."** → cierre de valor ✅ → CTA → hashtags.
  Los demás arquetipos ordenan el relato distinto.
- **Listas**: cuando hay entregables/beneficios, usar viñetas con `*` (un ítem por
  línea), como en el post de programación de obra.
- **Emojis**: sí, pero **medidos y temáticos** (🏥 🔊 🔥 🔍 🛡️ 📐 ♻️ 🩺 ✅ 📩 👉 🏗️ 🇨🇱).
  Uno o dos por párrafo, nunca decorativos en exceso.
- **#IDIEM**: se usa como mención inline dentro del cuerpo ("En #IDIEM realizamos…").
  Kike alterna a veces con "En IDIEM" en prosa; respetar su texto literal cuando lo
  entrega.
- **Sin superlativos** (GR-04): nada de "líderes", "los mejores", "#1", etc.
- **Hashtags**: `#IDIEM` + 4–6 temáticos (p. ej. #Minería #Ingeniería #Seguridad).
- **CTA**: se elige por **intención** (`cta_type`) y se redacta cada vez. ⛔ Las fórmulas
  "Contáctanos y conversemos sobre tu caso" y "Contáctanos a través de nuestros canales
  oficiales" quedaron **sobreusadas** en octubre: no usarlas como default ni repetirlas.
- **Registro**: profesional, técnico pero accesible, orientado al beneficio y a la
  evidencia técnica.

## Reglas de diseño (piezas)

- **NO** incluir las siglas de célula (IHA, IOM, etc.) en la pieza: es manejo interno.
- **Carruseles** → diseño **foto de fondo (Plantilla 02)**: portada + intermedias
  numeradas (ícono + palabra en caja roja + bajada) + cierre de marca. NO diseño plano.
- **Textos de las láminas de carrusel (MKT, 01-10-2026):** el título puede ser una etiqueta corta, pero
  la **bajada debe decir algo relevante**: por qué importa (riesgo/necesidad del cliente), qué aporta
  IDIEM y qué gana el cliente (propuesta de valor), con el mismo nivel del copy del post. ⛔ No sirve
  repetir el título con otras palabras ni listar el componente sin su valor. Si hay un caso, la lámina
  del caso explica la participación de IDIEM. Todo sigue trazando a 2A.2 (sin inventar beneficios ni
  resultados; con `USE_WITH_MATIZ` el valor se expresa como propósito, sin ampliar el alcance).
- **Videos (MKT 13-10-2026) — OBLIGATORIO usar la skill `.claude/skills/video-carrusel-idiem/`** (leer su
  SKILL.md). Pipeline fijo: config JSON → `build.py` → `music.py` (si se pide) → `render.py` (cuadro a cuadro
  con `window.seek(t)`) → `qa.py`. Reglas clave:
  - ⛔ Nunca animar las láminas como imágenes planas (zoom/fundido del PNG), ni grabar pantalla en tiempo
    real, ni IA generativa de video, ni fuentes de reemplazo. Se reconstruye en capas: foto limpia original
    de la librería + textos reales en HTML (Montserrat incrustada) + logo SVG.
  - Textos **literales** de las láminas aprobadas, con sus mismos saltos de línea; no resumir ni reescribir.
  - Movimiento sobrio de marca: un solo fondo con zoom lento 1,00→1,10 y velo; entradas expo-out, salidas
    cubic-in; títulos palabra a palabra desde máscara; caja roja que se barre; íconos Lucide trazo a trazo;
    párrafo línea a línea; logo y número persistentes; cierre que **termina sobre el logo**.
  - Tiempos: portada 4 s · láminas 5,5–9 s (`1,6 + palabras/4,4`) · cierre ≈ 6 s; cortes en múltiplos de
    0,5 s (120 BPM). Si supera ~45 s, avisar a MKT antes de renderizar (no recortar textos).
  - Música solo si se pide: pista original de `music.py` (−17 LUFS, pico ≤ −1 dBTP). Entregar MP4 con y sin
    música y decir que la música **requiere aprobación auditiva** de una persona.
  - QA obligatorio: chequeos técnicos de `qa.py` + revisar a ojo `hoja_transiciones.jpg` y `comparacion.jpg`.
  - Entrega: `video.mp4`, `video_musica.mp4`, `video.html` y nota de diferencias con la pieza aprobada.
- **Estáticos** → formato **Servicios (Plantilla 01)**: círculo rojo con servicio +
  mensaje clave + baseline.
- **Fotos**: preferir **fotos propias de faena** de la librería de IDIEM cuando existan;
  Adobe Stock (colección libre) solo como sustituto cuando no hay foto propia adecuada.
  Cada foto traza a su origen (Drive / Adobe Stock #id).
- **Sellos/logos de certificación** (p. ej. Green Hospital) van como overlay en la
  esquina inferior derecha, sin tapar el círculo ni el logo IDIEM, manteniendo la
  foto de fondo.

## Efemérides clave del sector (calendario de contenidos)

Al planificar la grilla de **cada mes**, revisar `config/efemerides.json` y sumar una
pieza conmemorativa si el mes cae en una de estas fechas (adicional a los 12 posts base):

| Fecha | Efeméride | Líneas IDIEM | Traza |
|---|---|---|---|
| 18 sep | Fiestas Patrias (Chile) | Saludo institucional patrio | **NO** traza → saludo general |
| 5 oct | Día Mundial de la Arquitectura | Revisión de proyectos, BIM (IPR/IHA) | puede trazar a knowledge_id |
| 13 oct | Reducción del Riesgo de Desastres | **Fecha fuerte:** vulnerabilidad/integridad estructural, resiliencia, geotecnia, monitoreo, **riesgo/peritaje de incendios** y **continuidad operacional** (IOM/IPR/LMD) | puede trazar a knowledge_id |
| 17 oct | Día del Geólogo (Chile) | Geotecnia y rocas, mecánica de suelos (LMD/IOM) | puede trazar a knowledge_id |
| 26 nov | Transporte Sostenible | INFRA CRÍTICA TRANSPORTE (**CONTENT_GAP**) | **NO** técnico → institucional general |
| 5 dic | Día Mundial del Suelo | Mecánica de suelos, ensayos de suelos, geotecnia (LMD/IPR/IOM) | puede trazar a knowledge_id |
| 25 dic | Navidad | Saludo institucional (cierre de año) | **NO** traza → saludo general |
| 31 dic | Año Nuevo | Saludo institucional (proyección) | **NO** traza → saludo general |

Regla: mismas cautelas que un saludo — las que no tienen respaldo técnico en 2A.2 se
mantienen institucionales/generales; **Transporte Sostenible** no puede afirmar
capacidades técnicas (la célula ICT no tiene conocimiento activo).

## Piezas institucionales (saludos)

- Los **saludos** (Fiestas Patrias, etc.) son piezas conmemorativas que **NO trazan a
  un knowledge_id**. Se mantienen **generales**: sin afirmar proyectos, fechas ni
  cifras específicas de IDIEM que no estén respaldadas por la librería 2A.2.
- Mensaje válido: aporte general de "ciencia e ingeniería al desarrollo de la
  infraestructura del país". Si se quieren hitos concretos (año de fundación, obras
  emblemáticas), deben confirmarse contra la librería antes de publicarse.

## Memoria de contenidos por mes (archivo)

El contenido publicado de cada mes se **congela** en `content/archive/AAAA-MM.json` (+ `.md`
legible). **Es el archivo mensual consolidado ÚNICO** (integración de ramas, 19-10-2026): reemplaza a
`state/consolidated/`, y `state/published_ledger.json` es solo un índice derivado de él
(`idiem.ledger.build_ledger_from_archive`). Sep/oct se generan con `design_system/archive_month.py`;
desde noviembre, con `design_system/archive_month_plan.py` (lee `state/plans/AAAA-MM_*.json`). Cada archivo guarda, por pieza: célula, subtema,
ángulo editorial, formato, `knowledge_id`/evidencia, copy final, foto (id + traza) y estado; más
un **índice de dedup** (knowledge_ids, subtemas, ángulos y distribución de células usadas).

Regla de uso al planificar un mes nuevo:
1. **Archiva** el mes anterior si aún no está (`archive_month.py --month AAAA-MM --published-all`).
2. **Lee** los archivos previos (al menos el mes inmediatamente anterior) como contexto.
3. **No repitas** los mismos `knowledge_id`, subtemas ni ángulos del mes anterior; rota células y
   temas para que el feed no se sienta repetido.
4. **Actualiza hechos** si algo cambió respecto de lo ya publicado (y refleja la corrección aquí).
5. **No repitas claims, ganchos ni CTAs** del mes anterior (aprendizaje MKT 2026-09-04). Rotar el
   `knowledge_id` no basta: dos posts se "sienten iguales" si repiten el mismo problema-solución,
   la misma evidencia o el mismo CTA. Variar el **CTA** (desde nov-2026: por intención, `cta_type`, según
   `docs/10_ESTRATEGIA_EDITORIAL_Y_SESGOS.md`; no repetir textual), variar el **gancho** (fecha, escenario,
   pregunta, dato) y no reusar el mismo claim técnico. Si 2A.2 no tiene material fresco bien
   documentado, preferir **menos posts sólidos** (o pedir insumos) antes que rellenar con versiones
   parecidas.

Meses archivados: **2026-09** (13 piezas, publicado) · **2026-10** (13 piezas, cerrado por MKT;
copy definitivo de la workstation + huellas asignadas) · **2026-11** (12 piezas: #4 publicado, resto
programado al 19-10-2026).

## Bitácora de correcciones

- **2026-08-24** — Post 1 → foto acuerdo/ejecutivos; post 3 → foto pixelada cambiada
  (casco+tablet); post 9 → hospital distinto; post 11 → edificio en construcción.
- **2026-08-28** — Ronda MKT (Kike):
  - Posts 1, 2, 5, 7: copy reescrito (versiones de MKT como oro).
  - Post 2 (carrusel): orden de láminas — incendios antes que fallas estructurales.
  - Post 5: quitar "Salud sin Daño"; Green Hospital = certificación propia; ISO 50001;
    overlay del sello Green Hospital (esquina inf-der), misma foto de fondo.
  - Post 7: foto propia `equipo_acustica_FA-1`; sumar "estudio de impacto" y "D.D. 14/24".
  - Post 8: foto propia `Tuberia_HDPE_END_ACERO4`.
  - Post 9: foto de acuerdo/apretón de manos (contexto profesional).
  - Post 11: mantener foto actual (Costanera).
  - Post 12: la soldadura se inspecciona por muestreo (no "cada soldadura verificada");
    se califica al soldador, no la soldadura.
  - Nuevo post 13: saludo Fiestas Patrias (institucional).
- **2026-08-31** — Ronda MKT (Kike), aplicada desde el ws-state de la workstation:
  - Post 3: copy → "pocas cosas **afectan** tanto" (antes "duelen"); foto propia de
    librería `generica_planos_arquitectos_casco` (arquitectos revisando planos + cascos).
  - Post 6: foto propia de librería `estructura_andamio_minera` (andamiaje industrial/minero;
    reemplaza vigas de acero).
  - Post 9: foto propia de librería `generica_ejecutivos_casco_acuerdo` (apretón de manos /
    acuerdo, con casco y planos; reemplaza la versión "construccion").
  - Post 10: copy → "una falla en un **activo** crítico" (antes "equipo rotativo").
  - Post 11: copy reescrito (versión MKT como oro) — "la calidad debe demostrarse con
    evidencia técnica"; se lista control técnico (suelos, hormigones, asfaltos, END en
    soldaduras), resistencia al fuego y peritajes; acreditación INN + Registro Oficial MINVU
    "dentro de sus alcances" + ISO 9001.
    - **Nota CTA:** MKT escribió "Conversemos en **idiem.cl** 👉" (sin `https://`). Se respetó
      su texto literal (MKT es la autoridad de tono). El estándar sigue siendo
      `https://idiem.cl`; confirmar con Kike si debe normalizarse.
  - Fotos: son fotos propias de la **librería de Drive de IDIEM** (no stock ni IA); trazan a
    su archivo por `viewUrl`. Bajadas, reescaladas (lado corto ≈1200px, JPEG q86) e incrustadas
    en `assets/month/pNN.jpg`.
  - **Nueva regla dura: copy ≤ 900 caracteres** (ver sección "Estilo y tono"). Al fijarla,
    quedaron **sobre el límite** los posts **1 (1075), 2 (1013), 5 (1028)** y el **4 (900,
    justo)** — son copies aprobados por MKT en rondas previas. Pendiente: recortarlos con
    visto bueno de Kike (no se tocan sin su aprobación por ser "oro").
- **2026-09-03** — **Contenidos de octubre 2026** (12 posts, artefacto nuevo):
  - Memoria de contenidos aplicada: se leyó `content/archive/2026-09.json` y se excluyeron sus
    12 `knowledge_id`. Mix por célula **IOM5 / IPR4 / LMD2 / IHA1** (aprobado por Kike) para poder
    rotar todos los subtemas: IHA solo tiene "ingeniería contractual" fresca y LMD solo "geotecnia
    y rocas" fresca, así que se apoyó en IOM/IPR (canteras profundas).
  - **Efemérides dentro de los 12** (trazan a 2A.2): Día de la Arquitectura (5-oct, IPR-018
    sustentabilidad), Reducción del Riesgo de Desastres (13-oct, IOM-047 integridad, carrusel) y
    Día del Geólogo (17-oct, LMD-004 geotecnia). El del Geólogo se redactó **como saludo** a la
    profesión + contenido de mecánica de rocas (pedido de Kike).
  - **Geotecnia / Triaxial (LMD-004, LMD-007):** copy SIN superlativos ni rankings — 2A.2 bloquea
    "único de Chile y Sudamérica", "el más grande del mundo", "tercero a nivel mundial", "primer y
    mayor laboratorio", "pioneros". Sí es publicable el núcleo técnico ("Triaxial para grandes
    partículas, desarrollado con ingeniería propia"). Confiabilidad (IOM-065): sin "reconocido en
    Chile y el mundo / rigor y excelencia".
  - **Ronda 2 (Kike):** se reemplazó el post de incendios (IPR-019) por **peritaje de componentes
    metálicos (IPR-002)** para eliminar el solape de subtema con septiembre; quedan **4 carruseles**
    (integridad/RRD, Triaxial, componentes metálicos, cumplimiento normativo); y **todos los posts
    llevan foto** de la librería de Drive de IDIEM.
  - Los 12 copies pasan `ingest_draft` sin violaciones y todos ≤900 caracteres (rango 638–861).
  - **Fotos (todas de la librería de Drive de IDIEM):** una por pieza, bajada y reescalada
    (~1200px lado corto, JPEG q86) a `assets/month/2026-10/pNN.jpg`. Trazan por `viewUrl` en
    `PHOTO_SUB`. Ej.: puentes → `estructuras_peritajes_puente_cortez` (coincide con el estudio del
    Puente Cortés citado en el copy); Triaxial → `Equipo_trixial_gigante`. Las de septiembre se
    preservaron en `assets/month/2026-09/`.
  - **Nota técnica:** `COPY` pasó a estar **keyed por `knowledge_id`** (no por `content_id`), para
    que el copy no se rompa cuando cambian los `seq` al reordenar/insertar piezas.
- **2026-09-04** — **Ronda MKT (Kike): octubre demasiado parecido a septiembre.** Kike marcó
  cambios en la workstation y pidió cortar posts/claims/CTAs similares entre meses. Aplicado:
  - **CTAs y ganchos diversificados** en los 12 (rotando las 3 variantes de marca; septiembre
    usaba casi siempre "¿Necesitas…? Conversemos en idiem.cl 👉"). Ver regla nueva arriba.
  - **Fuera por similitud:** contractual (IHA-002, ya trabajado en sept), integridad estructural
    (IOM-047, casi calcaba el peritaje estructural de sept) y confiabilidad se replanteó.
  - **Nuevos temas frescos:** control de productividad (IOM-019) y tecnología/I+D del hormigón
    (IOM-017). **OJO:** 2A.2 solo los **nombra** (sin detalle), así que sus posts van a **alto
    nivel**, sin inventar ensayos ni cifras. Confiabilidad (IOM-065) se mantuvo con ángulo de
    **equipo multidisciplinario** (metalurgia/mecánica/química), distinto del peritaje de
    componentes (IPR-002).
  - **Día del Geólogo (LMD-004):** reescrito como **saludo institucional** (importancia de los
    geólogos), sin detallar servicios.
  - **Mix del mes: IOM6 / IPR4 / LMD2** (IHA queda fuera: su única cantera fresca era contractual).
    **4 carruseles:** Triaxial, componentes, cumplimiento y rehabilitación (4 etapas).
  - **Límite de inventario 2A.2 (importante):** tras septiembre (12) + octubre, la biblioteca casi
    no tiene subtemas nuevos bien documentados. Para meses futuros conviene **pedir insumos** a
    IDIEM (hormigón, productividad, etc.) o planificar **menos posts** por mes.
  - **Fotos:** no existía `generica_geologo` en la librería → se usó `sondaje_relave` (geología de
    terreno); `generica_estructura_acero` no descargaba → se usó `generica_idiem_vigas_acero`
    (mismo tema, vigas de acero).
- **2026-09-04** — **Ronda de fotos exactas (Kike) + historial de cambios.** Kike subió
  `generica_geologo` al Drive y pidió aplicar las fotos exactas que había marcado.
  - **Aplicadas:** geólogo (LMD-004, seq 3) → `generica_geologo`; tecnología de la construcción
    (IPR-016, seq 5) → `generica_arquitectura-construccion-bim2`. Bajadas del Drive, reescaladas y
    horneadas a `assets/month/2026-10/p03.jpg` y `p05.jpg`; `PHOTO_SUB` actualizado.
  - **Anillo rojo configurable por post (`SIDE` en `gen_workstation.py`):** el geólogo usa el anillo
    a la **derecha** (59%) para dejar la **cara despejada** (pedido explícito: "el círculo rojo no
    debe tapar a la persona"). Regla: cuando el sujeto llena el encuadre, mover el anillo al lado
    contrario a la cara.
  - **Historial de cambios (`APPLIED_LOG`) poblado — OBLIGATORIO.** Cada tarjeta debe mostrar el
    bloque "Historial de cambios aplicados (N)" como en septiembre. Octubre había quedado vacío
    (el `<details>` no se renderiza si el log está vacío); ahora las 12 tarjetas lo llevan. **Todo
    artefacto de workstation debe incluir el historial poblado.**
  - **`generica_estructura_acero` (8,28 MB) NO descargaba** por el conector de Drive: la sesión
    expira en cada intento (~10 intentos). Los archivos livianos sí bajan (geólogo 4 MB, BIM
    0,5 MB). Regla operativa: **archivos de Drive > ~6 MB fallan; pedir versión comprimida
    (≤5 MB).** **Resuelto:** Kike re-subió `generica_estructura_acero_low.JPG` (1,57 MB); bajó sin
    problema y quedó aplicada en **#12 (rehabilitación)** — celosía de acero galvanizado (reemplaza
    a `generica_idiem_vigas_acero`).
  - **DB del tablero:** notas de foto aplicadas (geólogo, BIM, estructura_acero) borradas para
    limpiar los flags.
- **2026-09-07** — **Ajustes finos (Kike) sobre el tablero.**
  - **#3 Geólogo (gráfica):** el título central pasa a **"Feliz día del Geólogo"** y se **retira el
    kicker** "Día del Geólogo" (antes: kicker "Día del Geólogo" + "Gracias, geólogos.").
  - **#5 Tecnología de la Construcción (foto):** cambiada de BIM a **`generico_construccion_edificio_obra`**
    (obra en altura, grúas torre). Baja bien del Drive (3,3 MB).
  - **#9 Cumplimiento normativo (copy):** gancho **reformulado** — el original ("Incumplir la normativa
    no siempre se nota…") daba a entender que se puede incumplir. Nuevo foco: una **brecha** puede pasar
    desapercibida hasta que una auditoría/falla la deja en evidencia. **Regla:** en cumplimiento, hablar
    de detectar brechas/no conformidades, nunca insinuar que saltarse la norma es viable.
- **2026-09-07** — **Refactor de diversidad editorial.** Se agregó el motor de diversidad
  (ver `docs/13_MOTOR_DIVERSIDAD_EDITORIAL.md`): huella editorial por pieza, novedad vs historial,
  historial en el drafting, QA editorial (PASS/WARNING/FAIL) y cobertura por célula. Objetivo:
  no repetir **claim/pain/hook/arquetipo/CTA** aunque cambie el `knowledge_id`. Umbrales en
  `config/editorial_diversity.json`. **Factualidad manda sobre diversidad** (sin inventar; Sales
  Intelligence/performance no son hechos; CONTENT_GAP intacto).
  - **Longitud — fuente de verdad:** ahora es EJECUTABLE en `config/editorial_style.json → length`
    (en **caracteres**: tope duro 900; el rango preferido 650-850 de esta fecha quedó **reemplazado** por el objetivo 820–880 aprobado por MKT el 30-09-2026). Se retiró la regla en palabras (110-170)
    que colisionaba. **Si este documento discrepa con ese archivo, manda el archivo.**
  - **Diagnóstico octubre (QA automático):** el sistema detecta solo la concentración editorial —
    CTA `contact` ×9/12, arquetipo `problem_solution` ×5, hook `insight` ×5, visual `infrastructure`
    ×5, solo 4 arquetipos distintos. Aprendizaje: **variar el `cta_type` (no solo la frase) y rotar
    arquetipos/hooks** en la próxima grilla. Reporte fijo en `content/archive/2026-10.editorial_qa.md`.
- **2026-09-21** — **Ronda MKT (Kike) sobre el tablero de octubre — posts seleccionados.**
  - **#9 Cumplimiento normativo (carrusel, lámina 02):** el cuerpo pasa a **"Verificamos el
    cumplimiento frente a marcos normativos aplicables."** (antes "marcos estructurales") y el título
    de la lámina se ajusta a **"Marcos normativos"** para no dejar título estructural con cuerpo
    normativo. Sigue el foco de detectar brechas, sin insinuar que saltarse la norma sea viable.
  - **#13 Acústica (carrusel):** portada con **nuevo título** —"Conoce las nuevas exigencias
    acústicas para la construcción y locales de ocio nocturno."— (se baja el cuerpo del titular con
    `title_size` porque el texto es largo). **Foto de fondo DIVIDIDA en TODAS las láminas** (cierre
    incluido, con velo reforzado para legibilidad): mitad izquierda `generica_obra_construccion_edificio`
    (obra), mitad derecha `ruido_acustica_discotec` (ocio nocturno). Se compone un `p13.jpg` 1080²
    con las dos fotos de librería y se retira la foto por-lámina anterior (`p13_s3`). Regla de diseño
    reutilizable: `CIERRE_PHOTO` habilita foto en el cierre de un carrusel concreto sin tocar los demás.
  - **#13 Acústica (foto, 2ª pasada):** la mitad derecha (`ruido_acustica_discotec`) se veía muy
    oscura bajo los velos; se **aclara** al componer `p13.jpg` (brillo ×1.42, contraste ×1.06,
    saturación ×1.05); la mitad izquierda (obra) se mantiene sin tocar. Aprendizaje: al dividir una
    foto, igualar la exposición de ambas mitades porque los velos del carrusel oscurecen aún más.
- **2026-09-24** — **Ronda MKT (Kike) sobre el tablero de octubre.**
  - **#8 Peritaje de componentes metálicos (carrusel):** foto cambiada a **`ensayo_aceros2`** (técnico
    IDIEM mecanizando una probeta metálica). La anterior (`planta_aceros`) era una maestranza de acero
    estructural y no calzaba: las fallas peritadas son de **componentes mecánicos**. La lámina 03
    "Pavimento en autopistas" se reemplaza por **"Evidencia para decidir"** (frase ya aprobada del copy;
    KB-IPR-002 sólo respalda peritajes a pernos, ejes, engranajes y tuberías + pavimento, así que no se
    agregan métodos nuevos) y se retira también la mención a pavimentos del copy. **Regla:** en peritaje
    de componentes, la foto debe mostrar piezas/ensayos mecánicos, no estructura ni pavimento.
  - **#1 Ingeniería contractual (copy):** se incorporan las ediciones de MKT hechas en el tablero:
    "inconsistencias durante la ejecución de la obra" y viñeta "Diagnóstico contractual y de ejecución
    de la obra.".
- **2026-10-01** — Ronda MKT noviembre (workstation):
  - Fotos elegidas por MKT: #1 `tranque_caren4`, #2 `aeroporto_stgo`, #4 `generica_hospital`,
    #7 `generico_modelado_estructura`, #10 `Tuberia_HDPE_END_ACERO1`, efeméride `metro_stgo`.
  - #2: carrusel y copy reformulados hacia "laboratorio en obra" con el caso del aeropuerto.
  - #6: sin aeropuerto → servicio genérico de ingeniería contra incendios (ancla KB-IPR-019).
  - #5: edición de copy de MKT (salto de línea tras el gancho).
  - Carruseles #2, #5 y #10: bajadas reescritas con relevancia y propuesta de valor (pedido MKT:
    "los mensajes del carrusel no dicen nada relevante"). #7 foto → `modelado_bim`.
- **2026-10-05** — Ronda MKT noviembre (2): #1 profundizado (24/7, crece, razones del monitoreo);
  #5 SIM con monitoreo al final (lámina propia) + copy de MKT; #9 productividad → revisión de
  cumplimiento normativo (KB-IOM-016); #10 lámina 2 ajustada. Aprobados: 2, 3, 6, 7, 8, 11 y efeméride.
- **2026-10-13** — #5 SIM: primer video (método propio de zoom/fundido sobre PNG) **rechazado por MKT**; se
  regeneró con la skill `video-carrusel-idiem` (38 s, en capas, con y sin música). Ese método queda vigente.
- **2026-10-14** — MKT comparte 6 presentaciones de especialistas (incendio en industria/minería/hospitales,
  controversias hospitalarias, vulnerabilidad estructural y ENE en hospitales, RIC en salud). Registradas
  en `docs/11_FUENTES_EXPERTAS_Y_BANCO_DE_TEMAS.md` con 22 temas candidatos (17 de Salud/IHA).
- 2026-10-14 · Post especial de reconocimiento (Leonardo Massone, Top 2% más citados, Ingeniería Civil):
  pieza institucional fuera de grilla, no traza a knowledge_id. Plantilla `design_system/gen_post_reconocimiento.py`
  (data en `config/especiales/`). Los rankings de terceros sobre personas se informan tal cual, sin superlativos
  sobre IDIEM (GR-04); la fuente de la lista (Stanford University y Elsevier) va en la gráfica — confirmada por MKT 15-10.
- **2026-10-19** — #1 relaves: **el servicio IDIEM es la instrumentación del tranque PARA su monitoreo, no
  el monitoreo.** En copy y gráfica, IDIEM instrumenta/habilita el monitoreo a distancia; nunca "monitoreamos".
- **2026-10-19** — Noviembre: **todas las piezas programadas**; **#4 (ingeniería contractual, Salud) publicado**
  con el copy final de MKT (1083 caracteres: excepción al tope registrada, pendiente confirmar con MKT si el
  tope de 900 sigue siendo regla dura). Integración de ramas: memoria única en `content/archive/` y taxonomía
  única de MKT en el motor de diversidad (ver `docs/13_MOTOR_DIVERSIDAD_EDITORIAL.md`).
- **2026-10-19** — Decisiones MKT para todos los meses: (1) el largo de 900 caracteres pasa a ser **referencia
  flexible** ("más o menos si es necesario"; el QA avisa y se registra el motivo); (2) saludos, efemérides y
  reconocimientos usan `institutional_or_occasion`, fuera del conteo de arquetipos; (3) las piezas nuevas se
  renderizan con **Montserrat incrustada** (`design_system/brand_fonts.py`, pesos 400–800).
- **2026-10-19** — **Elección de herramienta de video** (ver `CLAUDE.md` § Videos para LinkedIn): carrusel/post
  aprobado → skill `video-carrusel-idiem` (sin cambios); formatos que esa skill no cubre (video grabado,
  subtítulos, cifras/mapas animados, 9:16 o 16:9) → Remotion (repo privado `motion-graphics-ia`). Prueba:
  el carrusel SIM portado a Remotion difiere < 0,1 % de píxeles del pipeline oficial. Primer video de
  cada formato nuevo pasa por MKT. Verificación de licencia de Remotion omitida por decisión del usuario
  (19-10-2026); no bloquea la publicación.
- **2026-10-19** — **Cruce sitio web vs 2A.2** (`docs/12_CRUCE_WEB_VS_2A2.md`): 2A.2 prevalece sobre el sitio.
  MKT decide: (1) **VERIFY = disponible**: los servicios del sitio se pueden planificar y redactar marcados
  VERIFY; se validan al aprobar el post que los usa o con las correcciones de MKT; (2) productividad **no se
  bloquea**: activa en VERIFY; (3) mediciones eléctricas de pisos conductivos (NCh4/2003) → célula Infra
  Hospitalaria, disponible en VERIFY.
- **2026-10-19** — **Formato de entrega (usuario):** cada mes lleva **su propio artefacto workstation**; los posts
  nunca se entregan como texto en el chat. Diciembre: https://claude.ai/artifact/LQbvx2h518ZtzvDppGHc1m
  (generador `design_system/gen_month_ws.py`, ahora con varias piezas extra por mes y videos por producir).
