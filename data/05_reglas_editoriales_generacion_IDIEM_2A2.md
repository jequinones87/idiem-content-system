# IDIEM — Reglas editoriales y de generación de contenido 2A.2

## 1. Propósito

Este documento define cómo convertir `04_base_produccion_IDIEM_2A2.json` en briefs y borradores de contenido para LinkedIn sin perder trazabilidad factual.

La capa se divide deliberadamente en dos:

1. **Reglas factuales no negociables**: heredadas directamente de la auditoría y la base de producción.
2. **Reglas editoriales propuestas**: convenciones operativas para producir contenido técnico, sobrio y consistente. Estas reglas pueden ajustarse posteriormente sin alterar la auditoría factual.

Este documento **no define el sistema visual** de IDIEM ni sustituye lineamientos gráficos existentes.

---

## 2. Reglas factuales no negociables

- **GR-01** — Para contenido de una célula, recuperar primero conocimiento técnico de esa misma célula; no importar relaciones de otra célula por similitud temática.
- **GR-02** — La evidencia verificada y la política de uso del registro son obligatorias. No agregar especificidad, metodología, resultados, clientes o aplicaciones que no estén respaldados.
- **GR-03** — Los registros NAME_ONLY_DO_NOT_EXPAND sólo pueden nombrarse; no explicar qué hacen ni equipararlos a otros servicios.
- **GR-04** — Los registros USE_TECHNICAL_CORE_BLOCK_CLAIMS permiten usar el núcleo técnico, pero bloquean rankings, exclusividades, superlativos y claims mundiales asociados.
- **GR-05** — Los elementos de evidencia auxiliar no crean servicios ni capacidades. Sólo complementan un contenido cuando su propia política lo permite.
- **GR-06** — Los CLAIM_BLOQUEADO y los registros que requieren validación externa no se publican como hechos sin una validación posterior.
- **GR-07** — La reserva SIN_CELULA_PRIORIZADA queda inactiva para la generación de contenidos de las cinco células; no es información descartada.
- **GR-08** — Las relaciones EXCLUDED_DO_NOT_USE nunca deben usarse como evidencia ni como base de un claim.
- **GR-09** — En minería, mandante/contratista no decide la célula. Ingeniería, integridad, diagnóstico, confiabilidad y continuidad pertenecen a INFRA OPERACIÓN MINERA; laboratorio, ensayo, inspección, control y evidencia pertenecen a LAB MINERO DIGITAL.
- **GR-10** — “Digital” no es requisito técnico de LAB MINERO DIGITAL. BIM, monitoreo remoto, plataformas o analítica no migran a Lab por el solo hecho de ser digitales.
- **GR-11** — Triaxial Gigante se considera siempre asociado a proyectos mineros, según decisión explícita del usuario en 2A.2.
- **GR-12** — Infra Hospitalaria tiene prioridad sobre Infra Pública cuando el proyecto es de salud; Infra Crítica Transporte se limita a Metro/EFE.
- **GR-13** — Vigencias normativas/jurídicas, acreditaciones, rankings, cifras relativas y cobertura actual deben verificarse antes de publicación cuando el registro lo indique.
- **GR-14** — No contar documentos relacionados/duplicados como evidencia independiente adicional. Usar document_group e independent_source para controlar el peso de la evidencia.

---

## 3. Reglas editoriales propuestas

- **ER-01 · principio_editorial** — Cada pieza debe partir de un problema, decisión, riesgo, necesidad técnica o evidencia relevante para la célula; evitar partir sólo desde el nombre comercial de un servicio.
- **ER-02 · tono** — Usar un tono técnico, sobrio, experto e institucional. Evitar lenguaje de venta agresivo, grandilocuencia, urgencia artificial y afirmaciones no respaldadas.
- **ER-03 · tono** — Priorizar claridad sobre jerga. Cuando un término técnico sea necesario, explicarlo sólo si la base lo permite; si no, mantener el término sin desarrollar.
- **ER-04 · estructura** — La estructura recomendada de una pieza es: contexto/problema → evidencia o explicación técnica respaldada → implicancia para el proyecto/operación → cierre/CTA sobrio.
- **ER-05 · estructura** — No es obligatorio mencionar IDIEM en la apertura. La marca puede aparecer después de haber establecido el problema o valor técnico.
- **ER-06 · seleccion_tema** — Preferir un único foco técnico por pieza. Combinar varios servicios sólo cuando la base demuestre una relación clara entre ellos dentro del mismo problema o proyecto.
- **ER-07 · seleccion_tema** — No importar conocimiento técnico desde otra célula para completar una pauta. Si una célula carece de evidencia suficiente, registrar CONTENT_GAP o solicitar insumo experto.
- **ER-08 · formatos** — Usar imagen estática para una idea principal, dato o mensaje breve; usar carrusel cuando la evidencia permita desarrollar una secuencia de 3 o más ideas relacionadas sin rellenar con contenido genérico.
- **ER-09 · claims** — Evitar superlativos, rankings, exclusividades, promesas absolutas y formulaciones de garantía salvo validación externa específica y vigente.
- **ER-10 · cifras** — Una cifra sólo puede publicarse cuando la evidencia incluya su contexto suficiente y no exista una restricción de vigencia. Cifras relativas como 'últimos X años' requieren fecha de corte antes de reutilizarse.
- **ER-11 · normativa** — Normas, acreditaciones, mecanismos legales, convenios y referencias regulatorias deben verificarse en su vigencia antes de convertirse en mensaje público cuando la base lo indique.
- **ER-12 · casos_proyectos** — Un proyecto o cliente sólo puede nombrarse cuando la relación documental lo identifica textualmente. Una fotografía, inferencia visual o similitud sectorial no basta.
- **ER-13 · casos_proyectos** — No atribuir resultados, impactos, ahorros, reducción de riesgo o desempeño a un proyecto salvo que esos resultados estén expresamente respaldados.
- **ER-14 · evidencia_auxiliar** — Beneficios, credenciales, cobertura, atributos diferenciadores y evidencia sectorial pueden complementar una pieza, pero nunca reemplazar el núcleo técnico ni transformarse en una capacidad.
- **ER-15 · cta** — Usar CTA de baja fricción y coherente con el contenido: conocer el servicio, conversar con un especialista, revisar una solución o solicitar información. Evitar CTA que prometan resultados no respaldados.
- **ER-16 · repeticion** — No repetir el mismo knowledge_id como eje principal en piezas consecutivas. La repetición sólo se permite si cambia claramente el problema, aplicación, etapa del ciclo de vida o audiencia.
- **ER-17 · aprobacion** — Toda pieza generada por IA queda en estado DRAFT hasta pasar control factual y aprobación humana. Los especialistas validan contenidos técnicos puntuales cuando el tema requiera conocimiento no contenido en la base.
- **ER-18 · actualidad** — Temas de actualidad, cambios normativos, tendencias sectoriales o coyuntura no deben generarse sólo desde esta biblioteca histórica; requieren una fuente externa vigente o insumo experto.

---

## 4. Guía editorial por célula

### INFRA PÚBLICA RESILIENTE

**Posicionamiento:** Infraestructura pública que sostiene conectividad, acceso y resiliencia territorial; respaldo técnico al servicio del país.

**Ángulos preferidos:**
- decisiones técnicas a lo largo del ciclo de vida de infraestructura pública
- control, inspección, diagnóstico y soporte técnico de obras públicas
- condición, desempeño y continuidad de infraestructura pública
- evidencia de experiencia pública cuando esté textualmente respaldada

**Evitar:**
- usar 'resiliente' como requisito técnico obligatorio
- absorber proyectos de salud o Metro/EFE
- presentar la Ley 21.094 como servicio técnico

### INFRA HOSPITALARIA Y ASISTENCIAL

**Posicionamiento:** Infraestructura destinada a la salud y al cuidado de las personas; habitabilidad, confiabilidad y continuidad.

**Ángulos preferidos:**
- desafíos técnicos de infraestructura sanitaria
- continuidad y confiabilidad de instalaciones de salud
- servicios transversales sólo cuando la aplicación hospitalaria esté respaldada

**Evitar:**
- ampliar GREEN HOSPITAL más allá de su alcance documentado
- crear prestaciones hospitalarias a partir de experiencia sectorial general
- extender la célula a infraestructura social no sanitaria

### INFRA CRÍTICA TRANSPORTE

**Posicionamiento:** Infraestructura de Metro y EFE y sus sistemas directamente asociados.

**Ángulos preferidos:**
- contenido sectorial o institucional respaldado específicamente por Metro/EFE
- insumos técnicos nuevos validados por especialistas para ampliar la biblioteca

**Evitar:**
- usar puentes, autopistas, aeropuertos, puertos o túneles genéricos como Transporte
- inventar servicios técnicos para compensar la ausencia actual de knowledge_items

**Regla de gap:** La base 2A.2 contiene 0 knowledge_items técnicos activos para esta célula. No generar piezas técnicas autónomas desde la biblioteca actual; marcar CONTENT_GAP hasta incorporar evidencia técnica específica Metro/EFE.

### INFRA OPERACIÓN MINERA

**Posicionamiento:** Continuidad operacional, integridad, confiabilidad, diagnóstico, ingeniería y soporte técnico de activos e infraestructura minera.

**Ángulos preferidos:**
- activos que no pueden detenerse
- integridad y condición de infraestructura y equipos
- diagnóstico, monitoreo, mantenimiento y rehabilitación
- ingeniería y soporte técnico en operación y CAPEX minero

**Evitar:**
- clasificar por mandante versus contratista
- mover servicios a Lab por contener BIM, sensores, plataformas o analítica
- presentar ensayos autónomos como ingeniería de continuidad

### LAB MINERO DIGITAL

**Posicionamiento:** Laboratorio, ensayo, inspección, control técnico y generación de evidencia para proyectos y obras mineras.

**Ángulos preferidos:**
- evidencia y control técnico desde terreno
- ensayos y caracterización de materiales
- control de uniones HDPE
- END e inspección de soldaduras
- trazabilidad y acceso a resultados como atributos complementarios

**Evitar:**
- usar 'digital' como requisito de entrada
- convertir ingeniería de integridad/continuidad en Lab
- usar claims mundiales o superlativos del Triaxial o laboratorios sin validación

---

## 5. Tipos de contenido permitidos

### TECHNICAL_INSIGHT
- **Propósito:** Explicar un problema, criterio o desafío técnico respaldado por uno o más knowledge_items.
- **Evidencia mínima:** 1 knowledge_item activo
- **Insumo experto:** Opcional; obligatorio si se agregan recomendaciones no presentes en la base.

### SERVICE_EXPLAINER
- **Propósito:** Explicar qué hace un servicio/capacidad y en qué aplicación documentada participa.
- **Evidencia mínima:** 1 knowledge_item con service/capability y evidencia suficiente
- **Insumo experto:** No necesario si el alcance se mantiene dentro de la base.

### PROJECT_EVIDENCE
- **Propósito:** Mostrar experiencia o aplicación concreta en un proyecto/sector identificado.
- **Evidencia mínima:** Relación textual que identifique proyecto/aplicación; no evidencia sólo fotográfica.
- **Insumo experto:** Necesario si se quieren agregar resultados o contexto no documentado.

### VALUE_ATTRIBUTE
- **Propósito:** Reforzar un diferenciador, beneficio, cobertura o credencial permitida.
- **Evidencia mínima:** auxiliary_evidence con política compatible
- **Insumo experto:** Puede requerir validación de vigencia.

### EXPERT_INPUT_REQUIRED
- **Propósito:** Contenido sobre tendencia, opinión técnica, actualización normativa o tema estratégico no cubierto por la biblioteca.
- **Evidencia mínima:** Insumo especialista y/o fuente externa vigente
- **Insumo experto:** Obligatorio.

---

## 6. Flujo obligatorio de generación

1. **SELECT_CELL** — Definir célula objetivo antes de buscar contenido.
2. **RETRIEVE** — Recuperar knowledge_items de la célula y, sólo como complemento, auxiliary_evidence permitido.
3. **CHECK_POLICY** — Leer generation_policy, usage_instruction, notas y fuentes de cada ítem.
4. **CHOOSE_ANGLE** — Elegir un único foco editorial y un content_type compatible con la evidencia.
5. **BUILD_FACT_SHEET** — Separar antes de redactar: hechos permitidos, matices obligatorios, claims bloqueados y vacíos.
6. **DRAFT** — Redactar sólo desde el fact sheet y las reglas editoriales.
7. **FACT_CHECK** — Comprobar cada afirmación concreta contra knowledge_id, relation_id o auxiliary_id.
8. **EDITORIAL_CHECK** — Revisar claridad, foco, tono, repetición, CTA y formato.
9. **HUMAN_APPROVAL** — Mantener DRAFT hasta aprobación humana; derivar al especialista cuando corresponda.

---

## 7. Estados de aprobación

- **DRAFT:** Generado pero aún no aprobado.
- **FACT_CHECKED:** Todas las afirmaciones concretas tienen trazabilidad y respetan políticas.
- **EXPERT_REVIEW:** Requiere o está en revisión por especialista.
- **APPROVED:** Aprobado para producción/diseño.
- **BLOCKED:** No publicar hasta resolver una restricción factual, vigencia o contradicción.
- **CONTENT_GAP:** La célula/tema no dispone de evidencia suficiente en la biblioteca actual.

---

## 8. Checklist QA antes de aprobación

- [ ] ¿La pieza tiene una célula definida?
- [ ] ¿El eje principal está respaldado por knowledge_id(s) de esa misma célula?
- [ ] ¿Cada afirmación técnica respeta generation_policy y usage_instruction?
- [ ] ¿Se evitó ampliar términos NAME_ONLY_DO_NOT_EXPAND?
- [ ] ¿Se bloquearon rankings, superlativos y claims cuando corresponde?
- [ ] ¿Las cifras tienen contexto y vigencia suficiente?
- [ ] ¿Los proyectos/clientes nombrados están textualmente identificados en la evidencia?
- [ ] ¿Se evitó atribuir resultados o impactos no documentados?
- [ ] ¿La evidencia auxiliar se usa sólo como complemento?
- [ ] ¿El contenido evita importar conocimiento desde otra célula?
- [ ] ¿El CTA es sobrio y no promete resultados no respaldados?
- [ ] ¿Si faltó evidencia, se marcó CONTENT_GAP o EXPERT_INPUT_REQUIRED en vez de rellenar?
- [ ] ¿La pieza permanece DRAFT hasta aprobación humana?

---

## 9. Regla de contenido insuficiente

Cuando la biblioteca no soporte suficientemente un tema, el sistema debe:

1. detener la generación factual;
2. registrar qué información falta;
3. marcar `CONTENT_GAP` o `EXPERT_INPUT_REQUIRED`;
4. solicitar un insumo técnico o una fuente vigente;
5. incorporar el nuevo conocimiento sólo después de validarlo y agregarlo a la biblioteca.

No se permite completar el vacío con conocimiento general del modelo.

---

## 10. Estructura mínima del brief de contenido

Cada pieza debe conservar al menos:

- célula;
- tipo de contenido;
- objetivo y ángulo editorial;
- `knowledge_ids` utilizados;
- hechos permitidos;
- matices obligatorios;
- claims bloqueados;
- gaps detectados;
- formato recomendado;
- borrador;
- brief visual;
- trazabilidad a `relation_id` y `document_id`;
- estado de QA y aprobación humana.

La estructura completa y legible por máquina se encuentra en `05_plantilla_brief_contenido_IDIEM_2A2.json`.

---

## 11. Restricción especial — INFRA CRÍTICA TRANSPORTE

La biblioteca actual tiene **0 knowledge_items técnicos activos** para esta célula. La célula está definida estratégicamente y existe evidencia sectorial, pero no hay una jerarquía técnica Metro/EFE suficientemente individualizada.

Por tanto, el agente no debe construir posts técnicos de Transporte reutilizando capacidades de Infra Pública u otras células. Debe marcar `CONTENT_GAP` hasta incorporar evidencia técnica específica de Metro/EFE o un insumo experto validado.

---

## 12. Resultado esperado del agente

El agente debe entregar primero un **brief factual trazable** y sólo después producir el copy. De esta manera la redacción queda subordinada a la evidencia y no al revés.
