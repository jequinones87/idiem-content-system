"""Consolidador de revisiones del equipo.

Toma N archivos JSON exportados por los especialistas desde la workstation
(cada uno trae `reviewer:{name,role}` + `posts:[{content_id,copy,image_note,regenerate}]`)
y produce:

  1) consolidated.json  — por post, todas las sugerencias con autor + flags.
  2) plantilla_consolidado_mes.html — artefacto visual: por post, el copy actual y
     al lado cada sugerencia por especialista, con CONFLICTOS de copy resaltados,
     un recuadro "Decisión final" por post y un botón para exportar las decisiones
     (que Claude aplica después).

Uso:
  PYTHONPATH=src python3 design_system/consolidate_reviews.py --in <dir_con_jsons> \
    [--month 2026-09] [--out design_system/plantilla_consolidado_mes.html]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import gen_month_grid as G  # noqa: E402  (COPY actual, CELL_SHORT, esc)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def load_reviews(indir: Path) -> list[dict]:
    out = []
    for p in sorted(indir.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  aviso: no pude leer {p.name}: {e}")
            continue
        rv = d.get("reviewer") or {}
        name = (rv.get("name") or p.stem).strip()
        out.append({"name": name, "role": (rv.get("role") or "").strip(),
                    "posts": d.get("posts", []), "file": p.name})
    return out


def consolidate(reviews: list[dict], month: str) -> dict:
    from idiem.loader import load_knowledge_base
    from idiem.review import compose_month
    kb = load_knowledge_base()
    review = compose_month(kb, month, target_count=12)
    meta = {}
    for i, p in enumerate(review.posts, 1):
        sub = p.subtheme if isinstance(p.subtheme, dict) else {}
        meta[p.content_id] = {
            "seq": i, "cell": p.cell,
            "cshort": G.CELL_SHORT.get(p.cell, p.cell[:3].upper()),
            "subtheme": sub.get("nombre", "") if isinstance(sub, dict) else "",
            "current_copy": _post_copy(p.content_id),
        }

    posts: dict[str, dict] = {}
    for rv in reviews:
        for pc in rv.get("posts", []):
            cid = pc.get("content_id")
            if not cid:
                continue
            e = posts.setdefault(cid, {"copy_proposals": [], "image_notes": [], "regenerate_by": []})
            if pc.get("copy"):
                e["copy_proposals"].append({"reviewer": rv["name"], "role": rv["role"], "copy": pc["copy"]})
            if pc.get("image_note"):
                e["image_notes"].append({"reviewer": rv["name"], "role": rv["role"], "note": pc["image_note"]})
            if pc.get("regenerate"):
                e["regenerate_by"].append(rv["name"])

    consolidated = []
    for cid, e in posts.items():
        m = meta.get(cid, {"seq": 999, "cell": "", "cshort": "?", "subtheme": "", "current_copy": ""})
        distinct = {_norm(x["copy"]) for x in e["copy_proposals"]}
        consolidated.append({
            "content_id": cid, **m,
            "copy_proposals": e["copy_proposals"],
            "copy_conflict": len(distinct) >= 2,
            "image_notes": e["image_notes"],
            "regenerate_by": sorted(set(e["regenerate_by"])),
        })
    consolidated.sort(key=lambda x: x["seq"])
    return {
        "month": month,
        "reviewers": [{"name": r["name"], "role": r["role"], "file": r["file"]} for r in reviews],
        "posts": consolidated,
    }


def _post_copy(cid: str) -> str:
    c = G.COPY.get(cid)
    if not c:
        return ""
    return f"{c['hook']}\n\n{c['body']}\n\n{c['cta']}"


def render_html(data: dict) -> str:
    revs = "".join(
        f'<span class="rv">{G.esc(r["name"])}'
        + (f' · <em>{G.esc(r["role"])}</em>' if r["role"] else "")
        + "</span>" for r in data["reviewers"])
    cards = "\n".join(render_card(p) for p in data["posts"]) or \
        '<p class="empty">Aún no hay cambios en los archivos cargados.</p>'
    n_conf = sum(1 for p in data["posts"] if p["copy_conflict"])
    return (TEMPLATE.replace("__REVS__", revs or "<span class='rv'>—</span>")
            .replace("__CARDS__", cards)
            .replace("__NPOSTS__", str(len(data["posts"])))
            .replace("__NREV__", str(len(data["reviewers"])))
            .replace("__NCONF__", str(n_conf)))


def render_card(p: dict) -> str:
    cid = p["content_id"]
    # propuestas de copy
    if p["copy_proposals"]:
        props = "".join(
            f'<div class="prop"><div class="who">{G.esc(x["reviewer"])}'
            + (f' · <em>{G.esc(x["role"])}</em>' if x["role"] else "")
            + f'</div><div class="ptext">{G.esc(x["copy"])}</div></div>'
            for x in p["copy_proposals"])
        conf = ('<span class="flag conf">⚠ conflicto · %d versiones</span>' % len(p["copy_proposals"])) \
            if p["copy_conflict"] else '<span class="flag ok">propuesta única</span>'
        copy_block = f'<div class="col"><div class="collab">Texto propuesto {conf}</div>{props}</div>'
    else:
        copy_block = '<div class="col"><div class="collab">Texto</div><div class="none">Sin cambios de texto.</div></div>'

    # notas de imagen
    if p["image_notes"] or p["regenerate_by"]:
        notes = "".join(
            f'<div class="prop"><div class="who">{G.esc(x["reviewer"])}'
            + (f' · <em>{G.esc(x["role"])}</em>' if x["role"] else "")
            + f'</div><div class="ptext">{G.esc(x["note"])}</div></div>'
            for x in p["image_notes"]) or '<div class="none">Sin notas de imagen.</div>'
        regen = ('<span class="flag conf">🔄 regenerar (%s)</span>' % ", ".join(G.esc(n) for n in p["regenerate_by"])) \
            if p["regenerate_by"] else ""
        img_block = f'<div class="col"><div class="collab">Imagen {regen}</div>{notes}</div>'
    else:
        img_block = '<div class="col"><div class="collab">Imagen</div><div class="none">Sin comentarios de imagen.</div></div>'

    return f'''<article class="pcard{' flag-conf' if p['copy_conflict'] else ''}" data-cid="{G.esc(cid)}" data-seq="{p['seq']}">
  <div class="phead">
    <span class="seq">{p['seq']:02d}</span><span class="badge">{p['cshort']}</span>
    <span class="sub">{G.esc(p['subtheme'])}</span><span class="cid"><code>{G.esc(cid)}</code></span>
  </div>
  <details class="cur"><summary>Copy actual</summary><div class="curtext">{G.esc(p['current_copy'])}</div></details>
  <div class="cols">{copy_block}{img_block}</div>
  <div class="decide">
    <label class="dlab">Decisión final — texto</label>
    <textarea class="final" data-cid="{G.esc(cid)}" spellcheck="false" placeholder="Escribe aquí el texto final elegido (o deja vacío si no cambia)…"></textarea>
    <label class="dlab">Decisión final — imagen</label>
    <input class="finalimg" data-cid="{G.esc(cid)}" type="text" spellcheck="false" placeholder="Ej.: usar la propuesta de X / mantener / nueva foto de …">
  </div>
</article>'''


TEMPLATE = r'''<title>Consolidado Revisión IDIEM</title>
<meta name="description" content="Consolidación de los comentarios del equipo sobre los 12 posts de septiembre: propuestas por especialista, conflictos de texto resaltados y decisión final por post.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap">
<style>
:root{--red:#e1261d;--gray-dark:#2f3030;--ink:#22262a;--paper:#f2f2ef;--card:#fff;
  --line:rgba(47,48,48,.13);--muted:#6a7075;--amber:#e19a1d;--ok:#2e7d32;--gray-light:#efefef;
  --shadow:0 18px 44px -26px rgba(47,48,48,.4);--mono:"Montserrat",system-ui,sans-serif;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ink:#eef0f0;--paper:#141617;--card:#1d2021;
  --gray-light:#282b2c;--line:rgba(239,239,239,.14);--muted:#9aa1a5;--shadow:0 22px 60px -30px rgba(0,0,0,.78);}}
:root[data-theme="dark"]{--ink:#eef0f0;--paper:#141617;--card:#1d2021;--gray-light:#282b2c;
  --line:rgba(239,239,239,.14);--muted:#9aa1a5;--shadow:0 22px 60px -30px rgba(0,0,0,.78);}
*{box-sizing:border-box}
body{margin:0;font-family:var(--mono);background:var(--paper);color:var(--ink);line-height:1.5;
  padding:clamp(18px,3.5vw,48px) clamp(14px,3.5vw,44px) 90px}
.wrap{max-width:1080px;margin:0 auto}
.eyebrow{font-size:.72rem;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--red);margin:0 0 10px}
h1{font-size:clamp(1.7rem,3.6vw,2.5rem);font-weight:800;letter-spacing:-.02em;margin:0 0 .3rem}
h1 b{color:var(--red)}
.lede{color:var(--muted);max-width:70ch;margin:0 0 14px}
.summ{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 8px;font-size:.8rem}
.pill{border:1px solid var(--line);background:var(--card);border-radius:100px;padding:6px 12px;font-weight:600}
.pill b{color:var(--red)}
.revs{font-size:.82rem;color:var(--muted);margin:0 0 20px}
.rv{display:inline-block;background:var(--gray-light);border-radius:100px;padding:3px 10px;margin:2px 4px 2px 0;color:var(--ink);font-weight:600}
.rv em{color:var(--muted);font-style:normal;font-weight:500}
.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:0 0 22px}
.xbtn{font-family:inherit;font-size:.8rem;font-weight:700;color:#fff;background:var(--red);border:0;padding:9px 18px;border-radius:100px;cursor:pointer}
.savehint{font-size:.76rem;color:var(--muted)}
.pcard{background:var(--card);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);padding:16px 18px;margin:0 0 18px}
.pcard.flag-conf{outline:2px solid var(--amber);outline-offset:-2px}
.phead{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:8px}
.seq{font-weight:800;color:var(--red);font-size:1.05rem}
.badge{font-size:.66rem;font-weight:800;letter-spacing:.1em;color:#fff;background:var(--gray-dark);padding:3px 9px;border-radius:100px}
.sub{font-size:.82rem;font-weight:600;color:var(--muted)}
.cid{margin-left:auto}
code{font-family:inherit;font-weight:700;background:var(--gray-light);padding:1px 6px;border-radius:5px;font-size:.86em}
.cur{margin:4px 0 12px}
.cur summary{cursor:pointer;font-size:.76rem;font-weight:700;color:var(--muted);letter-spacing:.04em}
.curtext{white-space:pre-wrap;font-size:.82rem;color:var(--muted);background:var(--gray-light);border-radius:8px;padding:10px 12px;margin-top:8px}
.cols{display:grid;grid-template-columns:1fr;gap:14px}
@media(min-width:760px){.cols{grid-template-columns:1fr 1fr}}
.collab{font-size:.68rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:8px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.flag{font-size:.64rem;font-weight:800;letter-spacing:.02em;padding:2px 8px;border-radius:100px;text-transform:none}
.flag.conf{background:rgba(225,154,29,.16);color:var(--amber)}
.flag.ok{background:rgba(46,125,50,.14);color:var(--ok)}
.prop{border-left:3px solid var(--line);padding:2px 0 2px 10px;margin-bottom:10px}
.pcard.flag-conf .prop{border-left-color:var(--amber)}
.who{font-size:.74rem;font-weight:700}
.who em{color:var(--muted);font-style:normal;font-weight:500}
.ptext{white-space:pre-wrap;font-size:.84rem;margin-top:3px}
.none{font-size:.82rem;color:var(--muted)}
.decide{margin-top:14px;border-top:1px solid var(--line);padding-top:12px;display:flex;flex-direction:column;gap:8px}
.dlab{font-size:.66rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--red)}
textarea.final,input.finalimg{font-family:inherit;width:100%;border:1px solid var(--line);border-radius:9px;background:var(--gray-light);color:var(--ink);padding:9px 11px;font-size:.85rem;line-height:1.5}
textarea.final{min-height:90px;resize:vertical}
textarea.final:focus,input.finalimg:focus{outline:2px solid var(--red);outline-offset:1px;background:var(--card)}
.empty{color:var(--muted)}
.foot{margin-top:26px;padding-top:16px;border-top:1px solid var(--line);font-size:.78rem;color:var(--muted)}
.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:var(--gray-dark);color:#fff;padding:10px 18px;border-radius:100px;font-size:.82rem;font-weight:600;opacity:0;transition:opacity .2s;z-index:60;pointer-events:none}
.toast.on{opacity:1}
</style>

<div class="wrap">
  <p class="eyebrow">IDIEM · Design System · Consolidado</p>
  <h1>Revisión del equipo — <b>Septiembre</b></h1>
  <p class="lede">Todos los comentarios del equipo, agrupados por post. Los <strong>conflictos de texto</strong> (dos o más versiones distintas) van resaltados. Fija la <strong>decisión final</strong> por post y expórtala para que Claude la aplique.</p>
  <div class="summ">
    <span class="pill"><b>__NPOSTS__</b> posts con comentarios</span>
    <span class="pill"><b>__NREV__</b> revisores</span>
    <span class="pill"><b>__NCONF__</b> conflictos de texto</span>
  </div>
  <p class="revs">Revisores: __REVS__</p>
  <div class="bar">
    <button class="xbtn export" type="button">⬇ Exportar decisiones (JSON)</button>
    <span class="savehint">Las decisiones se guardan en este navegador.</span>
  </div>

  __CARDS__

  <div class="foot">Consolidado generado desde los JSON de los revisores · 2A.2 = fuente de verdad · GR-04 sin superlativos.</div>
</div>
<div class="toast" id="toast"></div>

<script>
(function(){
  var KEY='idiem_consolidado_sep2026_v1';
  var store={};try{store=JSON.parse(localStorage.getItem(KEY)||'{}')||{};}catch(e){store={};}
  function persist(){try{localStorage.setItem(KEY,JSON.stringify(store));}catch(e){}}
  function rec(cid){return (store[cid]=store[cid]||{});}
  function toast(m){var t=document.getElementById('toast');t.textContent=m;t.classList.add('on');
    clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove('on');},1800);}
  function autosize(t){t.style.height='auto';t.style.height=(t.scrollHeight+2)+'px';}

  document.querySelectorAll('textarea.final').forEach(function(t){
    var cid=t.getAttribute('data-cid');if(store[cid]&&store[cid].final)t.value=store[cid].final;autosize(t);
    t.addEventListener('input',function(){rec(cid).final=t.value;persist();autosize(t);});});
  document.querySelectorAll('input.finalimg').forEach(function(t){
    var cid=t.getAttribute('data-cid');if(store[cid]&&store[cid].finalimg)t.value=store[cid].finalimg;
    t.addEventListener('input',function(){rec(cid).finalimg=t.value;persist();});});

  async function downloads(){try{return (window.claude&&claude.use)?await claude.use('downloads'):null;}catch(e){return null;}}

  document.querySelector('.xbtn.export').addEventListener('click',async function(){
    var out={month:'2026-09',decided_at:new Date().toISOString(),decisions:[]};
    document.querySelectorAll('.pcard').forEach(function(c){
      var cid=c.getAttribute('data-cid'),r=store[cid]||{};
      if((r.final&&r.final.trim())||(r.finalimg&&r.finalimg.trim())){
        out.decisions.push({content_id:cid,seq:c.getAttribute('data-seq'),
          final_copy:(r.final&&r.final.trim())?r.final:null,
          final_image:(r.finalimg&&r.finalimg.trim())?r.finalimg:null});
      }
    });
    if(!out.decisions.length){toast('No hay decisiones que exportar todavía');return;}
    var json=JSON.stringify(out,null,2),fname='idiem_decisiones_sep2026.json';
    var dl=await downloads();
    if(dl){try{await dl.save({filename:fname,data:json});toast('Decisiones exportadas');return;}
      catch(e){if(e&&e.code==='declined'){toast('Descarga cancelada');return;}}}
    try{var b=new Blob([json],{type:'application/json'}),u=URL.createObjectURL(b),a=document.createElement('a');
      a.href=u;a.download=fname;document.body.appendChild(a);a.click();
      setTimeout(function(){document.body.removeChild(a);URL.revokeObjectURL(u);},1500);toast('Decisiones exportadas');return;}catch(e){}
    var ta=document.createElement('textarea');ta.value=json;document.body.appendChild(ta);ta.select();
    try{document.execCommand('copy');}catch(e){}document.body.removeChild(ta);toast('JSON copiado al portapapeles');
  });
})();
</script>'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="indir", required=True, help="carpeta con los JSON de revisores")
    ap.add_argument("--month", default="2026-09")
    ap.add_argument("--out", default=str(ROOT / "plantilla_consolidado_mes.html"))
    ap.add_argument("--json", default=str(ROOT / "consolidated.json"))
    args = ap.parse_args()

    reviews = load_reviews(Path(args.indir))
    print(f"revisores: {len(reviews)} ({', '.join(r['name'] for r in reviews) or '—'})")
    data = consolidate(reviews, args.month)
    Path(args.json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.out).write_text(render_html(data), encoding="utf-8")
    n_conf = sum(1 for p in data["posts"] if p["copy_conflict"])
    print(f"posts con comentarios: {len(data['posts'])} · conflictos de texto: {n_conf}")
    print(f"-> {args.json}\n-> {args.out}")


if __name__ == "__main__":
    main()
