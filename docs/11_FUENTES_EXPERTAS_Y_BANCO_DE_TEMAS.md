# 11 — Fuentes expertas y banco de temas

> Memoria de **presentaciones y material de especialistas IDIEM** que MKT comparte como insumo para
> contenidos. Datos estructurados en `config/topic_bank/expert_sources.json` (fuentes `SRC-*`,
> afirmaciones `SRC-*#C*` clasificadas y temas `TOP-*`). Este documento es la vista legible.
> Se amplía cada vez que llega material nuevo.

## Cómo se usa (reglas)

- **La librería 2A.2 sigue mandando.** Las fuentes `SRC-*` son evidencia auxiliar *candidata*; no se
  copian a `data/`.
- Clasificación de cada afirmación:
  - **SAFE** → contenido conceptual, normativo o metodológico del especialista, o estadística pública
    con su fuente citada (p. ej. NFPA). Puede ir al copy, **citando la fuente** cuando es de terceros.
  - **VERIFY** → capacidades IDIEM que no están en 2A.2, incidentes públicos con nombre de
    institución, datos agregados de proyectos. Se valida con MKT o el especialista antes de redactar.
  - **INTERNAL** → cifras de casos, referencias internas, proyectos u hospitales con nombre. Sirven para
    entender el tema; **no van al copy** sin autorización explícita.
- **Foco en el tema, nunca en el expositor (MKT, 14-10-2026):** los contenidos **no nombran ni citan**
  a los expositores ni a la charla/webinar de origen. Consentimiento de uso confirmado por MKT. Los
  nombres en este documento son solo trazabilidad interna; los autores no se consideran para contenido.
- **Servicios declarados en las fuentes = vigentes (MKT, 14-10-2026):** AITO, diagnósticos
  estructurales hospitalarios, hoja de ruta de mitigación de controversias, etc. se usan como evidencia
  auxiliar (`SRC-xxx#Cyy`) en briefs y copies.
- **Fuentes truncadas:** se usa solo el contenido disponible.
- **Sensibilidad:** todo tema que nombre proyecto, hospital, cliente o incidente se marca para que MKT
  valide antes de redactar.
- Al armar cada grilla mensual: revisar este banco **junto con** la librería 2A.2 y el ledger
  (`state/published_ledger.json`) para evitar repetir temas; la diversidad sigue
  `config/editorial_diversity.json`.
- Un tema usado se marca en el JSON (`used_in`: mes y post).

## Fuentes registradas (al 14-10-2026)

| ID | Presentación | Expositor | Fecha | Célula |
|---|---|---|---|---|
| SRC-001 | Vulnerabilidad de incendio en industria | Diego Olave · Jefe Unidad Ingeniería contra incendios | 01-09-2026 | IOM (industria → minería, MKT) |
| SRC-002 | Desafíos técnicos y contractuales en infraestructura hospitalaria | *(autor no relevante)* | 28-07-2026 | IHA |
| SRC-003 | Vulnerabilidades en caso de incendios en infraestructura hospitalaria | Diego Olave | 21-07-2026 | IHA |
| SRC-004 | Vulnerabilidad estructural (vida avanzada) y sísmica en Elementos No Estructurales | Sergio Tapia Pérez · Jefe de Proyectos, Div. Estructuras Peritajes | 14-07-2026 | IHA |
| SRC-005 | Reglamento RIC en Salud (DS N°8) | Sergio Reygadas Veragua · Jefe de Proyectos Eléctricos, DES | s/f | IHA |
| SRC-006 | Vulnerabilidad de incendio en infraestructura y faenas mineras | Diego Olave | 19-08-2026 | IOM |

Notas: la lectura de SRC-004 llegó truncada al final (proceso AITO); se usa solo lo disponible.

### Ideas fuerza por fuente

**SRC-001 / SRC-006 · Incendio en industria y minería (Olave)**
- Las fallas de activos a lo largo de su vida útil se traducen en incendios que comprometen la
  continuidad operacional.
- Análisis de riesgo en tres niveles: simple (checklist normativo), medio (normativo más
  vulnerabilidades) y avanzado (procesos, interrelaciones y consecuencias, con costo de detención).
- Brechas: falta de revisión por pares, estudios sin plazo de validez, falta de criterio
  multidisciplinario y "basta con cumplir la norma".
- Estrategia contra incendios en 8 ejes, concebida desde el proyecto. NCC 40 para la evaluación en
  ingeniería básica y de detalle.
- Curva P-F y monitoreo predictivo, con sus límites: hay pocos datos de fallas.
- Casos tipo:
  - Industria: transformadores (NFPA 850), frigoríficos y estructuras reticuladas.
  - Minería: envolventes de FRP en electro-obtención, correas transportadoras y CAEX en truck shop.
- Estadística NFPA: −66 % de incendios industriales en EE.UU. entre 1980 y 2021 (SAFE, citar).
- Incidentes con nombre (Puerto Ventanas, CAEX, Lineage, Renca, Grenfell): **VERIFY**.

**SRC-002 · Controversias hospitalarias**
- Un hospital no es una obra convencional. Hay 7 fuentes de impacto, del Programa Médico
  Arquitectónico (PMA) a la puesta en marcha.
- Mitigación:
  - Coordinación: BIM/MEP, constructibilidad, matriz de interfaces.
  - Permisos tratados como ruta crítica contractual.
  - Documentar los cambios con orden formal y valorización; sin eso, el reclamo es difícil de probar.
- Distinguir atraso, disrupción, pérdida de productividad, aceleración y concurrencia. Herramientas
  mínimas: CPM, línea base, as-built, curvas S, registro de cambios.
- Cinco lecciones finales. Hoja de ruta de mitigación en 3 fases: servicio IDIEM vigente (validado).
- Se cruza con la librería en ingeniería contractual de Salud: KB-IHA-002 a 005.

**SRC-003 · Incendio en hospitales (Olave)**
- Evacuación masiva vs. defensa en sitio. Vulnerabilidades de la OGUC (una sola zona vertical de
  seguridad) y de NFPA 101 (ascensores en emergencia). Escenarios con modelación de humos (FDS).
- Resistencia al fuego (NCh 935/1) vs. reacción al fuego (ASTM).
- Recintos críticos para la continuidad:
  - tanques criogénicos;
  - calderas (DS 10, RF-60);
  - bodegas SUSPEL (DS 43);
  - salas eléctricas (RIC N°2: F-120; RIC N°13).
- Riesgos en detección y extinción (NFPA 13, detectores desactivados, cambios de uso).
- Estadística NFPA de salud:
  - el fuego superó la habitación de origen solo en el 4 % de los casos;
  - la distribución eléctrica causa el 6 % de los incendios pero el 36 % de los daños;
  - la extinción automática estaba presente en el 47 % de los casos (1980-84) y en el 79 % (2006-10).
- Casos San Borja Arriarán (2021) y Gustavo Fricke (2020): **VERIFY**.

**SRC-004 · Vulnerabilidad estructural y elementos no estructurales en hospitales (Tapia)**
- La vulnerabilidad se compara con el estado de salud de una persona. Se acumula con:
  - el deterioro de los materiales;
  - ampliaciones sin verificación;
  - equipos cada vez más pesados;
  - sismos cada 15 a 20 años sin reparación adecuada.
- "La pregunta ya no es si un hospital resistirá un terremoto, sino si seguirá operativo después de
  uno." Elementos no estructurales (ENE) y su función en cirugía, laboratorio, imagenología y diálisis.
- Problemas típicos en obra: anclajes, soporte sísmico de ductos, fachadas ventiladas, cielos falsos,
  ascensores y cambios de uso.
- Servicios que la presentación declara (**vigentes, validados por MKT**; evidencia auxiliar):
  - diagnósticos estructurales y propuestas de refuerzo;
  - revisiones sísmicas;
  - peritajes forenses;
  - **AITO** (Asesoría a la Inspección Técnica de Obra).

**SRC-005 · RIC en Salud (Reygadas)**
- La transición la define la fecha y condición del permiso de edificación (oficios de la SEC).
- Pasó de 1 norma a 19 pliegos (de 175 a 478 páginas).
- Cinco cambios prácticos; el cambio de fondo es pasar de instalar a demostrar con evidencia.
- RIC N°11: el alcance va más allá de "hospital".
- Sistemas de emergencia: de 4 a 3 grupos, con la **numeración invertida**. El Grupo 2 pasa a ser la
  máxima criticidad.
- Sistema médico IT en pabellones (50 kΩ, 0,2 Ω, libro de mantenimiento).
- "Los m² no definen la potencia": usar solo el mensaje agregado. Las cifras por hospital con nombre
  son **INTERNAL**.
- Efecto "bola de nieve" y decisiones por etapa y por rol.
- Cifras de casos (+86,1 %, 10–25 %, 8–12 meses): **INTERNAL**.

## Banco de temas candidatos (22)

| ID | Célula | Tema | Sugerencia (arquetipo · hook · formato) | Cuidado |
|---|---|---|---|---|
| TOP-001 | IHA | ¿Seguirá operativo después del terremoto? ENE en hospitales | technical_question · question · carrusel | — |
| TOP-002 | IHA | AITO: asesoría independiente a la ITO en obras hospitalarias | process_result · process_step · carrusel | — |
| TOP-003 | IHA | Hospitales que envejecen: cómo se acumula la vulnerabilidad | risk_prevention · insight · estático | — |
| TOP-004 | IHA | Un hospital no es una obra convencional: 7 fuentes de controversia | evidence_learning · contrast · carrusel | — |
| TOP-005 | IHA | Atraso, disrupción, aceleración, concurrencia: no son lo mismo | data_implication · insight · carrusel | — |
| TOP-006 | IHA | La sala de imagenología como ejemplo de complejidad | project_challenge · scenario · estático | — |
| TOP-007 | IHA | Planificar la puesta en marcha desde el diseño | risk_prevention · risk · estático | — |
| TOP-008 | IHA | Permisos como ruta crítica contractual | problem_impact_capability · contrast · estático | — |
| TOP-009 | IHA | Evacuar o defender en sitio: incendios en hospitales | technical_question · question · carrusel | casos con nombre = VERIFY |
| TOP-010 | IHA | Pocos incendios eléctricos, gran parte del daño (NFPA) | data_implication · data_point · estático | citar NFPA |
| TOP-011 | IHA | Calderas, tanques criogénicos y salas eléctricas: la continuidad que no se ve | capability_application · scenario · carrusel | — |
| TOP-012 | IHA | RIC en salud: el Grupo 2 es ahora la máxima criticidad | technical_question · technical_claim · carrusel | — |
| TOP-013 | IHA | La "bola de nieve" de una exigencia eléctrica tardía | process_result · process_step · carrusel | sin cifras INTERNAL |
| TOP-014 | IHA | Los m² no definen la potencia de un hospital | data_implication · insight · estático | sin nombres ni cifras por proyecto |
| TOP-015 | IHA | Sistema médico IT en pabellones: de instalar a demostrar | capability_application · technical_claim · estático | — |
| TOP-016 | IHA | ¿Mi proyecto se rige por el RIC? La fecha del permiso manda | evidence_learning · question · carrusel | vigencia de oficios (GR-13) |
| TOP-017 | IHA | Quién decide qué: mandante, proyectista y constructora | problem_impact_capability · contrast · carrusel | — |
| TOP-018 | IOM | Tres niveles de análisis de riesgo de incendio | evidence_learning · contrast · carrusel | — |
| TOP-019 | IOM | Correas, CAEX y envolventes: riesgo de incendio en faena | project_challenge · scenario · carrusel | incidentes = VERIFY |
| TOP-020 | IOM | La curva P-F: detectar el deterioro antes de la falla | data_implication · technical_claim · estático | — |
| TOP-021 | IOM | Un estudio de riesgo también vence | risk_prevention · risk · estático | — |
| TOP-022 | IOM | Estrategia contra incendios en 8 ejes desde el proyecto | process_result · process_step · carrusel | — |

**Lectura para la planificación:** este material **repone la célula Salud (IHA)**, que quedó sin
ítems frescos tras noviembre: 17 temas IHA y 5 IOM listos para diciembre en adelante. Validaciones de
MKT cerradas el 14-10-2026 (consentimiento, servicios vigentes, autores, célula de industria, fuentes
truncadas). Siguen pendientes por tema: incidentes con nombre (VERIFY) y cifras internas (INTERNAL).

## Cómo agregar material nuevo

1. Leer la presentación o documento y registrar una fuente `SRC-0NN` (título, fecha, link, células;
   expositor solo como trazabilidad interna, nunca en contenidos).
2. Extraer afirmaciones `SRC-0NN#Cxx` con `kind` (concept, normative, third_party_stat,
   idiem_capability, public_incident, project_data, internal_reference) y `class`
   (SAFE/VERIFY/INTERNAL/DO_NOT_PUBLISH).
3. Proponer temas `TOP-0NN` enlazados a afirmaciones y, si aplica, a `knowledge_id` de 2A.2.
4. Actualizar esta vista y correr `pytest tests/test_topic_bank.py`.

## Servicios publicados en www.idiem.cl (`WEB-*`, extraídos el 19-10-2026)

Registro en `config/topic_bank/web_services.json`, con el texto **literal** del sitio
(https://www.idiem.cl/servicios) en tres niveles: categoría → área → servicio específico (descripción
y prestaciones de "¿Qué tipo de servicio necesitas?"). Total: 7 categorías, 33 áreas, 135 servicios
(el sitio repite áreas bajo varias categorías: 70 entradas tienen `same_text_as`; únicas: 105).

| Categoría | Título | Áreas | Servicios |
|---|---|---|---|
| `WEB-001` | Asesoría contractual en controversias y claims | 1 | 11 |
| `WEB-002` | Asesorías y estudios técnicos | 9 | 48 |
| `WEB-003` | Ensayos de laboratorio | 8 | 28 |
| `WEB-004` | Geotecnia y Prospecciones | 2 | 6 |
| `WEB-005` | Inspección técnica de obra | 4 | 12 |
| `WEB-006` | Laboratorios en obra o fábrica | 5 | 16 |
| `WEB-007` | Peritajes y análisis de fallas | 4 | 14 |

Reglas de uso:

- **Todo `WEB-*` es VERIFY y está disponible (MKT, 19-10-2026).** Se puede planificar y redactar con él,
  citándolo como `WEB-xxx` marcado VERIFY en brief y copy. Se valida cuando MKT aprueba el post que lo usa
  (`validated_by`, `validated_on` en el JSON) o se corrige según lo que MKT cambie en el post. 2A.2 sigue mandando: el sitio no crea capacidades técnicas nuevas ni
  asigna célula (la decide `config/cell_rules.json`; Transporte sigue en `CONTENT_GAP`).
- **`promo_flags`** marca superlativos del sitio (p. ej. "la mejor tecnología", "el único triaxial
  gigante en Chile", "altos estándares"): **no pasan al copy** aunque el servicio esté validado.
- **`claim_flags`** marca menciones de certificación, acreditación o normas: requieren respaldo en
  2A.2 o validación puntual antes de afirmarse.
- **Cruce con 2A.2 (19-10-2026):** `docs/12_CRUCE_WEB_VS_2A2.md` (generado desde
  `config/topic_bank/web_crosswalk.json`). **2A.2 prevalece**: si el servicio tiene `knowledge_id`, se usa
  ese texto y su política; el sitio solo aporta alcance nuevo (VERIFY). Estados: RESPALDADO 36, PARCIAL 40,
  SOLO_RESERVA 11, NUEVO 18, BLOQUEADO 0 (productividad queda activa en VERIFY, MKT 19-10-2026).
- **Re-extracción:** `PYTHONPATH=src python -m idiem.web_services`. Conserva los IDs por ruta; si el
  texto de un servicio cambió, borra su validación y lo devuelve a VERIFY. Correr después
  `pytest tests/test_web_services.py tests/test_web_crosswalk.py` y revisar el diff antes de commitear;
  si aparecen servicios nuevos, cruzarlos en `web_crosswalk.json` y regenerar con `python -m idiem.web_crosswalk`.
