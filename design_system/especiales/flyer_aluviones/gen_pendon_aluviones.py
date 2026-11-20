import sys, base64
from pathlib import Path
R=Path('/home/user/idiem-content-system'); sys.path.insert(0,str(R/'design_system')); sys.path.insert(0,str(R/'src'))
from brand_fonts import FONT_CSS
from brand_assets import RING
from gen_webinar_card import LOGO, ESLOGAN, IC_CAL, IC_CLK
S=Path('/tmp/claude-0/-home-user-idiem-content-system/697f300d-8d05-59d1-8a33-32322d6f83a1')
def u(p,m): return f"data:{m};base64,"+base64.b64encode(Path(p).read_bytes()).decode()
FOTO=u(S/'scratchpad/flyer/quebrada_up.jpg','image/jpeg')
L_MOP=u(S/'images/1.png','image/png'); L_IDIEM=u(S/'images/2.webp','image/webp')
L_AMTC=u(S/'images/4.webp','image/webp'); L_FCFM=u(S/'images/5.png','image/png')
PIN='<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.6"/></svg>'
html=f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Pendón aluviones</title><style>{FONT_CSS}
@page{{size:800mm 2000mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#2f3030;font-family:Montserrat,sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.export{{width:800mm;height:2000mm;position:relative;overflow:hidden;background:#2f3030;color:#fff}}
.photo{{position:absolute;left:0;top:0;width:800mm;height:1180mm;background:url({FOTO}) 50% 40%/cover}}
.grad{{position:absolute;left:0;top:0;width:800mm;height:1182mm;
 background:linear-gradient(180deg,rgba(20,22,23,.80) 0%,rgba(20,22,23,.25) 22%,rgba(20,22,23,.30) 52%,rgba(47,48,48,.94) 84%,#2f3030 100%),
 linear-gradient(90deg,rgba(20,22,23,.65) 0%,rgba(20,22,23,.10) 75%)}}
.ring{{position:absolute;right:-270mm;top:760mm;width:540mm;height:540mm}}
.eslogan{{position:absolute;top:70mm;left:60mm;width:280mm}}
.logo{{position:absolute;top:56mm;right:60mm;width:170mm}}
.copy{{position:absolute;left:60mm;right:50mm;top:330mm}}
.kicker{{font-weight:700;font-size:27mm;letter-spacing:.03em;text-transform:uppercase;line-height:1.25}}
.bar{{width:80mm;height:7mm;background:#e2281e;margin:22mm 0 24mm}}
.title{{font-weight:800;font-size:69mm;line-height:1.04;letter-spacing:-.01em;text-transform:uppercase;text-shadow:0 2mm 18mm rgba(0,0,0,.5)}}
.sub{{margin-top:30mm;font-weight:600;font-size:29mm;line-height:1.3;text-transform:uppercase;text-shadow:0 1mm 12mm rgba(0,0,0,.6)}}
.card{{position:absolute;left:60mm;top:1030mm;width:600mm;background:#e2281e;border-radius:20mm;padding:30mm 34mm;display:flex;flex-direction:column;gap:18mm;box-shadow:0 14mm 34mm -14mm rgba(0,0,0,.7)}}
.row{{display:flex;align-items:center;gap:22mm}}
.row img,.row svg{{width:48mm;height:48mm;flex:none}}
.row b{{font-size:33mm;font-weight:700;line-height:1.15}}
.loc b{{display:block}} .loc span{{display:block;font-size:24mm;font-weight:500;line-height:1.35;margin-top:5mm}}
.hr{{height:.8mm;background:rgba(255,255,255,.45)}}
.aud{{position:absolute;left:60mm;right:60mm;top:1430mm;font-size:19.5mm;line-height:1.5;font-style:italic;color:rgba(255,255,255,.9)}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:345mm;background:#fff;padding:26mm 60mm 0}}
.org{{color:#2f3030;font-weight:700;font-size:19mm;letter-spacing:.14em;text-align:center}}
.orgbar{{width:56mm;height:4mm;background:#e2281e;margin:9mm auto 0}}
.grid{{display:grid;grid-template-columns:1fr 1px 1fr;grid-template-rows:115mm 100mm;align-items:center;justify-items:center;margin-top:12mm;row-gap:0}}
.grid img{{display:block;object-fit:contain}}
.vs{{width:1px;height:70mm;background:#c9cccd}}
</style></head><body><div class="export">
<div class="photo"></div><div class="grad"></div>
<svg class="ring" viewBox="0 0 850 850"><path d="{RING}" fill="#e2281e"/></svg>
<img class="eslogan" src="{ESLOGAN}" alt="Elige bien. Elige idiem.">
<img class="logo" src="{LOGO}" alt="idiem">
<div class="copy">
 <div class="kicker">Jornada de presentación<br>inicial del</div>
 <div class="bar"></div>
 <div class="title">Manual de<br>quebradas<br>para el estudio<br>de aluviones</div>
 <div class="sub">Inicio del proceso de validación técnica y actualización del manual</div>
</div>
<div class="card">
 <div class="row"><img src="{IC_CAL}" alt=""><b>30 de noviembre de 2026</b></div>
 <div class="hr"></div>
 <div class="row"><img src="{IC_CLK}" alt=""><b>09:30 a 13:00 hrs.</b></div>
 <div class="hr"></div>
 <div class="row">{PIN}<div class="loc"><b>Auditorio D’Etigny</b><span>FCFM – Universidad de Chile<br>Av. Beauchef 851, Santiago</span></div></div>
</div>
<div class="aud">Actividad dirigida a instituciones públicas, empresas, universidades, tomadores de decisión y profesionales vinculados a las áreas hidrología, peligros geológicos por remociones de masa, hidráulica fluvial y aluvional, el desarrollo de medidas de mitigación y la planificación territorial.</div>
<div class="foot"><div class="org">ORGANIZAN</div><div class="orgbar"></div>
 <div class="grid">
  <img src="{L_MOP}" style="height:100mm" alt="MOP · DOH"><div class="vs"></div><img src="{L_FCFM}" style="width:280mm" alt="FCFM">
  <img src="{L_AMTC}" style="width:190mm" alt="AMTC"><div class="vs"></div><img src="{L_IDIEM}" style="width:200mm" alt="idiem">
 </div></div>
</div></body></html>"""
(S/'scratchpad/flyer/pendon.html').write_text(html)
