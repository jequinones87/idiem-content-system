import sys, base64
from pathlib import Path
R=Path('/home/user/idiem-content-system'); sys.path.insert(0,str(R/'design_system')); sys.path.insert(0,str(R/'src'))
from brand_fonts import FONT_CSS
from brand_assets import RING
from gen_webinar_card import LOGO, ESLOGAN, IC_CAL, IC_CLK
S=Path('/tmp/claude-0/-home-user-idiem-content-system/697f300d-8d05-59d1-8a33-32322d6f83a1')
def u(p,m): return f"data:{m};base64,"+base64.b64encode(Path(p).read_bytes()).decode()
FOTO=u(S/'scratchpad/zip/Quebrada.png','image/png')
IC_LOC=u(R/'design_system/assets/icon_location.png','image/png')
L_MOP=u(S/'images/1.png','image/png'); L_IDIEM=u(S/'images/2.webp','image/webp')
L_AMTC=u(S/'images/4.webp','image/webp'); L_FCFM=u(S/'images/5.png','image/png')
html=f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Flyer aluviones</title><style>{FONT_CSS}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#111;font-family:Montserrat,sans-serif}}
.export{{width:1055px;height:1491px;position:relative;overflow:hidden;background:#2f3030;color:#fff}}
.photo{{position:absolute;left:0;top:0;width:1055px;height:860px;background:url({FOTO}) 55% 40%/cover}}
.grad{{position:absolute;left:0;top:0;width:1055px;height:862px;
 background:linear-gradient(180deg,rgba(20,22,23,.80) 0%,rgba(20,22,23,.22) 26%,rgba(20,22,23,.18) 50%,rgba(47,48,48,.92) 80%,#2f3030 100%),
 linear-gradient(90deg,rgba(20,22,23,.70) 0%,rgba(20,22,23,.15) 70%)}}
.ring{{position:absolute;right:-310px;top:540px;width:620px;height:620px}}
.logo{{position:absolute;top:58px;right:64px;width:170px}}
.eslogan{{position:absolute;top:70px;left:64px;width:300px}}
.copy{{position:absolute;left:64px;right:64px;top:250px}}
.kicker{{font-weight:700;font-size:25px;letter-spacing:.04em;text-transform:uppercase}}
.bar{{width:84px;height:7px;background:#e2281e;border-radius:2px;margin:20px 0 22px}}
.title{{font-weight:800;font-size:64px;line-height:1.04;letter-spacing:-.01em;text-transform:uppercase;text-shadow:0 2px 20px rgba(0,0,0,.5)}}
.sub{{margin-top:26px;font-weight:600;font-size:25px;line-height:1.3;text-transform:uppercase;max-width:700px;text-shadow:0 2px 14px rgba(0,0,0,.6)}}
.card{{position:absolute;left:64px;top:790px;width:620px;background:#e2281e;border-radius:22px;padding:28px 36px;display:flex;flex-direction:column;gap:16px;box-shadow:0 18px 40px -18px rgba(0,0,0,.7)}}
.row{{display:flex;align-items:center;gap:22px}}
.row img{{width:42px;height:42px;flex:none}} .row img.pin{{filter:brightness(0) invert(1)}}
.row b{{font-size:27px;font-weight:700}}
.row .loc b{{display:block}} .row .loc span{{display:block;font-size:19px;font-weight:500;line-height:1.35;margin-top:4px}}
.hr{{height:1px;background:rgba(255,255,255,.45)}}
.aud{{position:absolute;left:64px;right:250px;top:1112px;font-size:17.5px;line-height:1.5;font-weight:400;font-style:italic;color:rgba(255,255,255,.88)}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:226px;background:#fff;padding:24px 56px 0}}
.org{{color:#2f3030;font-weight:700;font-size:20px;letter-spacing:.14em;text-align:center}}
.orgbar{{width:56px;height:4px;background:#e2281e;margin:10px auto 0}}
.logos{{display:flex;align-items:center;justify-content:space-between;height:150px;gap:20px}}
.logos img{{display:block;object-fit:contain}}
.sep{{width:1px;height:84px;background:#c9cccd;flex:none}}
</style></head><body><div class="export">
<div class="photo"></div><div class="grad"></div>
<svg class="ring" viewBox="0 0 850 850"><path d="{RING}" fill="#e2281e"/></svg>
<img class="eslogan" src="{ESLOGAN}" alt="Elige bien. Elige idiem.">
<img class="logo" src="{LOGO}" alt="idiem">
<div class="copy">
 <div class="kicker">Jornada de presentación inicial del</div>
 <div class="bar"></div>
 <div class="title">Manual de quebradas<br>para el estudio<br>de aluviones</div>
 <div class="sub">Inicio del proceso de validación técnica<br>y actualización del manual</div>
</div>
<div class="card">
 <div class="row"><img src="{IC_CAL}" alt=""><b>30 de noviembre de 2026</b></div>
 <div class="hr"></div>
 <div class="row"><img src="{IC_CLK}" alt=""><b>09:30 a 13:00 hrs.</b></div>
 <div class="hr"></div>
 <div class="row"><svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex:none"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.6"/></svg><div class="loc"><b>Auditorio D’Etigny</b><span>FCFM – Universidad de Chile<br>Av. Beauchf 851, Santiago</span></div></div>
</div>
<div class="aud">Actividad dirigida a instituciones públicas, empresas, universidades, tomadores de decisión y profesionales vinculados a las áreas hidrología, peligros geológicos por remociones de masa, hidráulica fluvial y aluvional, el desarrollo de medidas de mitigación y la planificación territorial.</div>
<div class="foot"><div class="org">ORGANIZAN</div><div class="orgbar"></div>
 <div class="logos">
  <img src="{L_MOP}" style="height:104px" alt="MOP · Dirección de Obras Hidráulicas">
  <div class="sep"></div><img src="{L_FCFM}" style="width:236px" alt="FCFM Geología Universidad de Chile">
  <div class="sep"></div><img src="{L_AMTC}" style="width:150px" alt="AMTC">
  <div class="sep"></div><img src="{L_IDIEM}" style="width:132px" alt="idiem">
 </div></div>
</div></body></html>"""
out=S/'scratchpad/flyer/flyer.html'; out.write_text(html)
