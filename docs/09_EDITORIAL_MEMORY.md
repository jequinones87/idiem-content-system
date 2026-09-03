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

### Ingeniería contractual (célula IHA)
- Ámbitos que IDIEM atiende de forma explícita en el sector Salud: **análisis de
  programación**, **análisis ante término anticipado de contrato**, respaldo técnico
  para gestión de contratos y **reclamaciones**.

## Estilo y tono del copy (voz de marca, según ediciones aprobadas por MKT)

El equipo de MKT (Kike) es la autoridad de tono. Patrones observados en sus reescrituras:

- **Largo máximo: 900 caracteres (REGLA DURA).** Ningún copy publicable puede superar los
  **900 caracteres**, contando el cuerpo completo (gancho + desarrollo + CTA + hashtags,
  incluidos emojis y saltos de línea). Regla fijada por MKT el **2026-08-31**. Si un borrador
  excede, hay que **recortar antes de aprobar** (no es negociable). Objetivo práctico: apuntar
  a ~820–880 para dejar margen.
- **Estructura**: gancho con emoji → párrafo de problema/contexto → párrafo de
  solución que empieza con **"En #IDIEM ..."** (o "En IDIEM ...") → cierre de valor
  con ✅ → **CTA** (pregunta + "Conversemos en https://idiem.cl 👉" o "Contáctanos a
  través de nuestros canales oficiales") → **línea de hashtags**.
- **Listas**: cuando hay entregables/beneficios, usar viñetas con `*` (un ítem por
  línea), como en el post de programación de obra.
- **Emojis**: sí, pero **medidos y temáticos** (🏥 🔊 🔥 🔍 🛡️ 📐 ♻️ 🩺 ✅ 📩 👉 🏗️ 🇨🇱).
  Uno o dos por párrafo, nunca decorativos en exceso.
- **#IDIEM**: se usa como mención inline dentro del cuerpo ("En #IDIEM realizamos…").
  Kike alterna a veces con "En IDIEM" en prosa; respetar su texto literal cuando lo
  entrega.
- **Sin superlativos** (GR-04): nada de "líderes", "los mejores", "#1", etc.
- **Hashtags**: `#IDIEM` + 4–6 temáticos (p. ej. #Minería #Ingeniería #Seguridad).
- **CTA**: variantes válidas — "📩 ¿Necesitas…? Contáctanos y conversemos sobre tu
  caso." / "¿Necesitas…? Contáctanos a través de nuestros canales oficiales 👉
  https://idiem.cl" / "¿…? Conversemos en https://idiem.cl 👉".
- **Registro**: profesional, técnico pero accesible, orientado al beneficio y a la
  evidencia técnica.

## Reglas de diseño (piezas)

- **NO** incluir las siglas de célula (IHA, IOM, etc.) en la pieza: es manejo interno.
- **Carruseles** → diseño **foto de fondo (Plantilla 02)**: portada + intermedias
  numeradas (ícono + palabra en caja roja + bajada) + cierre de marca. NO diseño plano.
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
legible) con `design_system/archive_month.py`. Cada archivo guarda, por pieza: célula, subtema,
ángulo editorial, formato, `knowledge_id`/evidencia, copy final, foto (id + traza) y estado; más
un **índice de dedup** (knowledge_ids, subtemas, ángulos y distribución de células usadas).

Regla de uso al planificar un mes nuevo:
1. **Archiva** el mes anterior si aún no está (`archive_month.py --month AAAA-MM --published-all`).
2. **Lee** los archivos previos (al menos el mes inmediatamente anterior) como contexto.
3. **No repitas** los mismos `knowledge_id`, subtemas ni ángulos del mes anterior; rota células y
   temas para que el feed no se sienta repetido.
4. **Actualiza hechos** si algo cambió respecto de lo ya publicado (y refleja la corrección aquí).

Meses archivados: **2026-09** (13 piezas, publicado).

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
  - **Solape a vigilar:** "Ingeniería contra incendios" (seq3, IPR-019, preventivo en edificación
    pública) comparte etiqueta de subtema con el peritaje de incendios minero de septiembre
    (IOM-011); célula y ángulo son distintos (preventivo vs forense) y es pertinente a la semana
    RRD. Alternativa cero-solape ofrecida a Kike: IPR-002 (componentes metálicos) o IPR-023
    (diagnóstico de obras ejecutadas).
  - Los 12 copies pasan `ingest_draft` sin violaciones y todos ≤900 caracteres (rango 638–871).
  - **Fotos:** octubre parte sin fotos (campo de marca sólido / carrusel en campo oscuro); Kike
    elegirá fotos de la librería de Drive por pieza. Las de septiembre se preservaron en
    `assets/month/2026-09/`.
