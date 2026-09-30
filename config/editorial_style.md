# Guía editorial IDIEM — copies de LinkedIn

> ⚠️ **Actualizado 30-09-2026 (auditoría de sesgos).** Ya no existe un arquetipo ni una
> estructura únicos. La diversidad (arquetipos, hooks, CTA por intención, límites) y la
> longitud se rigen por `docs/10_ESTRATEGIA_EDITORIAL_Y_SESGOS.md` y
> `config/editorial_diversity.json`, que **mandan sobre esta guía**. Desde noviembre 2026.

> Derivada del corpus real publicado (jun–jul 2026). Gobierna la **forma** del
> copy. La **sustancia técnica** siempre se acota a la evidencia trazable del fact
> sheet (CLAUDE.md reglas 2–3): nunca se inventan servicios, cifras, clientes ni
> resultados. Externa y configurable (`config/editorial_style.json`).

## Voz

- **Quién habla:** IDIEM en 1ª persona plural (*nosotros / nuestro*), invitando al
  lector en 2ª persona (*tú / te*).
- **Registro:** profesional, técnico y **consultivo**. Sobrio, sin superlativos ni
  autobombo.
- **A quién:** al profesional del sector (mandante, contratista, especialista).

## Estructura

La secuencia *hook → problema → "En #IDIEM…" → impacto → CTA* es **solo uno** de los
arquetipos (`problem_impact_capability`), **no el default**. Cada post recibe su arquetipo,
hook_type y cta_type **antes** de redactar (ver doc 10). Regla general: el conocimiento
técnico aporta valor **antes** que lo comercial; no todos los posts abren con el problema,
ni nombran a IDIEM en el mismo lugar, ni terminan en venta explícita.

## Longitud (regla única, en caracteres)

- **Máximo 900 caracteres**; objetivo habitual **820–880**. Se valida en caracteres.
- Si la evidencia no alcanza: post **más corto y honesto**; si es insuficiente,
  marcar **`EXPERT_INPUT_REQUIRED`**. Nunca rellenar con datos no respaldados.

## Emojis

- Medidos y temáticos (**máximo 1–2 por párrafo**): 🏗️ 🏥 ⚙️ 📐 🛡️ 🔍 ⚠️ 📊 ✅ 👷 🌐 👉
- Nunca dentro de un término técnico o una norma. No abrir todos los párrafos con
  emoji.

## Hashtags

- Siempre **#IDIEM**.
- **Inline:** 1–3 términos clave como hashtag dentro del texto.
- **Bloque de cierre:** 4–6 hashtags. Vocabulario por célula:

| Célula | Hashtags base |
|---|---|
| Infra Pública Resiliente | #Infraestructura #ObrasPúblicas #Construcción #Ingeniería #Calidad |
| Hospitalaria y Asistencial | #InfraestructuraHospitalaria #Hospital #Salud #Ingeniería #Construcción |
| Operación Minera | #Minería #Ingeniería #Mantenimiento #Seguridad #Confiabilidad |
| Lab Minero Digital | #Minería #Ensayos #Laboratorio #Calidad #Tecnología |

Tags de tema (según corresponda): #IngenieríaMecánica #Ensayos #Geotecnia
#Estructuras #Incendios #Acústica #Sustentabilidad #BIM #Auditoria.

## Dolor prioritario por célula (organismos públicos)

Insight del equipo comercial: para **Infra Pública**, **Hospitalaria** y **Transporte**,
el dolor más relevante del mandante es el **atraso en la ejecución de las obras**.

- Es **guía de forma** (enmarca el problema del lector en el hook/problema), **no un
  hecho de IDIEM**: la sustancia técnica sigue acotada a `allowed_facts`.
- **Opcional y pertinente:** encabezar con este dolor cuando el servicio del post lo
  resuelva o mitigue (inspección técnica, control de calidad, diagnóstico, ingeniería
  contractual, programación de obra). **No** usar en todos los posts ni repetir la
  misma frase; no aplicar cuando el ángulo es otro (p. ej. sostenibilidad / Green
  Hospital).
- Vive en `config/editorial_style.json` → `pain_points_by_cell` (configurable).

## Sí / No

**Sí:** anclar cada afirmación a la evidencia · nombrar métodos/normas solo si están
respaldados · rotar arquetipo, hook_type y cta_type (doc 10) · elegir el CTA por intención · mantener `DRAFT` hasta aprobación humana.

**No:** inventar servicios/cifras/clientes/resultados · rankings/superlativos/
exclusividades (GR-04) · expandir términos `NAME_ONLY` · prometer resultados no
respaldados · abusar de emojis o signos de exclamación · usar `contact` como CTA por
defecto · repetir textual "Contáctanos y conversemos sobre tu caso" / "Contáctanos a
través de nuestros canales oficiales".
