"""Workstation del ciclo de webinar (Acero estructural) para revisar los 5 posts
con el equipo: gráficas renderizadas + copy editable + copiar + "listo para
publicar", con guardado por-navegador (localStorage), respaldo JSON y "Guardar y
compartir" (capacidad artifact) para que las ediciones lleguen a Claude.

Uso:
  python3 design_system/gen_webinar_workstation.py > /tmp/.../webinar_ws.html
Requiere los PNG renderizados en el directorio SLIDES (ver abajo).
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

SLIDES = Path("/tmp/claude-0/-home-user-idiem-content-system/"
              "1c5b178b-f8ee-5946-beb8-9cf3fffd70df/scratchpad/wslides")

FORM = ("https://docs.google.com/forms/d/e/1FAIpQLSdIHQss1ajlR2E1cQAU7EPPUZlaVJ5OGU4h8"
        "T6kh_b76fDHCQ/viewform?usp=pp_url&entry.1892003034=LinkedIn")
ZOOM = "https://us02web.zoom.us/j/84226077802?pwd=basVXzx7rE41rnjqLR0z1oGa4vCzW3.1"


def uri(name: str) -> str:
    b = (SLIDES / f"{name}.png").read_bytes()
    return "data:image/png;base64," + base64.b64encode(b).decode()


COPY = {
 "1": (
  "🏗️ El acero estructural de un proyecto minero o industrial hoy puede provenir de casi "
  "cualquier parte del mundo. Asegurar su calidad conforme a la NCh203 ya no se resuelve "
  "solo con un certificado de materiales.\n\n"
  "Cadenas de suministro globales, nuevos modelos de contratación y múltiples actores hacen "
  "que mantener la trazabilidad y verificar el cumplimiento normativo sea cada vez más "
  "desafiante. 📋\n\n"
  "En #IDIEM —laboratorio de ensayos, organismo certificador y centro de investigación "
  "aplicada— hemos participado durante años en el control y la certificación de acero "
  "estructural para proyectos mineros e industriales. Te invitamos a este webinar para "
  "compartir aprendizajes y buenas prácticas. ✅\n\n"
  "🎙️ David Silva, Jefe División Aceros Control de IDIEM\n"
  "🗓️ Miércoles 14 de octubre · 09:30 hrs (Chile) · Online\n\n"
  f"📩 Inscríbete aquí 👉 {FORM}\n\n"
  "#IDIEM #AceroEstructural #NCh203 #Minería #Industria #AseguramientoDeCalidad "
  "#Certificación #Ingeniería"),

 "2": (
  "🔎 ¿Por qué volver a mirar la NCh203? Porque el escenario del acero estructural cambió.\n\n"
  "El abastecimiento y la fabricación de estructuras hoy involucran cadenas de suministro "
  "globales y múltiples actores. Asegurar la conformidad va mucho más allá de un certificado "
  "de materiales: exige trazabilidad y evidencia técnica a lo largo de todo el proyecto. 📋\n\n"
  "Desliza para ver por qué es relevante y qué abordaremos en el webinar 👉\n\n"
  "En #IDIEM —laboratorio de ensayos, organismo certificador y centro de investigación "
  "aplicada— compartiremos los aprendizajes de años controlando y certificando acero "
  "estructural para proyectos mineros e industriales.\n\n"
  "🎙️ David Silva, Jefe División Aceros Control de IDIEM\n"
  "🗓️ Miércoles 14 de octubre · 09:30 hrs (Chile) · Online\n\n"
  f"📩 Inscríbete aquí 👉 {FORM}\n\n"
  "#IDIEM #AceroEstructural #NCh203 #Minería #Industria #AseguramientoDeCalidad"),

 "3": (
  "🧩 Un certificado de materiales no basta. La conformidad con la NCh203 se juega en la "
  "trazabilidad y en la evidencia técnica que respalda el cumplimiento a lo largo del "
  "proyecto.\n\n"
  "¿Dónde aparecen las principales brechas? En la trazabilidad entre el origen del acero, la "
  "fabricación de la estructura y la recepción en obra, con múltiples actores involucrados. 🔍\n\n"
  "En este webinar, David Silva —Jefe División Aceros Control de IDIEM— compartirá los "
  "aprendizajes de años en control y certificación de acero estructural, y buenas prácticas "
  "para cerrar esas brechas, independiente del origen del acero o del lugar de fabricación. ✅\n\n"
  "🗓️ Miércoles 14 de octubre · 09:30 hrs (Chile) · Online\n\n"
  f"📩 Inscríbete aquí 👉 {FORM}\n\n"
  "#IDIEM #AceroEstructural #NCh203 #Minería #Industria #Trazabilidad #Certificación"),

 "4": (
  "⏰ Mañana: webinar «Acero estructural en proyectos mineros e industriales».\n\n"
  "Si participas en la especificación, suministro, fabricación, inspección o recepción de "
  "estructuras de acero, esta conversación es para ti. Hablaremos de qué ha cambiado en la "
  "aplicación de la NCh203, las brechas más recurrentes en trazabilidad y el rol del "
  "laboratorio y la certificación en el aseguramiento de calidad. 🧱\n\n"
  "🎙️ David Silva, Jefe División Aceros Control de IDIEM\n"
  "🗓️ Miércoles 14 de octubre · 09:30 hrs (Chile) · Online\n\n"
  f"Aún estás a tiempo de inscribirte 📩 👉 {FORM}\n\n"
  "#IDIEM #AceroEstructural #NCh203 #Minería #Industria #AseguramientoDeCalidad"),

 "5": (
  "🔴 ¡Hoy es el día! Webinar «Acero estructural en proyectos mineros e industriales».\n\n"
  "Hoy conversamos sobre los aprendizajes y desafíos del aseguramiento de calidad del acero "
  "estructural conforme a la NCh203, junto a David Silva, Jefe División Aceros Control de "
  "IDIEM. 🧱\n\n"
  "🕘 Hoy, 09:30 hrs (Chile)\n"
  f"🎥 Ingresa por Zoom 👉 {ZOOM}\n\n"
  "¡Te esperamos! ✅\n\n"
  "#IDIEM #AceroEstructural #NCh203 #Minería #Industria #Webinar"),
}

POSTS = [
 {"id": "1", "fecha": "1 de octubre", "tipo": "Single", "obj": "Apertura de inscripciones",
  "graphics": ["inv"], "link": ("Formulario de inscripción", FORM)},
 {"id": "2", "fecha": "5 de octubre", "tipo": "Carrusel (4 láminas)", "obj": "Relevancia + temática",
  "graphics": ["car1", "car2", "car3", "car4"], "link": ("Formulario de inscripción", FORM)},
 {"id": "3", "fecha": "8 de octubre", "tipo": "Single", "obj": "Recordatorio · trazabilidad",
  "graphics": ["inv"], "link": ("Formulario de inscripción", FORM)},
 {"id": "4", "fecha": "13 de octubre", "tipo": "Single", "obj": "Víspera del evento",
  "graphics": ["inv"], "link": ("Formulario de inscripción", FORM)},
 {"id": "5", "fecha": "14 de octubre", "tipo": "Single", "obj": "Día del evento · ingreso",
  "graphics": ["live"], "link": ("Link de Zoom (solo hoy)", ZOOM)},
]

# data URIs una sola vez por gráfica usada
USED = sorted({g for p in POSTS for g in p["graphics"]})
IMG = {g: uri(g) for g in USED}

INIT_STATE = {"editor": "", "posts": {p["id"]: {"copy": COPY[p["id"]], "listo": False,
              "editedAt": "", "editedBy": ""} for p in POSTS}}


def esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def post_card(p: dict) -> str:
    imgs = "".join(
        f'<img class="slide" src="{IMG[g]}" alt="Post {p["id"]} lámina {i+1}" loading="lazy">'
        for i, g in enumerate(p["graphics"]))
    strip_cls = "gstrip carrusel" if len(p["graphics"]) > 1 else "gstrip"
    swipe = ('<span class="ghint">← desliza las 4 láminas →</span>'
             if len(p["graphics"]) > 1 else "")
    lname, lurl = p["link"]
    copy = esc(COPY[p["id"]])
    return f'''<article class="post" data-post="{p['id']}" data-listo="0">
  <div class="phead">
    <span class="pnum">{p['id']}</span>
    <div class="pmeta">
      <div class="pdate">{esc(p['fecha'])}</div>
      <div class="ptags"><span class="tag">{esc(p['tipo'])}</span><span class="tag ghost">{esc(p['obj'])}</span></div>
    </div>
    <span class="chip estado" data-role="estado">✎ pendiente</span>
  </div>
  <div class="pbody">
    <div class="gcol">
      <div class="{strip_cls}">{imgs}</div>
      {swipe}
    </div>
    <div class="ccol">
      <div class="cbar">
        <span class="lbl">Copy del post</span>
        <span class="wc" data-role="wc"></span>
        <button class="btn copybtn" data-post="{p['id']}">Copiar</button>
      </div>
      <textarea class="copy" data-post="{p['id']}" spellcheck="false">{copy}</textarea>
      <div class="crow">
        <a class="linkchip" href="{esc(lurl)}" target="_blank" rel="noopener">🔗 {esc(lname)}</a>
        <label class="listo"><input type="checkbox" class="listochk" data-post="{p['id']}"> ✅ Listo para publicar</label>
      </div>
    </div>
  </div>
</article>'''


def build() -> str:
    cards = "\n".join(post_card(p) for p in POSTS)
    state_json = json.dumps(INIT_STATE, ensure_ascii=False)
    return TEMPLATE.replace("__CARDS__", cards).replace("__STATE__", state_json)


TEMPLATE = r'''<title>Webinar Acero · Serie</title>
<meta name="description" content="Los 5 posts del ciclo del webinar de acero estructural (NCh203): gráficas, copy editable, control de listo-para-publicar y guardado compartido para revisar con el equipo.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900&display=swap">
<style>
:root{
  --red:#e1261d;--gray-blue:#666d72;--gray-dark:#2f3030;
  --ink:#22262a;--paper:#f2f2ef;--card:#ffffff;--line:rgba(47,48,48,.12);
  --muted:#6a7075;--ok:#1f9d55;--amber:#e19a1d;
  --shadow:0 20px 50px -26px rgba(47,48,48,.42);--mono:"Montserrat",system-ui,sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ink:#eef0f0;--paper:#141617;--card:#1d2021;--line:rgba(239,239,239,.13);
  --muted:#9aa1a5;--shadow:0 24px 64px -30px rgba(0,0,0,.78);
}}
:root[data-theme="dark"]{
  --ink:#eef0f0;--paper:#141617;--card:#1d2021;--line:rgba(239,239,239,.13);
  --muted:#9aa1a5;--shadow:0 24px 64px -30px rgba(0,0,0,.78);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:var(--mono);background:var(--paper);color:var(--ink);line-height:1.5;
  padding:clamp(16px,3vw,44px) clamp(14px,3vw,44px) 96px}
.wrap{max-width:1160px;margin:0 auto}
.eyebrow{display:inline-flex;align-items:center;gap:.6em;font-size:.72rem;font-weight:800;
  letter-spacing:.2em;text-transform:uppercase;color:var(--red);margin:0 0 10px}
.eyebrow .dot{width:.5em;height:.5em;border-radius:50%;background:var(--red)}
h1{font-size:clamp(1.7rem,3.6vw,2.5rem);font-weight:800;letter-spacing:-.02em;line-height:1.05;margin:0 0 .35rem;text-wrap:balance}
h1 b{color:var(--red)}
.lede{font-size:clamp(.98rem,1.5vw,1.1rem);color:var(--muted);max-width:72ch;margin:0 0 18px}
.timeline{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 18px}
.tl{display:inline-flex;align-items:center;gap:.5em;padding:6px 12px;border:1px solid var(--line);
  border-radius:100px;background:var(--card);font-size:.78rem;font-weight:600}
.tl b{color:var(--red)}
.toolbar{position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;align-items:center;gap:10px;
  background:color-mix(in srgb,var(--paper) 88%,transparent);backdrop-filter:blur(8px);
  padding:12px 0;margin:0 0 20px;border-bottom:1px solid var(--line)}
.namef{display:flex;align-items:center;gap:8px;font-size:.8rem;color:var(--muted)}
.namef input{font-family:inherit;font-size:.85rem;padding:7px 11px;border:1px solid var(--line);
  border-radius:9px;background:var(--card);color:var(--ink);min-width:150px}
.counts{font-size:.8rem;color:var(--muted);font-weight:600}
.counts b{color:var(--ink)}
.spacer{flex:1}
.btn{font-family:inherit;font-size:.8rem;font-weight:700;color:#fff;background:var(--red);border:0;
  padding:8px 15px;border-radius:100px;cursor:pointer}
.btn.ghost{background:transparent;color:var(--ink);border:1px solid var(--line)}
.btn.done{background:var(--gray-blue)}
.btn:disabled{opacity:.5;cursor:default}
.saveinfo{font-size:.74rem;color:var(--muted)}

.posts{display:flex;flex-direction:column;gap:20px}
.post{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:var(--shadow)}
.post[data-listo="1"]{border-color:color-mix(in srgb,var(--ok) 55%,var(--line))}
.phead{display:flex;align-items:center;gap:12px;padding:14px 16px;border-bottom:1px solid var(--line)}
.pnum{flex:none;width:30px;height:30px;border-radius:50%;background:var(--red);color:#fff;font-weight:800;
  display:flex;align-items:center;justify-content:center;font-size:.95rem}
.pmeta{min-width:0;flex:1}
.pdate{font-weight:800;font-size:1rem}
.ptags{display:flex;flex-wrap:wrap;gap:6px;margin-top:3px}
.tag{font-size:.66rem;font-weight:800;letter-spacing:.06em;color:#fff;background:var(--gray-dark);padding:3px 8px;border-radius:100px}
.tag.ghost{background:transparent;color:var(--muted);border:1px solid var(--line);letter-spacing:0;font-weight:600}
.chip{font-size:.72rem;font-weight:700;padding:5px 11px;border-radius:100px;white-space:nowrap}
.chip.estado{background:color-mix(in srgb,var(--amber) 18%,transparent);color:var(--amber)}
.chip.estado.ready{background:color-mix(in srgb,var(--ok) 18%,transparent);color:var(--ok)}
.pbody{display:flex;flex-direction:column;gap:16px;padding:16px}
@media(min-width:860px){.pbody{flex-direction:row;align-items:flex-start}}
.gcol{flex:none;width:100%}
@media(min-width:860px){.gcol{width:44%;max-width:420px}}
.gstrip{border-radius:10px;overflow:hidden}
.gstrip .slide{width:100%;display:block;border-radius:10px}
.gstrip.carrusel{display:flex;gap:8px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:4px}
.gstrip.carrusel .slide{flex:0 0 82%;scroll-snap-align:center}
.ghint{display:block;text-align:center;font-size:.7rem;color:var(--muted);margin-top:6px}
.ccol{flex:1;min-width:0;display:flex;flex-direction:column;gap:10px}
.cbar{display:flex;align-items:center;gap:10px}
.cbar .lbl{font-size:.66rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.cbar .wc{font-size:.72rem;color:var(--muted);margin-left:auto}
.copybtn{padding:6px 13px}
textarea.copy{font-family:inherit;width:100%;resize:vertical;border:1px solid var(--line);border-radius:10px;
  background:var(--paper);color:var(--ink);padding:12px 13px;font-size:.9rem;line-height:1.55;min-height:220px}
textarea.copy:focus{outline:2px solid var(--red);outline-offset:1px;background:var(--card)}
.crow{display:flex;flex-wrap:wrap;align-items:center;gap:12px;justify-content:space-between}
.linkchip{font-size:.78rem;font-weight:700;color:var(--red);text-decoration:none;border:1px solid color-mix(in srgb,var(--red) 40%,var(--line));
  padding:7px 12px;border-radius:100px;word-break:break-all}
.listo{display:inline-flex;align-items:center;gap:8px;font-size:.82rem;font-weight:700;cursor:pointer}
.listo input{width:17px;height:17px;accent-color:var(--ok);cursor:pointer}
.foot{margin-top:28px;padding-top:16px;border-top:1px solid var(--line);font-size:.76rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px 16px}
.foot code{font-family:inherit;font-weight:700;background:color-mix(in srgb,var(--muted) 16%,transparent);padding:1px 6px;border-radius:5px}
</style>

<script id="ws-state" type="application/json">__STATE__</script>

<div class="wrap">
  <p class="eyebrow"><span class="dot"></span>IDIEM · Webinar · Serie de campaña</p>
  <h1>Acero estructural en proyectos mineros e industriales — <b>5 posts</b></h1>
  <p class="lede">Ciclo de difusión del webinar del <strong>14 de octubre</strong> (relator David Silva). Revisa las gráficas y edita el copy de cada post. Los cambios se guardan en tu navegador; con <strong>«Guardar y compartir»</strong> quedan disponibles para el equipo y para que yo los aplique.</p>
  <div class="timeline">
    <span class="tl"><b>1</b> · 1 oct · Apertura</span>
    <span class="tl"><b>2</b> · 5 oct · Carrusel</span>
    <span class="tl"><b>3</b> · 8 oct · Recordatorio</span>
    <span class="tl"><b>4</b> · 13 oct · Víspera</span>
    <span class="tl"><b>5</b> · 14 oct · Día del evento</span>
  </div>

  <div class="toolbar">
    <label class="namef">Tu nombre <input id="editor" type="text" placeholder="p. ej. Kike" autocomplete="off"></label>
    <span class="counts" id="counts"></span>
    <span class="spacer"></span>
    <span class="saveinfo" id="saveinfo"></span>
    <button class="btn ghost" id="backup">⬇ Respaldo (JSON)</button>
    <button class="btn" id="share">💾 Guardar y compartir</button>
  </div>

  <div class="posts">
__CARDS__
  </div>

  <div class="foot">
    <span>Serie generada por IDIEM Content System · <code>gen_webinar_workstation.py</code>.</span>
    <span>Inscripción: Google Forms · Zoom solo en el post del día del evento.</span>
    <span>Reglas: 2A.2 fuente factual · logística de evento = dato libre · sin superlativos.</span>
  </div>
</div>

<script>
(function(){
  var KEY='idiem_webinar_acero_v1';
  var embed={};
  try{embed=JSON.parse(document.getElementById('ws-state').textContent)||{};}catch(e){embed={};}
  var local={};
  try{local=JSON.parse(localStorage.getItem(KEY)||'{}')||{};}catch(e){local={};}

  // merge: por post gana el editedAt más nuevo
  var store={editor: local.editor||embed.editor||'', posts:{}};
  var ids=Object.keys(embed.posts||{});
  ids.forEach(function(id){
    var e=(embed.posts||{})[id]||{}, l=(local.posts||{})[id]||{};
    var pick=( (l.editedAt||'') > (e.editedAt||'') ) ? l : e;
    // si local no tiene copy (nunca editado), usa embed
    store.posts[id]={
      copy: (pick.copy!=null?pick.copy:(e.copy||'')),
      listo: !!(pick.listo),
      editedAt: pick.editedAt||'',
      editedBy: pick.editedBy||''
    };
  });

  function save(){ try{localStorage.setItem(KEY,JSON.stringify(store));}catch(e){} }
  function now(){ var d=new Date(); function z(n){return (n<10?'0':'')+n;}
    return d.getFullYear()+'-'+z(d.getMonth()+1)+'-'+z(d.getDate())+' '+z(d.getHours())+':'+z(d.getMinutes()); }
  function autosize(t){ t.style.height='auto'; t.style.height=(t.scrollHeight+2)+'px'; }
  function wc(s){ return (s.trim().match(/\S+/g)||[]).length; }

  var editorEl=document.getElementById('editor');
  editorEl.value=store.editor;
  editorEl.addEventListener('input',function(){ store.editor=editorEl.value; save(); });

  document.querySelectorAll('.post').forEach(function(card){
    var id=card.getAttribute('data-post');
    var st=store.posts[id]||{copy:'',listo:false};
    var ta=card.querySelector('textarea.copy');
    var chk=card.querySelector('.listochk');
    var estado=card.querySelector('[data-role="estado"]');
    var wcEl=card.querySelector('[data-role="wc"]');
    ta.value=st.copy; autosize(ta);
    chk.checked=!!st.listo;
    function paint(){
      card.setAttribute('data-listo', st.listo?'1':'0');
      estado.textContent = st.listo ? '✅ listo para publicar' : (st.editedAt? ('✎ editado · '+st.editedAt):'✎ pendiente');
      estado.classList.toggle('ready', !!st.listo);
      wcEl.textContent = wc(ta.value)+' palabras';
      updateCounts();
    }
    ta.addEventListener('input',function(){
      autosize(ta); st.copy=ta.value; st.editedAt=now(); st.editedBy=store.editor||''; store.posts[id]=st; save(); paint();
    });
    chk.addEventListener('change',function(){
      st.listo=chk.checked; st.editedAt=now(); st.editedBy=store.editor||''; store.posts[id]=st; save(); paint();
    });
    card.querySelector('.copybtn').addEventListener('click',function(){
      var b=this, txt=ta.value;
      var done=function(){ var o=b.textContent; b.textContent='Copiado ✓'; b.classList.add('done');
        setTimeout(function(){ b.textContent=o; b.classList.remove('done'); },1400); };
      if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(txt).then(done,done); }
      else{ ta.select(); try{document.execCommand('copy');}catch(e){} done(); }
    });
    paint();
  });

  function updateCounts(){
    var listos=0, edit=0, tot=0;
    Object.keys(store.posts).forEach(function(id){ tot++; var p=store.posts[id];
      if(p.listo) listos++; if(p.editedAt) edit++; });
    document.getElementById('counts').innerHTML='<b>'+listos+'</b>/'+tot+' listos · '+edit+' con ediciones';
  }
  updateCounts();

  // ---- respaldo JSON ----
  document.getElementById('backup').addEventListener('click', async function(){
    var payload=JSON.stringify(store,null,2);
    var dl=null; try{ dl=await claude.use('downloads'); }catch(e){ dl=null; }
    if(dl){ try{ await dl.save({filename:'webinar_acero_copies.json', data:payload}); return; }catch(e){} }
    // fallback navegador
    var blob=new Blob([payload],{type:'application/json'});
    var a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='webinar_acero_copies.json';
    document.body.appendChild(a); a.click(); a.remove();
  });

  // ---- guardar y compartir (capacidad artifact) ----
  var shareBtn=document.getElementById('share');
  var info=document.getElementById('saveinfo');
  function buildCleanHTML(){
    var clone=document.documentElement.cloneNode(true);
    var s=clone.querySelector('#ws-state'); if(s) s.textContent=JSON.stringify(store);
    clone.querySelectorAll('textarea.copy').forEach(function(t){
      var id=t.getAttribute('data-post'); var st=(store.posts||{})[id]||{};
      t.textContent = (st.copy!=null? st.copy : t.textContent);
    });
    clone.querySelectorAll('.post').forEach(function(p){
      var id=p.getAttribute('data-post'); var st=(store.posts||{})[id]||{};
      p.setAttribute('data-listo', st.listo?'1':'0');
    });
    // limpia runtime inyectado por claude.ai
    clone.querySelectorAll('base').forEach(function(b){ if(((b.getAttribute('href')||'')).charAt(0)==='/') b.remove(); });
    clone.querySelectorAll('script').forEach(function(sc){ if((sc.textContent||'').indexOf('__FRAME_PREAMBLE')>=0) sc.remove(); });
    clone.querySelectorAll('[data-id]').forEach(function(e){ e.removeAttribute('data-id'); });
    Array.prototype.forEach.call(clone.querySelectorAll('*'), function(e){
      Array.prototype.slice.call(e.attributes||[]).forEach(function(a){
        if(a.name.indexOf('artifact-sync')===0) e.removeAttribute(a.name);
      });
    });
    return '<!doctype html>'+clone.outerHTML;
  }
  shareBtn.addEventListener('click', async function(){
    var art=null; try{ art=await claude.use('artifact'); }catch(e){ art=null; }
    if(!art){ info.textContent='No disponible aquí (ábrelo en claude.ai). Usa el respaldo JSON.'; return; }
    shareBtn.disabled=true; var o=shareBtn.textContent; shareBtn.textContent='Guardando…';
    try{
      await art.publish(buildCleanHTML());
      info.textContent='Guardado y compartido · '+now();
    }catch(e){
      info.textContent='No se pudo guardar ('+((e&&e.code)||'error')+'). Reintenta o usa el respaldo JSON.';
    }
    shareBtn.textContent=o; shareBtn.disabled=false;
  });
})();
</script>'''


if __name__ == "__main__":
    import sys
    sys.stdout.write(build())
