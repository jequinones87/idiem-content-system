# 01 — Scope and principles

## Product goal

Create an internal system that helps IDIEM produce a monthly/weekly LinkedIn content grid from an audited knowledge base.

The tool should help answer:

- What cells need content?
- What technically supported topics are available?
- Which evidence can be used?
- What claims are blocked or need validation?
- Which topics need expert input?
- What copy/visual brief can be drafted safely?
- What has already been used recently?

## Current operating context

The current planning target used in prior work is approximately **12 posts/month, 2–3 per week**. Treat this as configurable, not hard-coded.

Historical cell weighting reference:
- Infra Crítica Transporte: 6
- Infra Hospitalaria y Asistencial: 6
- Infra Operación Minera: 8
- Infra Pública Resiliente: 6
- Lab Minero Digital: 8

For a 12-post month, the planner may normalize these weights proportionally, but must also respect actual evidence availability. If evidence does not support a quota, return a gap rather than borrowing from another cell.

## Human-in-the-loop

The system does not publish by itself.

Expected approvals:
- monthly themes/grid: marketing + commercial management;
- specific technical content: specialist when required;
- final publishable piece: human approval.

## Initial formats

- static image
- carousel

The design system and real image library will be added in a later handoff. The software should already output a structured `visual_brief`.

## Out of scope for milestone 1

- final graphic generation;
- automatic photo selection;
- social publishing;
- external fact enrichment;
- live regulatory verification;
- scraping;
- CRM or ad platform integrations.
