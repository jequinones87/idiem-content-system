"""Grilla mensual — "Grilla + copy editable".

Renderiza los 12 posts del mes como una grilla de piezas terminadas (formato
Servicios/Plantilla 01) + el copy editable + el graphic_brief/trazabilidad de
cada uno, tal como el flujo mensual de revisión.

Data-driven: toma el plan real de `compose_month` (célula, subtema, formato,
photo_selection, evidencia) y le agrega la capa visual (titular gráfico, bajada)
y el copy publicable ya validado. No inventa evidencia: cada pieza traza a su
knowledge_id y su foto (librería o Muapi) sale de photo_selection.

Dos acabados legítimos del feed IDIEM:
  - photo-field: foto real de la librería incrustada (data URI).
  - solid brand-field: campo gris de marca; la foto (librería pesada o Muapi
    generada) se incrusta en la plataforma. El link Muapi abre la imagen real.

Uso:
  PYTHONPATH=src python3 design_system/gen_month_grid.py > design_system/plantilla_grilla_mes.html
"""
from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from idiem.loader import load_knowledge_base  # noqa: E402
from idiem.review import compose_month, set_post_copy  # noqa: E402

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

# Mes activo del sistema. La memoria de los meses anteriores vive en
# content/archive/AAAA-MM.{json,md}; las fotos por mes en assets/month/AAAA-MM/.
MONTH_ID = "2026-10"
MONTH = ASSETS / "month" / MONTH_ID   # fotos del mes activo (pNN.jpg por seq)

# --- Curación del mes (memoria de contenidos: NO repetir el mes anterior) -----
# knowledge_ids publicados en 2026-09 (se excluyen para rotar subtemas/ángulos).
PREV_PUBLISHED = [
    "KB-IHA-001", "KB-IHA-005", "KB-IHA-006",
    "KB-IOM-011", "KB-IOM-043", "KB-IOM-056",
    "KB-IPR-008", "KB-IPR-021", "KB-IPR-024",
    "KB-LMD-001", "KB-LMD-010", "KB-LMD-020",
]
# Las 12 piezas elegidas para octubre (subtemas frescos + efemérides: 5-oct
# Arquitectura, 13-oct Reducción del Riesgo de Desastres, 17-oct Día del Geólogo)
# y el mix por célula (IOM5 / IPR4 / LMD2 / IHA1). Determinista: se restringe cada
# célula a estas piezas y el planner arma el plan; cada pieza traza a su 2A.2.
MONTH_PICKS = [
    "KB-IOM-065", "KB-IOM-047", "KB-IOM-063", "KB-IOM-004", "KB-IOM-030",
    "KB-IPR-018", "KB-IPR-005", "KB-IPR-002", "KB-IPR-016",
    "KB-LMD-004", "KB-LMD-007",
    "KB-IHA-002",
]
MONTH_WEIGHTS = {
    "INFRA OPERACIÓN MINERA": 5,
    "INFRA PÚBLICA RESILIENTE": 4,
    "LAB MINERO DIGITAL": 2,
    "INFRA HOSPITALARIA Y ASISTENCIAL": 1,
}
_CURATED_CELLS = list(MONTH_WEIGHTS)


def _svg_data_uri(path: Path) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode()


def _ring_path(path: Path) -> str:
    """Extrae el trazo del anillo geométrico de marca (viewBox 0 0 850 850)."""
    svg = path.read_text(encoding="utf-8")
    for d in re.findall(r'd="([^"]+)"', svg):
        if d.lstrip().startswith("M"):
            return d
    raise ValueError(f"no ring path in {path}")


# ---- recursos oficiales compartidos (idénticos a Plantilla 01) --------------
# Reconstruidos desde los SVG versionados en assets/. Antes vivían en un
# scratchpad efímero de sesión, lo que rompía la reproducibilidad del pipeline
# (el import fallaba en cualquier máquina nueva). Ahora la fuente es el repo.
# Nota: si se hace un re-render completo (emit→render), verificar una lámina
# contra la gráfica publicada antes de republicar (fidelidad de logo/slogan).
SLOGAN = _svg_data_uri(ASSETS / "eslogan_idiem_3_blanco.svg")
LOGO = _svg_data_uri(ASSETS / "logo_idiem_oficial.svg")
RING = _ring_path(ASSETS / "circulo_geometrico.svg")


def data_uri(path: Path) -> str:
    b = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/jpeg;base64,{b}"


# ---- copy publicable octubre 2026 (validado con ingest_draft) --------------
# Clave = knowledge_id (no content_id): así el copy no se rompe si cambian los seq.
# compose_current() lo aplica al content_id que arme el plan para cada pieza.
COPY = {
 "KB-IHA-002": {  # IHA · Ingeniería contractual (Salud) — diagnóstico/reclamos
  "hook": "🏥 En un proyecto de salud, una controversia contractual mal gestionada puede frenar la obra y tensionar a las partes.",
  "body": ("Cuando surge un desacuerdo por plazos, alcances o costos, decidir sin un diagnóstico técnico claro suele "
    "agravar el conflicto y postergar la puesta en marcha de una obra crítica para las personas. ⚖️\n\n"
    "En #IDIEM, dentro de nuestra Ingeniería Contractual para el sector Salud, entregamos:\n\n"
    "* Diagnóstico contractual del estado del contrato y sus controversias.\n"
    "* Análisis de prefactibilidad de un reclamo, para evaluar su sustento técnico.\n"
    "* Apoyo técnico para lograr acuerdos entre las partes.\n\n"
    "Respaldo técnico e imparcial para resolver sin improvisar y sostener el avance de la obra. ✅"),
  "cta": "¿Enfrentas una controversia contractual en salud? Conversemos en https://idiem.cl 👉\n\n#IDIEM #InfraestructuraHospitalaria #Salud #IngenieríaContractual"},

 "KB-IOM-047": {  # IOM · Vulnerabilidad e integridad estructural (13-oct RRD, carrusel)
  "hook": "🛡️ El 13 de octubre es el Día Internacional para la Reducción del Riesgo de Desastres. Una estructura vulnerable es un riesgo que no siempre se ve.",
  "body": ("Fisuras, deformaciones y corrosión avanzan en silencio en soportes, edificios industriales, fundaciones, "
    "muros, túneles y relaves. Sin conocer su estado real, la operación queda expuesta. 🔎\n\n"
    "En #IDIEM realizamos inspecciones estructurales especializadas y peritajes, evaluando fisuras, deformaciones y "
    "corrosión bajo gestión de riesgos y cumplimiento normativo. Sumamos levantamiento en terreno con inspección "
    "visual, aérea y termográfica, y modelos 3D con escáner láser y dron. 🛰️📐\n\n"
    "Conocer la vulnerabilidad es el primer paso para reducir el riesgo. ✅"),
  "cta": "¿Necesitas evaluar la integridad de tus estructuras? Conversemos en https://idiem.cl 👉\n\n#IDIEM #Minería #ReducciónDelRiesgo #IntegridadEstructural #Seguridad"},

 "KB-IPR-018": {  # IPR · Sustentabilidad y Arquitectura (5-oct Día de la Arquitectura)
  "hook": "🏛️ En el Día Mundial de la Arquitectura celebramos que diseñar hoy también es diseñar para un futuro sostenible.",
  "body": ("La arquitectura y la infraestructura pública enfrentan un desafío: reducir su impacto ambiental sin "
    "resignar calidad ni funcionalidad. 🌱\n\n"
    "En #IDIEM aportamos soluciones sostenibles para infraestructura, ciudades y edificaciones, con planes y estudios "
    "de cambio climático para el territorio y las comunas: cálculo de huella de carbono e hídrica, análisis "
    "energéticos, ciclo de vida de materiales y estudios de reciclaje. ♻️📊\n\n"
    "Ciencia e ingeniería para una edificación pública más eficiente y responsable. ✅"),
  "cta": "¿Tu proyecto busca ser más sostenible? Conversemos en https://idiem.cl 👉\n\n#IDIEM #DíaDeLaArquitectura #Sustentabilidad #CambioClimático #EdificaciónPública"},

 "KB-LMD-004": {  # LMD · Geotecnia y rocas (17-oct Día del Geólogo — saludo + contenido)
  "hook": "⛏️ Hoy es el Día del Geólogo en Chile. Saludamos a quienes leen la tierra para que la infraestructura se construya sobre bases firmes.",
  "body": ("La geología aplicada es clave en minería y obras: entender el macizo rocoso permite tomar mejores "
    "decisiones de diseño y de operación. 🪨\n\n"
    "En #IDIEM acompañamos ese trabajo con ensayos convencionales y especiales de mecánica de rocas para la "
    "caracterización del macizo rocoso: compresión no confinada (UCS), triaxiales, carga puntual (PLT), tracción "
    "indirecta, velocidad de ondas, hinchamientos y difracción de rayos X (DRX). 🔬\n\n"
    "Ciencia y ensayos al servicio de la geología y la ingeniería del país. ✅"),
  "cta": "¡Feliz día a las y los geólogos! 👷 ¿Necesitas ensayos de mecánica de rocas? Conversemos en https://idiem.cl 👉\n\n#IDIEM #DíaDelGeólogo #Geotecnia #Minería #MecánicaDeRocas"},

 "KB-IOM-065": {  # IOM · Confiabilidad de materiales metálicos y poliméricos
  "hook": "🔩 En una faena, un material que falla antes de tiempo puede detener la operación y poner en riesgo la seguridad.",
  "body": ("Cuando un componente metálico o polimérico se comporta distinto a lo esperado, entender por qué es clave "
    "para evitar que vuelva a ocurrir. 🔍\n\n"
    "En #IDIEM evaluamos la confiabilidad de los materiales usados en elementos mecánicos y estructuras, con un "
    "equipo especializado en metalurgia, mecánica, química y estructuras, apoyado en tecnología de laboratorio para "
    "el análisis de materiales metálicos y poliméricos. 🧪\n\n"
    "Evidencia técnica para anticipar fallas y respaldar la confiabilidad de tus activos. ✅"),
  "cta": "¿Necesitas evaluar la confiabilidad de tus materiales? Conversemos en https://idiem.cl 👉\n\n#IDIEM #Minería #Materiales #Confiabilidad #Ingeniería"},

 "KB-IPR-016": {  # IPR · Tecnología de la construcción (edificación pública)
  "hook": "🏢 Innovar en construcción pública exige una pregunta previa: ¿este material o sistema cumple realmente el estándar?",
  "body": ("Incorporar nuevas soluciones sin validación técnica puede comprometer la calidad y la seguridad de una "
    "obra que usarán miles de personas. 🔎\n\n"
    "En #IDIEM ofrecemos Servicios de Tecnología de la Construcción y acompañamos procesos de innovación en la "
    "edificación pública, con ensayos y certificaciones de materiales, componentes y sistemas para verificar el "
    "cumplimiento de estándares de calidad y seguridad. 🧪📋\n\n"
    "Innovación respaldada por evidencia técnica. ✅"),
  "cta": "¿Buscas validar materiales o sistemas para edificación pública? Conversemos en https://idiem.cl 👉\n\n#IDIEM #EdificaciónPública #Innovación #Ensayos #Construcción"},

 "KB-LMD-007": {  # LMD · Triaxial suelos de partículas grandes (carrusel, SIN superlativos)
  "hook": "🪨 Muchos suelos reales tienen partículas demasiado grandes para los equipos de ensayo convencionales.",
  "body": ("En presas de tierra, gran minería, energía e infraestructura, ensayar el material tal como es —con sus "
    "partículas de gran tamaño— es clave para caracterizarlo bien y diseñar con seguridad. 🔬\n\n"
    "En #IDIEM contamos con un equipo Triaxial para grandes partículas, desarrollado con ingeniería propia, que "
    "permite ensayar suelos de gran tamaño y obtener parámetros representativos para el diseño geotécnico. 📐\n\n"
    "Ensayos que reflejan el material real, no una versión reducida de él. ✅"),
  "cta": "¿Necesitas ensayar suelos de partículas grandes? Conversemos en https://idiem.cl 👉\n\n#IDIEM #Geotecnia #Minería #Ensayos #PresasDeTierra"},

 "KB-IOM-004": {  # IOM · Modelamiento digital / BIM (minería)
  "hook": "🏗️ En un proyecto de infraestructura minera, la falta de información confiable del estado real dispara los imprevistos.",
  "body": ("Coordinar disciplinas sobre datos incompletos multiplica errores, retrabajos y sorpresas en obra. 🧭\n\n"
    "En #IDIEM abordamos la ingeniería de apoyo para proyectos mineros con un equipo multidisciplinario: ingeniería "
    "civil, mecánica y geomensura, modelación BIM y mantenimiento industrial, partiendo por el levantamiento de las "
    "condiciones existentes en las distintas disciplinas. 📐📊\n\n"
    "Una base digital y multidisciplinaria para decidir con información confiable. ✅"),
  "cta": "¿Tu proyecto minero necesita ingeniería de apoyo con BIM? Conversemos en https://idiem.cl 👉\n\n#IDIEM #Minería #BIM #Ingeniería #ModelamientoDigital"},

 "KB-IPR-002": {  # IPR · Peritaje de componentes metálicos (carrusel) — reemplaza incendios
  "hook": "🔧 Cuando un componente metálico falla, la pregunta clave no es solo qué se rompió, sino por qué.",
  "body": ("Un perno, un eje, un engranaje o una tubería que falla puede detener una operación o comprometer la "
    "seguridad. Sin un peritaje riguroso, la causa queda sin resolver y el riesgo permanece. 🔎\n\n"
    "En #IDIEM realizamos estudios de falla de componentes, con peritajes a pernos, ejes, engranajes y tuberías, y "
    "también evaluamos el daño del pavimento en autopistas. Determinamos qué ocurrió y entregamos evidencia técnica "
    "para decidir. 🧪📐\n\n"
    "Entender la falla es el primer paso para evitar que se repita. ✅"),
  "cta": "¿Necesitas peritar la falla de un componente? Conversemos en https://idiem.cl 👉\n\n#IDIEM #Peritajes #Materiales #Ingeniería #Confiabilidad"},

 "KB-IOM-063": {  # IOM · Cumplimiento normativo (carrusel)
  "hook": "📋 En una obra o instalación, incumplir la normativa no siempre se nota… hasta que llega una auditoría o una falla.",
  "body": ("Detectar las brechas normativas a tiempo evita sobrecostos, detenciones y riesgos para las personas. 🔍\n\n"
    "En #IDIEM realizamos revisión de cumplimiento normativo en tres ámbitos —estructural, incendios y "
    "especialidades—, identificando las brechas respecto de los marcos aplicables. 🛡️📐\n\n"
    "Una mirada técnica e independiente para operar con respaldo y sin sorpresas. ✅"),
  "cta": "¿Necesitas revisar el cumplimiento normativo de tu proyecto? Conversemos en https://idiem.cl 👉\n\n#IDIEM #CumplimientoNormativo #Ingeniería #Seguridad #Calidad"},

 "KB-IPR-005": {  # IPR · Evaluación estructural de puentes (capacidad de carga)
  "hook": "🌉 Un puente conecta territorios y sostiene la vida de las comunidades: saber cuánta carga resiste no es un detalle.",
  "body": ("Con el paso del tiempo y el aumento del tránsito, un puente puede quedar exigido más allá de lo previsto. "
    "Evaluar su capacidad real es clave para decidir con seguridad. 🔎\n\n"
    "En #IDIEM evaluamos la capacidad de carga de puentes con diagnóstico, ensayos, modelación por elementos finitos, "
    "levantamiento topográfico del trazado y análisis de alternativas de diseño, como en el estudio estructural del "
    "Puente Cortés. 📐📊\n\n"
    "Evidencia técnica para resguardar la seguridad y la conectividad del territorio. ✅"),
  "cta": "¿Necesitas evaluar la capacidad de un puente? Conversemos en https://idiem.cl 👉\n\n#IDIEM #Puentes #Infraestructura #Ingeniería #Estructuras"},

 "KB-IOM-030": {  # IOM · Revisión integral de rehabilitación
  "hook": "🏗️ Rehabilitar una estructura compleja sin un diagnóstico completo es avanzar a ciegas.",
  "body": ("Intervenir sin conocer el estado real, sin ensayos que lo respalden ni alternativas evaluadas, encarece "
    "la obra y arriesga el resultado. 🔍\n\n"
    "En #IDIEM abordamos la revisión integral de proyectos complejos de rehabilitación en cuatro etapas:\n\n"
    "* Levantamiento de las condiciones existentes.\n"
    "* Soporte de nuestros laboratorios.\n"
    "* Diagnóstico y evaluación de alternativas.\n"
    "* Ingeniería de rehabilitación.\n\n"
    "Un proceso ordenado para intervenir con respaldo técnico de principio a fin. ✅"),
  "cta": "¿Tienes un proyecto de rehabilitación estructural? Conversemos en https://idiem.cl 👉\n\n#IDIEM #Rehabilitación #Ingeniería #Estructuras #Minería"},
}

# ---- capa visual: titular gráfico (dentro del círculo) + bajada -------------
# Keyed por seq (orden determinista del plan de octubre). msg: <br> = 2 líneas.
GRAPHIC = {
 1:  {"svc": "Ingeniería contractual",          "msg": "Claridad ante<br>la controversia.", "base": "Diagnóstico · reclamos · <b>sector Salud</b>"},
 2:  {"svc": "Integridad estructural",          "msg": "Reducir<br>el riesgo.",             "base": "Fisuras · corrosión · <b>láser y dron</b>"},
 3:  {"svc": "Sustentabilidad y arquitectura",  "msg": "Construir<br>sostenible.",          "base": "Huella C e hídrica · <b>ciclo de vida</b>"},
 4:  {"svc": "Mecánica de rocas",               "msg": "Leer el<br>macizo rocoso.",         "base": "UCS · triaxiales · <b>caracterización</b>"},
 5:  {"svc": "Confiabilidad de materiales",     "msg": "Anticiparse<br>a la falla.",        "base": "Metálicos · poliméricos · <b>laboratorio</b>"},
 6:  {"svc": "Tecnología de la construcción",   "msg": "Innovar con<br>respaldo.",          "base": "Ensayos · certificación · <b>edificación pública</b>"},
 7:  {"svc": "Triaxial grandes partículas",     "msg": "Ensayar el<br>material real.",      "base": "Suelos de gran tamaño · <b>presas de tierra</b>"},
 8:  {"svc": "Ingeniería de apoyo · BIM",       "msg": "Decidir con<br>datos reales.",      "base": "Civil · mecánica · <b>modelación BIM</b>"},
 9:  {"svc": "Peritaje de componentes",         "msg": "¿Por qué<br>falló?",                "base": "Pernos · ejes · <b>engranajes y tuberías</b>"},
 10: {"svc": "Cumplimiento normativo",          "msg": "Cerrar las<br>brechas.",            "base": "Estructural · incendios · <b>especialidades</b>"},
 11: {"svc": "Evaluación de puentes",           "msg": "¿Cuánta carga<br>resiste?",         "base": "Capacidad de carga · <b>elementos finitos</b>"},
 12: {"svc": "Revisión de rehabilitación",      "msg": "Intervenir<br>con respaldo.",       "base": "Levantamiento · diagnóstico · <b>ingeniería</b>"},
}

# seq -> foto de librería incrustada (data URI). Octubre: se bajan de la librería
# de Drive y se hornean en assets/month/2026-10/pNN.jpg (resueltas por resolve_photo).
PHOTO_FILE = {}

# seq -> URL Muapi generada. Sin Muapi este mes.
MUAPI_URL = {}

CELL_SHORT = {
 "INFRA PÚBLICA RESILIENTE": "IPR",
 "INFRA HOSPITALARIA Y ASISTENCIAL": "IHA",
 "INFRA CRÍTICA TRANSPORTE": "ICT",
 "INFRA OPERACIÓN MINERA": "IOM",
 "LAB MINERO DIGITAL": "LMD",
}


def esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def canvas(seq: int, cell_short: str, photo_uri: str | None, finish: str,
           corner_logo: str | None = None, side: str = "left") -> str:
    g = GRAPHIC[seq]
    if photo_uri:
        bg = (f'<div class="photo" style="background-image:url(\'{photo_uri}\')"></div>'
              '<div class="legibility"></div>')
    else:
        bg = f'<div class="solidfield"></div><div class="legibility soft"></div>'
    seal = (f'<img class="cornerlogo" src="{corner_logo}" alt="Certificación Green Hospital IDIEM">'
            if corner_logo else "")
    side_cls = " circ-right" if side == "right" else ""
    return f'''<div class="canvas{side_cls}" data-finish="{finish}">
  {bg}
  <img class="slogan" src="{SLOGAN}" alt="Elige bien. Elige idiem.">
  <img class="logo" src="{LOGO}" alt="Logo IDIEM">
  <div class="circle-wrap">
    <svg viewBox="0 0 850 850" aria-hidden="true"><path class="ring" d="{RING}"/></svg>
    <div class="circle-msg">
      <div class="svc">{esc(g["svc"])}</div>
      <div class="msg">{g["msg"]}</div>
    </div>
  </div>
  <div class="baseline">{g["base"]}</div>
  {seal}
</div>'''


def copy_panel(cid: str, kid: str, seq: int) -> str:
    c = COPY[kid]  # COPY keyed por knowledge_id; cid (content_id) es la clave de estado
    full = c["hook"] + "\n\n" + c["body"] + "\n\n" + c["cta"]
    words = len(full.split())
    return f'''<div class="copy">
  <div class="copyhead">
    <span class="lbl">Copy editable</span>
    <span class="wc">{words} palabras</span>
    <button class="cpbtn" data-cid="{esc(cid)}">Copiar</button>
  </div>
  <textarea class="edit hook" data-cid="{esc(cid)}" data-part="hook" spellcheck="false">{esc(c["hook"])}</textarea>
  <textarea class="edit body" data-cid="{esc(cid)}" data-part="body" spellcheck="false">{esc(c["body"])}</textarea>
  <textarea class="edit cta" data-cid="{esc(cid)}" data-part="cta" spellcheck="false">{esc(c["cta"])}</textarea>
</div>'''


def source_row(seq: int, ps: dict) -> str:
    src = (ps or {}).get("source")
    if src == "library":
        pid = ps.get("photo_id", "")
        fu = ps.get("fuente", "")
        return (f'<span class="k">Foto</span><span class="v">Librería · <code>{esc(pid)}</code> '
                f'· <a href="{esc(fu)}" target="_blank" rel="noopener">ver en Drive</a></span>')
    if src == "muapi":
        url = MUAPI_URL.get(seq)
        if url:
            link = f'<a href="{esc(url)}" target="_blank" rel="noopener">ver imagen generada ↗</a>'
        else:
            link = '<span class="pending">generación en curso</span>'
        return (f'<span class="k">Foto</span><span class="v">Muapi (generada) · {link}<br>'
                f'<span class="muprompt">{esc((ps.get("prompt") or "")[:180])}…</span></span>')
    return ('<span class="k">Foto</span><span class="v">Sin foto — por diseño '
            '(<code>needs_photo=false</code>): evidencia contractual, campo de marca sólido.</span>')


def finish_tag(seq: int, ps: dict) -> tuple[str, str]:
    """Return (finish_key, human_note) for tile styling + caption."""
    if seq in PHOTO_FILE:
        return "photo", "Foto real de librería incrustada"
    src = (ps or {}).get("source")
    if src == "muapi":
        return "muapi", "Foto Muapi generada · se incrusta en la plataforma"
    if src == "library":
        return "libpend", "Foto de librería lista · se incrusta en la plataforma"
    return "text", "Campo de marca sólido (sin foto por diseño)"


def card(post, seq: int) -> str:
    cid = post.content_id
    cell = post.cell
    cshort = CELL_SHORT.get(cell, cell[:3].upper())
    sub = post.subtheme if isinstance(post.subtheme, dict) else {}
    subname = sub.get("nombre") if isinstance(sub, dict) else (post.subtheme or "")
    gb = post.graphic_brief or {}
    ps = gb.get("photo_selection") or {}
    fmt = gb.get("recommended_format") or "STATIC"

    finish, fnote = finish_tag(seq, ps)
    photo_uri = data_uri(MONTH / PHOTO_FILE[seq]) if seq in PHOTO_FILE else None

    ev = gb.get("evidence_ids") or []
    ev_codes = " · ".join(f"<code>{esc(e)}</code>" for e in ev[:4]) or f"<code>{esc(post.knowledge_id)}</code>"

    return f'''<article class="card">
  <div class="stage">
    {canvas(seq, cshort, photo_uri, finish)}
    <p class="cap"><span class="fdot {finish}"></span>{esc(fnote)}</p>
  </div>
  <div class="side">
    <div class="ctop">
      <span class="seq">{seq:02d}</span>
      <span class="badge">{cshort}</span>
      <span class="badge ghost">{esc(fmt)}</span>
      <span class="sub">{esc(subname or "")}</span>
    </div>
    {copy_panel(cid, post.knowledge_id, seq)}
    <div class="trace">
      <div class="trrow"><span class="k">Post ancla</span><span class="v"><code>{esc(cid)}</code></span></div>
      <div class="trrow"><span class="k">Evidencia</span><span class="v">{ev_codes}</span></div>
      <div class="trrow">{source_row(seq, ps)}</div>
    </div>
  </div>
</article>'''


def compose_current(kb):
    """Compone el mes activo (MONTH_ID) con la curación editorial + copy aplicado.

    Restringe cada célula a MONTH_PICKS (excluye todo lo demás, incluido lo
    publicado el mes anterior) y fija el mix por célula con MONTH_WEIGHTS, de modo
    que el plan determinista quede con exactamente las 12 piezas elegidas, cada una
    trazada a su knowledge_id (2A.2). Devuelve el review con el copy ya aplicado.
    Es la fuente única de composición para la grilla, la workstation y el archivo.
    """
    exclude = [
        it.knowledge_id
        for cell in _CURATED_CELLS
        for it in kb.items_in_cell(cell)
        if it.knowledge_id not in MONTH_PICKS
    ]
    review = compose_month(kb, MONTH_ID, target_count=12,
                           recent_history=exclude, weights=MONTH_WEIGHTS)
    # COPY está keyed por knowledge_id; se aplica al content_id que armó el plan.
    for post in review.posts:
        c = COPY.get(post.knowledge_id)
        if c:
            set_post_copy(review, post.content_id, c)
    return review


def main() -> None:
    kb = load_knowledge_base()
    review = compose_current(kb)

    cards = "\n".join(card(p, i) for i, p in enumerate(review.posts, 1))
    n_photo = len(PHOTO_FILE)
    n_muapi = sum(1 for p in review.posts if ((p.graphic_brief or {}).get("photo_selection") or {}).get("source") == "muapi")
    n_text = sum(1 for p in review.posts if not ((p.graphic_brief or {}).get("photo_selection") or {}))

    print(TEMPLATE.replace("__CARDS__", cards)
                  .replace("__NPHOTO__", str(n_photo))
                  .replace("__NMUAPI__", str(n_muapi))
                  .replace("__NTEXT__", str(n_text)))


TEMPLATE = r'''<title>Grilla Octubre IDIEM</title>
<meta name="description" content="Los 12 posts de septiembre de IDIEM como grilla de piezas terminadas (formato Servicios) con copy editable y trazabilidad de evidencia y foto por post.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900&display=swap">
<style>
:root{
  --red:#e1261d;--gray-blue:#666d72;--gray-light:#efefef;--gray-dark:#2f3030;
  --ink:#22262a;--paper:#f2f2ef;--card:#ffffff;--line:rgba(47,48,48,.12);
  --muted:#6a7075;--field-a:#33383a;--field-b:#22282b;
  --shadow:0 20px 50px -26px rgba(47,48,48,.42);--mono:"Montserrat",system-ui,sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ink:#eef0f0;--paper:#141617;--card:#1d2021;--gray-light:#282b2c;
  --line:rgba(239,239,239,.13);--muted:#9aa1a5;--shadow:0 24px 64px -30px rgba(0,0,0,.78);
}}
:root[data-theme="dark"]{
  --ink:#eef0f0;--paper:#141617;--card:#1d2021;--gray-light:#282b2c;
  --line:rgba(239,239,239,.13);--muted:#9aa1a5;--shadow:0 24px 64px -30px rgba(0,0,0,.78);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:var(--mono);background:var(--paper);color:var(--ink);line-height:1.5;
  padding:clamp(18px,3.5vw,52px) clamp(14px,3.5vw,52px) 80px}
.wrap{max-width:1280px;margin:0 auto}
.eyebrow{display:inline-flex;align-items:center;gap:.6em;font-size:.72rem;font-weight:700;
  letter-spacing:.22em;text-transform:uppercase;color:var(--red);margin:0 0 12px}
.eyebrow .dot{width:.5em;height:.5em;border-radius:50%;background:var(--red)}
h1{font-size:clamp(1.8rem,4vw,2.7rem);font-weight:800;letter-spacing:-.02em;line-height:1.04;margin:0 0 .4rem;text-wrap:balance}
h1 b{color:var(--red)}
.lede{font-size:clamp(1rem,1.6vw,1.14rem);color:var(--muted);max-width:70ch;margin:0 0 1.2rem}
.legend{display:flex;flex-wrap:wrap;gap:8px 10px;margin:0 0 30px;font-size:.76rem}
.lchip{display:inline-flex;align-items:center;gap:.5em;padding:6px 12px;border:1px solid var(--line);
  border-radius:100px;background:var(--card);font-weight:600}
.fdot{width:.7em;height:.7em;border-radius:50%;flex:none;display:inline-block}
.fdot.photo{background:var(--red)} .fdot.muapi{background:#8a5cf6}
.fdot.libpend{background:#e19a1d} .fdot.text{background:var(--gray-blue)}

.cards{display:grid;grid-template-columns:1fr;gap:22px}
@media(min-width:1080px){.cards{grid-template-columns:1fr 1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;
  box-shadow:var(--shadow);display:flex;flex-direction:column}
@media(min-width:600px){.card{flex-direction:row;align-items:stretch}}
.stage{padding:16px;display:flex;flex-direction:column;gap:8px;flex:none;justify-content:center}
@media(min-width:600px){.stage{width:46%;max-width:340px}}
.cap{margin:0;font-size:.7rem;color:var(--muted);display:flex;align-items:center;gap:.5em;line-height:1.3}

/* ---------- 1080x1080 canvas (Servicios) ---------- */
.canvas{container-type:inline-size;width:100%;aspect-ratio:1/1;position:relative;overflow:hidden;
  border-radius:9px;background:var(--gray-dark);isolation:isolate;color:#fff;user-select:none;box-shadow:0 8px 24px -12px rgba(0,0,0,.5)}
.photo{position:absolute;inset:0;z-index:0;background-size:cover;background-position:50% 45%}
.solidfield{position:absolute;inset:0;z-index:0;
  background:radial-gradient(120% 120% at 78% 12%, var(--field-a) 0%, var(--field-b) 60%, #1a1f21 100%)}
.legibility{position:absolute;inset:0;z-index:1;background:
  linear-gradient(90deg,rgba(0,0,0,.72) 0%,rgba(0,0,0,.4) 40%,rgba(0,0,0,.04) 70%),
  linear-gradient(0deg,rgba(0,0,0,.5) 0%,rgba(0,0,0,0) 30%),
  linear-gradient(180deg,rgba(0,0,0,.32) 0%,rgba(0,0,0,0) 22%)}
.legibility.soft{background:linear-gradient(0deg,rgba(0,0,0,.34) 0%,rgba(0,0,0,0) 40%),
  linear-gradient(180deg,rgba(0,0,0,.22) 0%,rgba(0,0,0,0) 26%)}
.slogan{position:absolute;z-index:3;top:5.4cqw;left:5.4cqw;width:33cqw;height:auto;display:block;
  filter:drop-shadow(0 1px 10px rgba(0,0,0,.4))}
.logo{position:absolute;z-index:3;top:5cqw;right:5.4cqw;width:19cqw;height:auto;display:block;
  filter:drop-shadow(0 1px 10px rgba(0,0,0,.4))}
.circle-wrap{position:absolute;z-index:2;top:50%;left:41%;transform:translate(-50%,-50%);width:80cqw;height:80cqw}
.circle-wrap svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible;filter:drop-shadow(0 2px 18px rgba(0,0,0,.35))}
.circle-wrap .ring{fill:var(--red)}
.circle-msg{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.circle-msg .svc{font-size:2.05cqw;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#fff;margin-bottom:2cqw;opacity:.96;max-width:44cqw}
.circle-msg .msg{font-size:4.35cqw;font-weight:800;line-height:1.14;letter-spacing:-.005em;max-width:56cqw;white-space:nowrap;text-shadow:0 2px 16px rgba(0,0,0,.5)}
.baseline{position:absolute;z-index:3;left:5.4cqw;bottom:5cqw;font-size:2.35cqw;font-weight:500;color:rgba(255,255,255,.94);text-shadow:0 1px 10px rgba(0,0,0,.5)}
.baseline b{font-weight:700}
.cellbadge{position:absolute;z-index:3;right:5.4cqw;bottom:5cqw;font-size:2.1cqw;font-weight:800;letter-spacing:.14em;
  color:#fff;background:rgba(225,38,29,.9);padding:1.1cqw 2.2cqw;border-radius:100px}
.cornerlogo{position:absolute;z-index:1;right:5cqw;bottom:5cqw;width:37cqw;height:auto;display:block;
  border-radius:50%;filter:drop-shadow(0 2px 12px rgba(0,0,0,.45))}
.canvas.circ-right .circle-wrap{left:59%}
.canvas.circ-right .legibility{background:
  linear-gradient(270deg,rgba(0,0,0,.5) 0%,rgba(0,0,0,.22) 42%,rgba(0,0,0,.04) 72%),
  linear-gradient(0deg,rgba(0,0,0,.5) 0%,rgba(0,0,0,0) 30%),
  linear-gradient(180deg,rgba(0,0,0,.32) 0%,rgba(0,0,0,0) 22%)}

/* ---------- side: copy + trace ---------- */
.side{padding:16px 18px 18px;display:flex;flex-direction:column;gap:14px;flex:1;min-width:0;border-left:1px solid var(--line)}
@media(max-width:599px){.side{border-left:0;border-top:1px solid var(--line)}}
.ctop{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.seq{font-size:1.1rem;font-weight:800;color:var(--red)}
.badge{font-size:.68rem;font-weight:800;letter-spacing:.1em;color:#fff;background:var(--gray-dark);padding:3px 9px;border-radius:100px}
.badge.ghost{background:transparent;color:var(--muted);border:1px solid var(--line)}
.sub{font-size:.82rem;font-weight:600;color:var(--muted)}
.copy{display:flex;flex-direction:column;gap:7px}
.copyhead{display:flex;align-items:center;gap:8px}
.copyhead .lbl{font-size:.66rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.copyhead .wc{font-size:.7rem;color:var(--muted);margin-left:auto}
.cpbtn{font-family:inherit;font-size:.7rem;font-weight:700;color:#fff;background:var(--red);border:0;
  padding:5px 12px;border-radius:100px;cursor:pointer}
.cpbtn.done{background:var(--gray-blue)}
.edit{font-family:inherit;width:100%;resize:vertical;border:1px solid var(--line);border-radius:9px;
  background:var(--gray-light);color:var(--ink);padding:9px 11px;font-size:.84rem;line-height:1.5}
.edit:focus{outline:2px solid var(--red);outline-offset:1px;background:var(--card)}
.edit.hook{font-weight:600;min-height:60px}
.edit.body{min-height:150px}
.edit.cta{min-height:70px;color:var(--muted)}
.trace{display:flex;flex-direction:column;gap:7px;border-top:1px solid var(--line);padding-top:12px}
.trrow{display:grid;grid-template-columns:78px 1fr;gap:10px;align-items:start;font-size:.78rem}
.trrow .k{font-size:.62rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);padding-top:2px}
.trrow .v{color:var(--ink);min-width:0;word-break:break-word}
.trrow a{color:var(--red);font-weight:600}
code{font-family:inherit;font-weight:700;background:var(--gray-light);padding:1px 6px;border-radius:5px;font-size:.9em}
.muprompt{color:var(--muted);font-size:.72rem;font-style:italic}
.pending{color:#e19a1d;font-weight:600}
.foot{margin-top:34px;padding-top:18px;border-top:1px solid var(--line);font-size:.78rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px 18px}
.foot code{font-size:.86em}
</style>

<div class="wrap">
  <p class="eyebrow"><span class="dot"></span>IDIEM · Design System · Grilla mensual</p>
  <h1>Octubre — <b>12 posts</b></h1>
  <p class="lede">Cada pieza es un post terminado en formato <strong>Servicios (Plantilla 01)</strong>: recursos oficiales (logo, círculo, eslogan), un mensaje clave acotado a evidencia y la foto que corresponde al servicio. El copy es <strong>editable</strong> —edítalo aquí y cópialo— y cada post traza a su <strong>knowledge_id</strong> y a su foto. Los webinars son un agregado aparte y no ocupan estos 12 espacios.</p>
  <div class="legend">
    <span class="lchip"><span class="fdot photo"></span>__NPHOTO__ con foto real de librería</span>
    <span class="lchip"><span class="fdot muapi"></span>__NMUAPI__ con foto Muapi generada</span>
    <span class="lchip"><span class="fdot libpend"></span>foto de librería lista (se incrusta en plataforma)</span>
    <span class="lchip"><span class="fdot text"></span>__NTEXT__ sin foto por diseño (contractual)</span>
  </div>

  <div class="cards">
__CARDS__
  </div>

  <div class="foot">
    <span>Motor: <code>compose_current(2026-10)</code> · copy validado con <code>ingest_draft</code>.</span>
    <span>Foto: <code>photo_selection</code> (librería/Muapi) · fallback Muapi solo si ninguna foto de librería corresponde.</span>
    <span>Reglas: 2A.2 fuente de verdad · GR-04 sin superlativos · NAME_ONLY.</span>
  </div>
</div>

<script>
(function(){
  var KEY='idiem_sep_copy_v1';
  var store={};
  try{store=JSON.parse(localStorage.getItem(KEY)||'{}')||{};}catch(e){store={};}
  var areas=document.querySelectorAll('textarea.edit');
  areas.forEach(function(t){
    var cid=t.getAttribute('data-cid'),part=t.getAttribute('data-part');
    if(store[cid]&&typeof store[cid][part]==='string'){t.value=store[cid][part];}
    autosize(t);
    t.addEventListener('input',function(){
      autosize(t);
      if(!store[cid])store[cid]={};
      store[cid][part]=t.value;
      try{localStorage.setItem(KEY,JSON.stringify(store));}catch(e){}
    });
  });
  function autosize(t){t.style.height='auto';t.style.height=(t.scrollHeight+2)+'px';}
  document.querySelectorAll('.cpbtn').forEach(function(b){
    b.addEventListener('click',function(){
      var cid=b.getAttribute('data-cid');
      var parts=['hook','body','cta'].map(function(p){
        var el=document.querySelector('textarea[data-cid="'+CSS.escape(cid)+'"][data-part="'+p+'"]');
        return el?el.value:'';
      });
      var text=parts.join('\n\n');
      var done=function(){var o=b.textContent;b.textContent='Copiado ✓';b.classList.add('done');
        setTimeout(function(){b.textContent=o;b.classList.remove('done');},1400);};
      if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text).then(done,done);}
      else{var ta=document.createElement('textarea');ta.value=text;document.body.appendChild(ta);ta.select();
        try{document.execCommand('copy');}catch(e){}document.body.removeChild(ta);done();}
    });
  });
})();
</script>'''


if __name__ == "__main__":
    main()
