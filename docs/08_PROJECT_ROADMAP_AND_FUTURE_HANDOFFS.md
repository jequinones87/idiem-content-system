# IDIEM — Project Roadmap and Future Handoffs

## Propósito

Este documento entrega a Claude Code la visión completa del sistema que se está construyendo para IDIEM.

Su objetivo es evitar que las decisiones de arquitectura de la etapa actual bloqueen o compliquen las siguientes fases, especialmente:

- incorporación del Design System IDIEM;
- biblioteca de fotografías y assets;
- generación visual;
- flujos de aprobación;
- integración con Metricool;
- orquestación con n8n;
- publicación y reporting.

Este documento complementa `CLAUDE.md` y los documentos `docs/01–07`.

La regla principal es:

> Construir ahora el motor factual/editorial de forma modular, dejando interfaces preparadas para diseño, assets e integraciones futuras, pero sin inventar ni implementar esas capas antes de recibir sus handoffs específicos.

---

# 1. Visión general del sistema

La arquitectura final esperada es:

```text
KNOWLEDGE
    ↓
EDITORIAL
    ↓
PLANNER
    ↓
CONTENT BRIEF
    ↓
VISUAL BRIEF
    ↓
DESIGN SYSTEM + IMAGE LIBRARY
    ↓
VISUAL PRODUCTION
    ↓
HUMAN APPROVAL
    ↓
METRICOOL / N8N
    ↓
PUBLISHING
    ↓
REPORTING / LEARNING
```

Cada bloque debe permanecer desacoplado.

Un cambio en diseño no debe requerir modificar la base factual.

Un cambio en células o taxonomía no debe requerir reescribir el motor visual.

Una nueva imagen no debe alterar la lógica de conocimiento.

---

# 2. FASE A — Knowledge System

## Estado

`COMPLETADA COMO HANDOFF 2A.2`

## Objetivo

Crear una biblioteca factual, auditada y trazable de servicios, capacidades, aplicaciones y evidencia IDIEM.

## Entregables existentes

- mapa de relaciones 2A.2;
- taxonomía maestra;
- base limpia de producción;
- knowledge items;
- evidencia auxiliar;
- reserva fuera de células;
- relaciones excluidas;
- reglas de generación;
- validación de cierre.

## Principios

- evidence-first;
- trazabilidad;
- no completar gaps;
- claims y capacidades separados;
- políticas de uso explícitas;
- células configurables;
- archivos canónicos inmutables.

## Rol de Claude Code

Claude Code debe consumir esta capa.

No debe reinterpretarla ni reconstruirla desde los brochures.

---

# 3. FASE B — Content Planner

## Estado

`IMPLEMENTACIÓN ACTUAL`

## Objetivo

Transformar la biblioteca factual en una planificación mensual/semanal de contenidos.

## Debe permitir

- definir cantidad objetivo de publicaciones;
- distribuir contenido por célula;
- aplicar pesos configurables;
- considerar disponibilidad real de evidencia;
- evitar repetición excesiva;
- detectar gaps;
- proponer ángulos editoriales;
- generar una grilla revisable por humanos.

## Restricción fundamental

La planificación no puede sacrificar factualidad para cumplir cuotas.

Ejemplo:

Si `INFRA CRÍTICA TRANSPORTE` tiene una cuota asignada pero no existe evidencia técnica suficiente:

```text
NO:
tomar un servicio de Infra Pública y reclasificarlo.

SÍ:
CONTENT_GAP
```

---

# 4. FASE C — Editorial Drafting

## Estado

`IMPLEMENTACIÓN ACTUAL`

## Objetivo

Generar briefs y borradores de contenido sólo después de construir un fact sheet trazable.

## Flujo obligatorio

```text
CELL
  ↓
RETRIEVAL
  ↓
POLICY CHECK
  ↓
FACT SHEET
  ↓
EDITORIAL ANGLE
  ↓
CONTENT BRIEF
  ↓
COPY
  ↓
QA
  ↓
HUMAN APPROVAL
```

## Salida esperada

Cada pieza debe conservar:

- célula;
- content type;
- knowledge IDs;
- auxiliary IDs;
- hechos permitidos;
- matices;
- claims bloqueados;
- gaps;
- copy;
- visual brief;
- relation IDs;
- document IDs;
- estado de QA.

---

# 5. FASE D — Design System Handoff

## Estado

`HANDOFF FUTURO`

## No implementar todavía

Claude Code no debe definir por su cuenta:

- colores;
- tipografías;
- estilos;
- grillas;
- componentes;
- jerarquía visual;
- tratamientos de imagen;
- uso de logo;
- composiciones;
- templates gráficos.

Estos elementos llegarán mediante un handoff específico.

## Objetivo futuro

Incorporar el Design System IDIEM como una capa separada del conocimiento factual.

Arquitectura sugerida:

```text
visual/
    design-system/
        tokens
        typography
        colors
        spacing
        grids
        components
        brand rules

    templates/
        static/
        carousel/
```

## Requisito actual para Claude Code

Dejar preparada una interfaz para recibir esta información sin modificar el motor editorial.

No hard-codear decisiones visuales en la lógica de generación de contenido.

---

# 6. FASE E — Image Library Handoff

## Estado

`HANDOFF FUTURO`

## Objetivo

Crear una biblioteca estructurada de fotografías y assets IDIEM.

Claude Code no debe seleccionar imágenes reales hasta recibir esta biblioteca.

## Principio crítico

Una imagen no es evidencia factual por sí sola.

Debe distinguirse entre:

### `illustrative`

Imagen utilizada para representar visualmente un sector, contexto o concepto.

Puede acompañar un contenido.

No puede demostrar que:

- IDIEM trabajó en ese proyecto;
- una empresa es cliente;
- un servicio se ejecutó en ese lugar;
- una fotografía corresponde al caso descrito.

### `project_evidence`

Imagen asociada a un proyecto o evidencia IDIEM previamente validada.

Debe poseer metadata que permita vincularla a relaciones verificadas.

## Contrato recomendado

```json
{
  "image_id": "IMG-0001",
  "file": "archivo.jpg",
  "cells": [],
  "topics": [],
  "asset_type": "photography",
  "asset_role": "illustrative",
  "orientation": "horizontal",
  "people": false,
  "project_identified": false,
  "project_name": null,
  "relation_ids": [],
  "approved_for_use": true,
  "usage_notes": ""
}
```

## Requisito actual para Claude Code

Preparar únicamente:

- schema/interface;
- asset query;
- campos de metadata;
- placeholder de integración.

No inventar clasificación de fotografías.

---

# 7. FASE F — Visual Production

## Estado

`FUTURA`

## Dependencias

Sólo puede comenzar cuando existan:

1. brief editorial validado;
2. Design System;
3. templates;
4. biblioteca de assets;
5. reglas de uso de fotografía.

## Flujo esperado

```text
APPROVED CONTENT BRIEF
        ↓
VISUAL BRIEF
        ↓
TEMPLATE SELECTION
        ↓
ASSET QUERY
        ↓
IMAGE SELECTION
        ↓
LAYOUT / DESIGN
        ↓
VISUAL QA
```

## Estrategia operativa

La producción visual debe privilegiar el trabajo por lote mensual/semanal en lugar de diseñar post por post de manera aislada.

Esto permite:

- coherencia visual;
- balance de formatos;
- mejor uso de assets;
- control de repetición;
- revisión conjunta.

---

# 8. FASE G — Approval Workflow

## Estado

`FUTURA`

## Principio

El sistema debe mantener aprobación humana.

Estados previstos:

```text
DRAFT
FACT_CHECKED
EXPERT_REVIEW
APPROVED
BLOCKED
CONTENT_GAP
```

## Roles esperados

### Marketing

- planificación;
- contenido;
- tono;
- calendario;
- aprobación editorial.

### Gerencia Comercial

- validación de grilla/prioridades;
- relevancia comercial.

### Especialistas IDIEM

- revisión puntual cuando el contenido requiere conocimiento técnico no contenido en la biblioteca;
- validación de nuevos inputs técnicos.

## Regla

Un output generado por IA no debe considerarse publicable simplemente porque pasa validación automática.

---

# 9. FASE H — Metricool / n8n

## Estado

`FUTURA`

## Objetivo

Orquestar el flujo posterior a la aprobación.

Posibles funciones:

- exportar posts aprobados;
- programar contenidos;
- asociar assets finales;
- administrar calendario;
- registrar estado de publicación;
- enviar alertas;
- activar aprobaciones;
- mantener logs.

## Principio de arquitectura

Las integraciones deben consumir outputs aprobados.

No deben consultar directamente la biblioteca factual para crear contenido por su cuenta.

Correcto:

```text
knowledge
→ planner
→ brief
→ approval
→ integration
```

Incorrecto:

```text
Metricool/n8n
→ LLM libre
→ publicar
```

---

# 10. FASE I — Publishing and Reporting

## Estado

`FUTURA`

## Objetivo

Cerrar el ciclo mediante publicación y aprendizaje.

Datos potenciales:

- fecha;
- célula;
- topic;
- knowledge IDs;
- formato;
- alcance;
- impresiones;
- engagement;
- clics;
- leads;
- comportamiento por célula;
- comportamiento por temática.

## Evolución esperada

Con el tiempo, el planner podrá usar performance histórica para sugerir distribución o ángulos.

Pero:

> Performance no modifica la verdad factual.

La analítica puede influir en **qué comunicar**, nunca en **qué es cierto**.

---

# 11. Separación de dominios

Claude Code debe mantener los siguientes dominios conceptualmente separados:

## Knowledge

Responde:

> ¿Qué sabemos y con qué evidencia?

## Editorial

Responde:

> ¿Qué podemos decir y bajo qué reglas?

## Planner

Responde:

> ¿Qué conviene comunicar, cuándo y con qué balance?

## Visual

Responde:

> ¿Cómo se representa gráficamente el contenido aprobado?

## Assets

Responde:

> ¿Qué imágenes o recursos están disponibles y bajo qué condiciones?

## Integrations

Responde:

> ¿Cómo se mueve el output aprobado hacia otros sistemas?

---

# 12. Decisiones que Claude Code NO debe tomar todavía

Hasta recibir futuros handoffs, Claude Code no debe decidir:

- identidad visual;
- paleta;
- tipografías;
- templates;
- número definitivo de slides por carrusel;
- reglas fotográficas;
- clasificación real de imágenes;
- selección automática de fotografías;
- tratamiento gráfico de fotografías;
- integración con Metricool;
- workflows n8n;
- publicación automática;
- reporting definitivo.

Debe limitarse a dejar interfaces claras para esas funciones.

---

# 13. Validación paralela con el equipo IDIEM

Las definiciones de células y reglas operativas están siendo revisadas paralelamente por el equipo.

Por ello:

- células;
- scopes;
- pesos;
- reglas de exclusión;
- posicionamientos;

deben permanecer configurables.

Un cambio validado por el equipo debe poder incorporarse actualizando configuración/datos y ejecutando regression tests.

No debe requerir reescribir el sistema.

---

# 14. Estado actual del proyecto

```text
FASE A — Knowledge System          ✅ COMPLETA
FASE B — Content Planner           🟡 IMPLEMENTACIÓN
FASE C — Editorial Drafting        🟡 IMPLEMENTACIÓN
FASE D — Design System Handoff     ⏳ SIGUIENTE HANDOFF
FASE E — Image Library Handoff     ⏳ SIGUIENTE HANDOFF
FASE F — Visual Production         ⏳ FUTURA
FASE G — Approval Workflow         ⏳ FUTURA
FASE H — Metricool / n8n           ⏳ FUTURA
FASE I — Publishing / Reporting    ⏳ FUTURA
```

---

# 15. Principio final de arquitectura

La implementación actual debe optimizarse para:

> estabilidad factual + modularidad futura.

Claude Code debe construir el sistema de manera que:

- la base factual pueda evolucionar;
- las células puedan ajustarse;
- el sistema editorial pueda cambiar;
- el Design System pueda incorporarse después;
- las fotografías puedan catalogarse después;
- los templates puedan cambiar;
- las integraciones puedan reemplazarse;

sin romper la cadena de trazabilidad entre evidencia, brief y contenido.

La evidencia IDIEM debe seguir siendo siempre la capa más estable y protegida del sistema.
