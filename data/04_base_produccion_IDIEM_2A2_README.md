# IDIEM — Base limpia de producción 2A.2

## Propósito

Esta base es la capa de producción derivada de la auditoría factual 2A.1B y la taxonomía 2A.2. Está preparada para generación de contenidos, búsqueda/retrieval y futuro handoff a Claude Code.

No reemplaza ni sobrescribe los archivos de auditoría. La trazabilidad se mantiene mediante `relation_id`, `document_id`, página y evidencia verificada.

## Contenido

- Relaciones fuente totales: **292**
- Ítems técnicos activos: **116**
- Relaciones fuente que alimentan conocimiento técnico: **102**
- Evidencias/atributos auxiliares: **35**
- Relaciones de reserva fuera de las cinco células: **150**
- Relaciones excluidas como evidencia: **5**
- Documentos editoriales indexados: **29**

## Políticas de uso del conocimiento técnico

- `USE_FACTUAL`: Puede usarse como conocimiento técnico factual, respetando literalmente el alcance respaldado por la evidencia. (42 ítems)
- `USE_AUDITED_CORRECTION`: Usar únicamente la versión corregida/normalizada por la auditoría 2A.1B; no reutilizar la normalización anterior. (58 ítems)
- `USE_WITH_MATIZ`: Puede usarse sólo conservando el matiz/limitación registrada; no ampliar el alcance. (10 ítems)
- `USE_TECHNICAL_CORE_BLOCK_CLAIMS`: Puede usarse el núcleo técnico; rankings, exclusividades, superlativos u otros claims asociados quedan bloqueados. (3 ítems)
- `NAME_ONLY_DO_NOT_EXPAND`: Puede mencionarse el término, pero no explicar metodología, alcance, entregable ni equivalencias no documentadas. (3 ítems)

## Distribución de ítems técnicos por célula

- **INFRA PÚBLICA RESILIENTE:** 24
- **INFRA HOSPITALARIA Y ASISTENCIAL:** 6
- **INFRA CRÍTICA TRANSPORTE:** 0
- **INFRA OPERACIÓN MINERA:** 65
- **LAB MINERO DIGITAL:** 21

## Estructura del JSON

- `metadata`: estado y cobertura de la base.
- `cell_definitions`: definiciones y reglas operativas de las cinco células.
- `generation_rules`: controles que debe respetar cualquier agente de contenido.
- `knowledge_items`: conocimiento técnico activo, normalizado y deduplicado.
- `knowledge_sources`: trazabilidad exacta de cada ítem técnico hacia relaciones, documentos, páginas y evidencia.
- `auxiliary_evidence`: claims, beneficios, atributos, credenciales, etapas, mecanismos de contratación y evidencia sectorial que no deben confundirse con capacidades.
- `reserve_outside_prioritized_cells`: conocimiento válido fuera de las cinco células; permanece inactivo para esta estrategia.
- `excluded_relations`: relaciones que no deben usarse como evidencia.
- `source_documents`: índice de los 29 documentos editoriales con control de grupos/versiones.

## Regla de oro para generación

Un agente no debe transformar una evidencia auxiliar en una capacidad, completar términos no definidos, usar claims bloqueados como hechos, ni importar conocimiento de otra célula por similitud temática. Ante ausencia de respaldo, debe omitir el dato o marcarlo para revisión.
