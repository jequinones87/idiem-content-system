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
MONTH = ASSETS / "month"
SCRATCH = Path("/tmp/claude-0/-home-user-idiem-content-system/"
               "1c5b178b-f8ee-5946-beb8-9cf3fffd70df/scratchpad")

# ---- recursos oficiales compartidos (idénticos a Plantilla 01) --------------
SLOGAN = (SCRATCH / "_slogan.txt").read_text().strip()
LOGO = (SCRATCH / "_logo.txt").read_text().strip()
RING = (SCRATCH / "_ring.txt").read_text().strip()


def data_uri(path: Path) -> str:
    b = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/jpeg;base64,{b}"


# ---- copy publicable (validado con ingest_draft en sesión) ------------------
COPY = {
 "PLAN-KB-IHA-005-01": {
  "hook": ("¿Tu obra de salud está cumpliendo el programa?\n\n"
    "🏥 En proyectos públicos de salud, cada atraso importa. Una desviación en los plazos puede postergar la "
    "puesta en marcha de infraestructura crítica para las personas y generar importantes impactos "
    "contractuales y económicos."),
  "body": ("Muchas veces, el problema no está solo en el atraso observado, sino en cómo se planifica, actualiza y "
    "controla la programación de la obra.\n\n"
    "En IDIEM, a través de nuestra Ingeniería Contractual, realizamos análisis técnicos de programación para "
    "proyectos del sector Salud, que permiten:\n\n"
    "* Identificar desviaciones respecto del programa contractual.\n"
    "* Analizar las causas y evolución de los atrasos.\n"
    "* Evaluar sus efectos sobre los plazos de ejecución.\n"
    "* Generar respaldo técnico para la gestión de contratos y reclamaciones.\n\n"
    "Anticiparse al atraso también es parte de una buena gestión contractual."),
  "cta": "📩 ¿Necesitas analizar la programación de tu proyecto? Contáctanos y conversemos sobre tu caso.\n\n#IDIEM #IngenieríaContractual #Construcción #Infraestructura #Salud #GestiónDeProyectos #AnálisisDeAtrasos"},

 "PLAN-KB-IOM-011-02": {
  "hook": "🔥 Cuando se produce un incendio en faena, las consecuencias pueden comprometer la seguridad de las personas y afectar seriamente la continuidad operacional.",
  "body": ("Un peritaje oportuno, riguroso e imparcial permite establecer el origen y la causa del siniestro, pero "
    "también obtener información clave para tomar decisiones y reducir la probabilidad de que un evento similar "
    "vuelva a ocurrir. 🔍\n\n"
    "En #IDIEM realizamos peritajes de incendio causa-origen, además de peritajes estructurales y mecánicos en "
    "minería. Este trabajo puede complementarse con estudios de riesgo de incendio, identificando "
    "vulnerabilidades en las instalaciones y definiendo medidas de mitigación. 🛡️📐\n\n"
    "Evidencia técnica para entender lo ocurrido, identificar brechas y fortalecer la seguridad y continuidad "
    "de la operación. ✅"),
  "cta": "¿Necesitas un peritaje de incendio o evaluar el riesgo de tus instalaciones? Contáctanos a través de nuestros canales oficiales 👉 https://idiem.cl\n\n#IDIEM #Minería #Ingeniería #Seguridad #Peritajes #ContinuidadOperacional"},

 "PLAN-KB-IPR-008-03": {
  "hook": "🏛️ Para un mandante público, pocas cosas duelen tanto como el atraso de una obra: cada desviación golpea plazos, presupuesto y confianza.",
  "body": ("Y ese atraso muchas veces nace de una mirada fragmentada del proyecto, sin acompañamiento técnico a lo "
    "largo de todo el ciclo. 📉\n\n"
    "En #IDIEM entregamos estudios técnicos y asesorías para el sector público a lo largo del ciclo completo "
    "del proyecto, con 12 áreas especializadas: mecánica de suelos, topografía, revisión de proyectos y "
    "validación normativa en arquitectura, estructura y especialidades, además de coordinación BIM. 🧭📊\n\n"
    "Una capacidad multidisciplinaria que da respaldo técnico al mandante para decidir a tiempo y sostener el "
    "avance de la obra. 🤝"),
  "cta": "¿Tu proyecto público necesita respaldo integral? Conversemos en https://idiem.cl 👉\n\n#IDIEM #ObrasPúblicas #Ingeniería #BIM #Calidad"},

 "PLAN-KB-LMD-001-04": {
  "hook": "🧪 En faena minera, un resultado de ensayo que llega tarde ya no sirve para decidir.",
  "body": ("El control técnico solo agrega valor si la información es confiable y llega a tiempo. La falta de "
    "trazabilidad y los reportes fuera de plazo debilitan la toma de decisiones en obra. ⏱️\n\n"
    "En #IDIEM ofrecemos servicio permanente de laboratorio en obra —instalaciones, personal, equipamiento y "
    "ensayos— para proyectos mineros, energéticos, inmobiliarios e infraestructura pública y privada, con "
    "modalidades flexibles: visitas, personal permanente, o personal y equipos permanentes en obra. 👷🔬\n\n"
    "Como institución certificada ISO 17025 e ISO 9001, con estándar HSEC en seguridad y salud ocupacional, "
    "entregamos informes en plazo y seguimiento en línea de los resultados de #Ensayos. 📈✅"),
  "cta": "¿Buscas control técnico con trazabilidad en tu faena? Conversemos en https://idiem.cl 👉\n\n#IDIEM #Minería #Ensayos #Laboratorio #Calidad"},

 "PLAN-KB-IHA-001-05": {
  "hook": "Un hospital no solo cuida a las personas: también puede cuidar el entorno en el que funciona. 🌱",
  "body": ("La sostenibilidad ambiental en salud va más allá de la atención clínica: abarca cómo se gestiona el "
    "establecimiento, cómo usa sus recursos y cómo administra sus residuos. Ahí es donde un Hospital Verde "
    "marca la diferencia. ♻️\n\n"
    "En #IDIEM impulsamos la certificación GREEN HOSPITAL en Chile, que considera normativas nacionales e "
    "internacionales adecuadas a la realidad nacional, complementándose con otras certificaciones como la "
    "ISO 50001. Su evaluación abarca eficiencia energética y reducción de emisiones, gestión responsable de "
    "residuos clínicos, uso sostenible de recursos hídricos y materiales, compras responsables y promoción de "
    "la salud ambiental. 🩺\n\n"
    "Sostenibilidad que se traduce en instituciones de salud más eficientes y comprometidas con su "
    "entorno. 🤝"),
  "cta": "¿Tu institución de salud avanza hacia la sostenibilidad? Conversemos en https://idiem.cl 👉\n\n#IDIEM #GreenHospital #Sostenibilidad #Salud #InfraestructuraHospitalaria"},

 "PLAN-KB-IOM-043-06": {
  "hook": "🏗️ En infraestructura minera, las fisuras, deformaciones y la corrosión no avisan: avanzan en silencio hasta comprometer la seguridad.",
  "body": ("Planificar sin conocer el estado real de las estructuras multiplica los imprevistos y expone la "
    "operación a riesgos evitables. 🔎\n\n"
    "En #IDIEM realizamos inspecciones estructurales especializadas y peritajes, con evaluación de fisuras, "
    "deformaciones y corrosión, bajo gestión de riesgos y cumplimiento normativo. Sumamos levantamiento de "
    "información técnica en terreno mediante inspección visual, aérea y termográfica, y modelos 3D con escáner "
    "láser y dron. 🛰️📐\n\n"
    "Una línea base técnica confiable para diagnosticar la integridad estructural y priorizar "
    "intervenciones. ⚙️✅"),
  "cta": "¿Necesitas diagnosticar la integridad de tus estructuras? Conversemos en https://idiem.cl 👉\n\n#IDIEM #Minería #Ingeniería #Mantenimiento #Seguridad"},

 "PLAN-KB-IPR-021-07": {
  "hook": "🔊 El ruido generado por todo proyecto es una variable relevante: la normativa lo vigila y la comunidad lo percibe.",
  "body": ("Sin mediciones, estudio de impacto, modelación ni seguimiento, un proyecto queda expuesto a "
    "incumplimientos normativos y a conflictos con su entorno. 📉\n\n"
    "En #IDIEM entregamos servicios de ingeniería acústica: ensayos en laboratorio y terreno, líneas base e "
    "impacto acústico, desarrollo de mapas de ruido y modelos predictivos de propagación sonora, y monitoreo "
    "de cumplimiento normativo D.S. 38-11 MMA (futuro D.D. 14/24). También diseñamos soluciones de control de "
    "ruido y vibraciones, con mediciones de aislamiento acústico. 📡📊\n\n"
    "Gestión del ruido convertida en evidencia técnica para cumplir la norma y resguardar el confort. ✅"),
  "cta": "¿Necesitas gestionar la acústica de tu proyecto? Conversemos en https://idiem.cl 👉\n\n#IDIEM #Acústica #Infraestructura #Ingeniería #MedioAmbiente"},

 "PLAN-KB-LMD-010-08": {
  "hook": "🔧 En minería, una unión soldada de HDPE que falla puede detener el transporte de fluidos de toda una operación.",
  "body": ("Las uniones soldadas de tuberías HDPE para transporte de fluidos son elementos críticos: un defecto no "
    "detectado a tiempo se transforma en riesgo operacional y sobrecostos por detenciones. ⚠️\n\n"
    "En #IDIEM controlamos la calidad de estas uniones con ensayos no destructivos —para verificar "
    "especificaciones y detectar defectos— y ensayos mecánicos que evalúan las propiedades de las uniones "
    "soldadas. Sumamos asesoría experta en la documentación técnica asociada a su fabricación. 🧪📐\n\n"
    "Control técnico que respalda la confiabilidad de un componente que la operación no puede dar por "
    "supuesto. ✅"),
  "cta": "¿Necesitas asegurar la calidad de tus líneas HDPE? Conversemos en https://idiem.cl 👉\n\n#IDIEM #Minería #Ensayos #HDPE #Calidad"},

 "PLAN-KB-IHA-006-09": {
  "hook": "🏥 El término anticipado de un contrato en un proyecto de salud es uno de los escenarios más delicados de una obra.",
  "body": ("Cuando un contrato se detiene antes de tiempo, las partes necesitan claridad técnica para resolver sin "
    "improvisar. En infraestructura de salud, esa claridad es aún más crítica. ⚖️\n\n"
    "En #IDIEM, dentro de nuestra ingeniería contractual, realizamos análisis ante el término anticipado de "
    "contrato para el sector Salud, uno de los ámbitos que atendemos de forma explícita. 🤝"),
  "cta": "¿Enfrentas un conflicto contractual en salud? Conversemos en https://idiem.cl 👉\n\n#IDIEM #InfraestructuraHospitalaria #Salud #Ingeniería"},

 "PLAN-KB-IOM-056-10": {
  "hook": "📡 Una falla en un equipo rotativo crítico rara vez avisa… salvo que lo estés monitoreando.",
  "body": ("Esperar a la próxima inspección programada puede significar detectar tarde un cambio de comportamiento "
    "en un activo clave de la faena. La vigilancia continua marca la diferencia entre reaccionar y "
    "anticiparse. 🔍\n\n"
    "En #IDIEM realizamos monitoreo de salud estructural con seguimiento continuo mediante sensores e "
    "información en tiempo real, análisis de vibraciones de equipo rotativo y análisis predictivo para un "
    "mantenimiento oportuno. 📊⚙️\n\n"
    "Datos que se transforman en decisiones anticipadas para sostener la #Confiabilidad de los activos y la "
    "continuidad operacional. ✅"),
  "cta": "¿Quieres anticiparte a las fallas de tus activos críticos? Conversemos en https://idiem.cl 👉\n\n#IDIEM #Minería #Mantenimiento #Confiabilidad #Monitoreo"},

 "PLAN-KB-IPR-024-11": {
  "hook": "🏗️ En una obra pública, la calidad no se declara: se ensaya. Y un ensayo mal hecho compromete la seguridad de todo el proyecto.",
  "body": ("Sin control técnico riguroso sobre suelos, hormigones y especialidades, los problemas aparecen tarde, "
    "cuando corregirlos cuesta más. 📉\n\n"
    "En #IDIEM ejecutamos ensayos de control de obras en suelos y hormigones —densidad con densímetro nuclear "
    "o cono de arena, granulometrías, Proctor, CBR, control de hormigón fresco, extracción de testigos y "
    "madurez— además de ensayos de especialidad: corte directo, placa de carga, resistividad eléctrica, "
    "ensayos al asfalto, END a soldaduras, resistencia al fuego y peritajes en hormigones. 🧪📐\n\n"
    "Respaldados por una red de laboratorios acreditados INN y MINVU y certificación ISO 9001, con modalidad "
    "spot o permanente en terreno. ✅"),
  "cta": "¿Tu obra necesita control técnico con respaldo? Conversemos en https://idiem.cl 👉\n\n#IDIEM #ObrasPúblicas #Ensayos #Construcción #Calidad"},

 "PLAN-KB-LMD-020-12": {
  "hook": "🔩 Una soldadura defectuosa en una estructura metálica minera puede no verse… hasta que falla.",
  "body": ("Los defectos superficiales e internos en soldaduras no siempre son evidentes, pero comprometen la "
    "seguridad de estructuras y componentes mecánicos. Detectarlos a tiempo es parte del control. 🔍\n\n"
    "En #IDIEM realizamos inspección no destructiva de soldaduras metálicas en minería, maestranzas e "
    "industria: evaluamos el estado superficial e interno para detectar defectos, y brindamos asesoría en la "
    "calificación de procedimientos y de soldadores, con equipos técnicos en el norte del país. 🧪📋\n\n"
    "Evidencia técnica que respalda la confiabilidad de cada unión soldada. ✅"),
  "cta": "¿Necesitas verificar la calidad de tus soldaduras? Conversemos en https://idiem.cl 👉\n\n#IDIEM #Minería #Ensayos #END #Calidad"},
}

# ---- capa visual: titular gráfico (dentro del círculo) + bajada -------------
GRAPHIC = {
 1:  {"svc": "Ingeniería contractual",              "msg": "Respaldo técnico<br>en obras de salud.", "base": "Programación · plazos · <b>sector Salud</b>"},
 2:  {"svc": "Peritajes de fallas e incendios",     "msg": "Entender<br>qué ocurrió.",               "base": "Fallas · incendios · <b>causa raíz</b>"},
 3:  {"svc": "Asesoría a mandantes públicos",       "msg": "Respaldo técnico<br>al mandante.",        "base": "12 áreas · revisión · <b>coordinación BIM</b>"},
 4:  {"svc": "Laboratorio en obra",                 "msg": "Resultados<br>a tiempo.",                 "base": "ISO 17025 · HSEC · <b>reportes en plazo</b>"},
 5:  {"svc": "Green Hospital",                       "msg": "Hospitales que<br>cuidan su entorno.",    "base": "Energía · residuos · <b>agua y materiales</b>"},
 6:  {"svc": "Inspección y peritaje estructural",   "msg": "Diagnóstico de<br>integridad.",           "base": "Fisuras · corrosión · <b>escáner láser y dron</b>"},
 7:  {"svc": "Ingeniería acústica",                 "msg": "Gestión técnica<br>del ruido.",           "base": "Mediciones · mapas · <b>D.S. 38-11 MMA</b>"},
 8:  {"svc": "Control de calidad HDPE",             "msg": "Uniones<br>confiables.",                  "base": "Ensayos no destructivos · <b>ensayos mecánicos</b>"},
 9:  {"svc": "Ingeniería contractual",              "msg": "Claridad ante<br>el conflicto.",          "base": "Término anticipado · <b>sector Salud</b>"},
 10: {"svc": "Monitoreo de salud estructural",      "msg": "Anticiparse<br>a la falla.",              "base": "Sensores · vibraciones · <b>análisis predictivo</b>"},
 11: {"svc": "Ensayos de especialidades",           "msg": "Calidad que<br>se ensaya.",               "base": "Suelos · hormigones · <b>END a soldaduras</b>"},
 12: {"svc": "Inspección no destructiva de soldaduras", "msg": "Soldaduras<br>inspeccionadas.",       "base": "Estado superficial e interno · <b>según plan de inspección</b>"},
}

# seq -> foto real de librería incrustada (data URI)
PHOTO_FILE = {2: "p02.jpg", 3: "p03.jpg", 4: "p04.jpg", 5: "p05.jpg", 11: "p11.jpg"}

# seq -> URL Muapi generada (imagen real, se abre en el navegador/plataforma)
MUAPI_URL = {
 7:  "https://cdn.muapi.ai/outputs/generated/3df53ef3e65e44dfa908eb3c69a80b19.png",
 12: "https://cdn.muapi.ai/outputs/generated/1c61d012fe0c4b63836676ba39122c58.png",
 8:  "https://cdn.muapi.ai/outputs/generated/f8ba829f6b804553b99ce0d1a31f27dd.png",
}

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
           corner_logo: str | None = None) -> str:
    g = GRAPHIC[seq]
    if photo_uri:
        bg = (f'<div class="photo" style="background-image:url(\'{photo_uri}\')"></div>'
              '<div class="legibility"></div>')
    else:
        bg = f'<div class="solidfield"></div><div class="legibility soft"></div>'
    seal = (f'<img class="cornerlogo" src="{corner_logo}" alt="Certificación Green Hospital IDIEM">'
            if corner_logo else "")
    return f'''<div class="canvas" data-finish="{finish}">
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


def copy_panel(cid: str, seq: int) -> str:
    c = COPY[cid]
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
    {copy_panel(cid, seq)}
    <div class="trace">
      <div class="trrow"><span class="k">Post ancla</span><span class="v"><code>{esc(cid)}</code></span></div>
      <div class="trrow"><span class="k">Evidencia</span><span class="v">{ev_codes}</span></div>
      <div class="trrow">{source_row(seq, ps)}</div>
    </div>
  </div>
</article>'''


def main() -> None:
    kb = load_knowledge_base()
    review = compose_month(kb, "2026-09", target_count=12)
    for cid, c in COPY.items():
        set_post_copy(review, cid, c)

    cards = "\n".join(card(p, i) for i, p in enumerate(review.posts, 1))
    n_photo = len(PHOTO_FILE)
    n_muapi = sum(1 for p in review.posts if ((p.graphic_brief or {}).get("photo_selection") or {}).get("source") == "muapi")
    n_text = sum(1 for p in review.posts if not ((p.graphic_brief or {}).get("photo_selection") or {}))

    print(TEMPLATE.replace("__CARDS__", cards)
                  .replace("__NPHOTO__", str(n_photo))
                  .replace("__NMUAPI__", str(n_muapi))
                  .replace("__NTEXT__", str(n_text)))


TEMPLATE = r'''<title>Grilla Septiembre IDIEM</title>
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
.cornerlogo{position:absolute;z-index:3;right:5cqw;bottom:5cqw;width:21cqw;height:auto;display:block;
  border-radius:50%;filter:drop-shadow(0 2px 12px rgba(0,0,0,.45));background:rgba(255,255,255,.14)}

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
  <h1>Septiembre — <b>12 posts</b></h1>
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
    <span>Motor: <code>compose_month(2026-09)</code> · copy validado con <code>ingest_draft</code>.</span>
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
