(function(){
  var CFG=(window.WSCFG||{});
  var KEY=CFG.key||'idiem_ws_oct2026_v7';
  var CCMAX=CFG.ccMax||900;
  function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function readJSON(s){try{return JSON.parse(s||'{}')||{};}catch(e){return {};}}
  function mergeState(base,over){var out={},k;for(k in base)out[k]=base[k];
    for(k in over){var a=out[k],b=over[k];if(!a){out[k]=b;continue;}
      var ta=a&&a.editedAt?Date.parse(a.editedAt):0,tb=b&&b.editedAt?Date.parse(b.editedAt):0;
      out[k]=(tb>=ta)?b:a;}return out;}
  // Estado COMPARTIDO embebido (viaja entre dispositivos al "Guardar y compartir")
  // fusionado con el borrador LOCAL de este navegador (gana el más reciente por post).
  var _embed=readJSON((document.getElementById('ws-state')||{}).textContent);
  var _local=readJSON(localStorage.getItem(KEY));
  var store=mergeState(_embed,_local);
  function persistLocal(){try{localStorage.setItem(KEY,JSON.stringify(store));}catch(e){}}
  // ---- estado compartido en vivo (capacidad db del artefacto) ----
  // La DB es la fuente de verdad cuando está disponible; localStorage queda como
  // caché offline. persist() guarda local y agenda un push a la DB de los docs
  // que cambiaron. Un onSnapshot repinta en vivo lo que cambie cualquier equipo.
  var db=null, dbShadow={}, pushTimer=null;
  function isPostKey(k){return k && k.charAt(0)!=='_';}
  function schedulePush(){if(!db)return;clearTimeout(pushTimer);pushTimer=setTimeout(pushNow,400);}
  function pushNow(){if(!db)return;
    Object.keys(store).forEach(function(cid){
      if(!isPostKey(cid))return;
      var body=JSON.stringify(store[cid]||{});
      if(body!==dbShadow[cid]){dbShadow[cid]=body;
        try{db.doc('posts/'+cid).set(store[cid]||{}).catch(function(){});}catch(e){}}
    });}
  function persist(){persistLocal();schedulePush();}
  function rec(cid){return (store[cid]=store[cid]||{});}
  function syncIndicator(mode){var el=document.getElementById('syncState');if(!el)return;
    el.setAttribute('data-mode',mode);
    el.textContent = mode==='sync'?'🟢 Sincronizado con el equipo'
      : mode==='local'?'🟡 Sin conexión · cambios locales' : 'Conectando…';}

  function toast(msg){var t=document.getElementById('toast');t.textContent=msg;t.classList.add('on');
    clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove('on');},1900);}
  function autosize(t){t.style.height='auto';t.style.height=(t.scrollHeight+2)+'px';}

  // ---- helpers de estado ----
  var revName=document.getElementById('revName');
  function currentUser(){return (revName&&revName.value.trim())||'';}
  function fmtWhen(iso){if(!iso)return '';var d=new Date(iso);if(isNaN(d))return '';
    var D=('0'+d.getDate()).slice(-2),M=('0'+(d.getMonth()+1)).slice(-2);
    var hh=('0'+d.getHours()).slice(-2),mm=('0'+d.getMinutes()).slice(-2);
    var today=new Date();var same=d.toDateString()===today.toDateString();
    return (same?'hoy':D+'-'+M)+' '+hh+':'+mm;}

  function computeStatus(copyEl,noteEl,r){
    var edited=(copyEl.value!==copyEl.defaultValue)||(noteEl.value.trim()!=='')||!!r.regen;
    if(!edited)return 'publicado';
    return r.ready?'listo':'pendiente';
  }

  // ---- per-post wiring ----
  document.querySelectorAll('.post').forEach(function(post){
    var cid=post.getAttribute('data-cid');
    var slides=[];
    try{slides=JSON.parse(post.querySelector('.slides-data').textContent)||[];}catch(e){}
    var r=store[cid]||{};

    var copy=post.querySelector('textarea.copy');
    var note=post.querySelector('textarea.imgnote');
    var cc=post.querySelector('[data-cc]');
    var chip=post.querySelector('.statuschip');
    var applied=chip?(chip.getAttribute('data-applied')||''):'';
    var editline=post.querySelector('.editline');
    var ready=post.querySelector('.btn.ready');
    var regen=post.querySelector('.btn.regen');
    var revs=post.querySelectorAll('.revert');

    if(typeof r.copy==='string')copy.value=r.copy;
    if(typeof r.note==='string')note.value=r.note;
    autosize(copy);autosize(note);

    function refresh(){
      // contador de caracteres (regla MKT: máx 900; .length cuenta unidades UTF-16)
      if(cc){var nch=copy.value.length;cc.textContent=nch+' / '+CCMAX;
        cc.classList.toggle('warn',nch>(CCMAX-40)&&nch<=CCMAX);cc.classList.toggle('over',nch>CCMAX);}
      var st=computeStatus(copy,note,store[cid]||{});
      post.setAttribute('data-status',st);
      post.classList.toggle('flag',st!=='publicado');
      // chip
      if(chip){chip.className='statuschip '+(st==='publicado'?'pub':st==='listo'?'ready':'pend');
        var when=fmtWhen((store[cid]||{}).editedAt);
        chip.textContent = st==='publicado' ? (applied?('publicado · '+applied):'sin cambios')
          : st==='listo' ? ('✓ listo'+(when?' · '+when:'')) : ('✎ pendiente'+(when?' · '+when:''));}
      // editline + revert
      var rr=store[cid]||{};
      var parts=[];
      if(copy.value!==copy.defaultValue)parts.push('el texto');
      if(note.value.trim()!=='')parts.push('una nota de imagen');
      if(rr.regen)parts.push('regeneración');
      if(editline){
        if(parts.length){var by=rr.editedBy?(' · por <span class="who">'+esc(rr.editedBy)+'</span>'):'';
          editline.innerHTML='Editaste '+parts.join(', ')+' · '+(fmtWhen(rr.editedAt)||'sin fecha')+by;}
        else editline.textContent='Sin cambios respecto a lo publicado.';
      }
      revs.forEach(function(b){var f=b.getAttribute('data-field');
        b.hidden = f==='copy' ? (copy.value===copy.defaultValue) : (note.value.trim()==='');});
      // ready button
      if(ready){var on=!!rr.ready && st!=='publicado';
        ready.classList.toggle('on',on);
        ready.textContent=on?'✓ Listo (quitar marca)':'✓ Marcar listo para aplicar';
        ready.disabled = (st==='publicado');}
      // el evento de Calendar incluye el copy: refrescar su enlace si cambió
      if(typeof paintCal==='function')paintCal();
    }
    function stamp(){var rc=rec(cid);rc.editedAt=new Date().toISOString();rc.editedBy=currentUser();}

    copy.addEventListener('input',function(){rec(cid).copy=copy.value;stamp();persist();autosize(copy);refresh();updateDash();});
    note.addEventListener('input',function(){rec(cid).note=note.value;stamp();persist();autosize(note);refresh();updateDash();});

    function paintRegen(){var on=!!(store[cid]&&store[cid].regen);
      regen.classList.toggle('on',on);
      regen.textContent=on?'✓ Regeneración solicitada':'🔄 Solicitar regeneración';}
    regen.addEventListener('click',function(){var cur=!!(store[cid]&&store[cid].regen);
      rec(cid).regen=!cur;stamp();persist();paintRegen();refresh();updateDash();
      toast(!cur?'Marcado para regenerar la imagen.':'Marca quitada.');});

    ready.addEventListener('click',function(){var rc=rec(cid);rc.ready=!rc.ready;persist();refresh();updateDash();
      toast(rc.ready?'Marcado como listo para aplicar.':'Marca de "listo" quitada.');});

    // ---- estado "subido a LinkedIn" (independiente del estado de contenido) ----
    var liBtn=post.querySelector('.btn.linkedin');
    var liBadge=post.querySelector('.li-badge');
    function paintLinked(){var r2=store[cid]||{};var on=!!r2.posted;
      post.classList.toggle('posted',on);
      if(liBtn){liBtn.classList.toggle('on',on);
        liBtn.textContent=on?('✓ Subido a LinkedIn'+(r2.postedAt?(' · '+fmtWhen(r2.postedAt)):'')):'🔗 Marcar subido a LinkedIn';}
      if(liBadge)liBadge.hidden=!on;}
    paintLinked();
    if(liBtn)liBtn.addEventListener('click',function(){var rc=rec(cid);rc.posted=!rc.posted;
      rc.postedAt=rc.posted?new Date().toISOString():null;persist();paintLinked();updateDash();
      toast(rc.posted?'Marcado como subido a LinkedIn.':'Marca de LinkedIn quitada.');});

    // ---- estado "aprobado para publicar" (independiente: revisado → aprobado → subido) ----
    var apBtn=post.querySelector('.btn.approve');
    var apBadge=post.querySelector('.ap-badge');
    function paintApproved(){var r2=store[cid]||{};var on=!!r2.approved;
      post.classList.toggle('approved',on);
      if(apBtn){apBtn.classList.toggle('on',on);
        apBtn.textContent=on?('✓ Aprobado'+(r2.approvedAt?(' · '+fmtWhen(r2.approvedAt)):'')):'✅ Aprobar para publicar';}
      if(apBadge)apBadge.hidden=!on;}
    paintApproved();
    if(apBtn)apBtn.addEventListener('click',function(){var rc=rec(cid);rc.approved=!rc.approved;
      rc.approvedAt=rc.approved?new Date().toISOString():null;persist();paintApproved();updateDash();
      toast(rc.approved?'Aprobado para publicar.':'Aprobación quitada.');});

    // ---- fecha de publicación + Google Calendar (independiente) ----
    // El artifact corre en un iframe sandbox y no puede llamar la API de Calendar;
    // el botón es un enlace "TEMPLATE" que abre Google Calendar con el evento pre-llenado.
    var calDate=post.querySelector('.caldate');
    var calTime=post.querySelector('.caltime');
    var calBtn=post.querySelector('.btn.cal');
    var calBadge=post.querySelector('.cal-badge');
    var calClear=post.querySelector('.calclear');
    var calTitle=post.getAttribute('data-caltitle')||('Post '+post.getAttribute('data-seq'));
    var WS_URL=CFG.wsUrl||'https://claude.ai/code/artifact/f9016145-d797-4a02-867e-1e478de62a6b';
    if(calDate&&typeof r.scheduledFor==='string')calDate.value=r.scheduledFor;
    if(calTime&&typeof r.scheduledTime==='string'&&r.scheduledTime)calTime.value=r.scheduledTime;
    function pad2(x){return ('0'+x).slice(-2);}
    function fmtDM(iso){var p=(iso||'').split('-');return p.length===3?(p[2]+'-'+p[1]):'';}
    function calURL(){
      var d=calDate?calDate.value:''; if(!d)return null;
      var t=(calTime&&calTime.value)||'09:00';
      var hh=parseInt(t.split(':')[0],10); if(isNaN(hh))hh=9;
      var mm=parseInt(t.split(':')[1],10); if(isNaN(mm))mm=0;
      var ymd=d.replace(/-/g,'');
      var start=ymd+'T'+pad2(hh)+pad2(mm)+'00';
      var em=mm+30, eh=hh; if(em>=60){em-=60; eh=(hh+1)%24;}
      var end=ymd+'T'+pad2(eh)+pad2(em)+'00';
      var title='📢 Publicar en LinkedIn — '+calTitle;
      var details=(copy.value||'')+'\n\n— Verifica la publicación y marca "subido a LinkedIn" en la workstation:\n'+WS_URL;
      return 'https://calendar.google.com/calendar/render?action=TEMPLATE'
        +'&text='+encodeURIComponent(title)
        +'&dates='+start+'/'+end
        +'&ctz=America/Santiago'
        +'&details='+encodeURIComponent(details);
    }
    function paintCal(){
      if(!calBtn)return;
      var d=calDate?calDate.value:'';
      var url=calURL();
      if(url){calBtn.setAttribute('href',url);calBtn.classList.remove('off');}
      else{calBtn.removeAttribute('href');calBtn.classList.add('off');}
      if(calBadge){if(d){calBadge.hidden=false;calBadge.textContent='📅 '+fmtDM(d);}else calBadge.hidden=true;}
      if(calClear)calClear.hidden=!d;
      post.classList.toggle('scheduled',!!d);
    }
    function saveCal(){var rc=rec(cid);var d=(calDate&&calDate.value)||'';
      if(d){rc.scheduledFor=d;rc.scheduledTime=(calTime&&calTime.value)||'09:00';}
      else{delete rc.scheduledFor;delete rc.scheduledTime;}
      persist();paintCal();updateDash();}
    if(calDate)calDate.addEventListener('change',function(){saveCal();
      toast(calDate.value?('Agendado para el '+fmtDM(calDate.value)+' · abre el botón para crear el evento'):'Fecha quitada.');});
    if(calTime)calTime.addEventListener('change',saveCal);
    if(calClear)calClear.addEventListener('click',function(){if(calDate)calDate.value='';if(calTime)calTime.value='09:00';saveCal();toast('Fecha quitada.');});

    revs.forEach(function(b){b.addEventListener('click',function(){
      var f=b.getAttribute('data-field');
      if(f==='copy'){copy.value=copy.defaultValue;rec(cid).copy=copy.defaultValue;autosize(copy);}
      else{note.value='';rec(cid).note='';autosize(note);}
      var rc=store[cid]||{};
      if(copy.value===copy.defaultValue&&note.value.trim()===''&&!rc.regen){rc.ready=false;}
      persist();refresh();updateDash();toast('Volviste a lo publicado.');});});

    // selected slide index for PNG download / main preview
    var curIdx=0;
    var main=post.querySelector('.main');
    post.querySelectorAll('.thumb').forEach(function(th){
      th.addEventListener('click',function(){
        curIdx=parseInt(th.getAttribute('data-idx'),10)||0;
        main.src=slides[curIdx];
        post.querySelectorAll('.thumb').forEach(function(x){x.classList.remove('on');});
        th.classList.add('on');
      });
    });

    post.querySelector('.gwrap').addEventListener('click',function(){openLB(slides,curIdx);});

    post.querySelector('.btn.copybtn').addEventListener('click',function(){
      var txt=copy.value;
      if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(function(){toast('Texto copiado');},function(){toast('Texto copiado');});}
      else{var ta=document.createElement('textarea');ta.value=txt;document.body.appendChild(ta);ta.select();try{document.execCommand('copy');}catch(e){}document.body.removeChild(ta);toast('Texto copiado');}
    });

    post.querySelector('.btn.png').addEventListener('click',function(){downloadPNG(post,slides,curIdx);});
    post.querySelector('.btn.pdf').addEventListener('click',function(){downloadPDF(post,slides);});

    // Reaplica el estado (store[cid]) a los controles + repinta. Lo llama el
    // onSnapshot de la DB para reflejar en vivo lo que cambie otro equipo.
    // No pisa un campo de texto que se está editando (activeElement).
    function applyState(){
      var rr=store[cid]||{};
      if(document.activeElement!==copy){
        copy.value=(typeof rr.copy==='string')?rr.copy:copy.defaultValue;autosize(copy);}
      if(document.activeElement!==note){
        note.value=(typeof rr.note==='string')?rr.note:'';autosize(note);}
      if(calDate&&document.activeElement!==calDate)calDate.value=rr.scheduledFor||'';
      if(calTime&&document.activeElement!==calTime)calTime.value=rr.scheduledTime||'09:00';
      paintRegen();paintApproved();paintLinked();paintCal();refresh();
    }
    applyState();
    post._apply=applyState;
  });

  // ---- lightbox ----
  var lb=document.getElementById('lb'),lbImg=document.getElementById('lbImg'),
      lbPrev=document.getElementById('lbPrev'),lbNext=document.getElementById('lbNext'),
      lbCount=document.getElementById('lbCount'),lbClose=document.getElementById('lbClose');
  var lbSlides=[],lbIdx=0;
  function paintLB(){lbImg.src=lbSlides[lbIdx];lbCount.textContent=(lbIdx+1)+' / '+lbSlides.length;
    lbPrev.disabled=lbIdx<=0;lbNext.disabled=lbIdx>=lbSlides.length-1;
    lbPrev.style.visibility=lbNext.style.visibility=lbSlides.length>1?'visible':'hidden';}
  function openLB(slides,idx){lbSlides=slides;lbIdx=idx||0;paintLB();lb.classList.add('on');}
  function closeLB(){lb.classList.remove('on');
    var box=document.getElementById('exportBox');
    if(box){box.remove();lbImg.style.display='';lb.querySelector('.lbbar').style.display='';}}
  lbPrev.addEventListener('click',function(){if(lbIdx>0){lbIdx--;paintLB();}});
  lbNext.addEventListener('click',function(){if(lbIdx<lbSlides.length-1){lbIdx++;paintLB();}});
  lbClose.addEventListener('click',closeLB);
  lb.addEventListener('click',function(e){if(e.target===lb)closeLB();});
  document.addEventListener('keydown',function(e){if(!lb.classList.contains('on'))return;
    if(e.key==='Escape')closeLB();if(e.key==='ArrowLeft')lbPrev.click();if(e.key==='ArrowRight')lbNext.click();});

  // ---- downloads capability ----
  var _dl=null,_dlTried=false;
  async function downloads(){if(_dlTried)return _dl;_dlTried=true;
    try{_dl=(window.claude&&claude.use)?await claude.use('downloads'):null;}catch(e){_dl=null;}return _dl;}

  function dataURItoBytes(uri){var b64=uri.split(',')[1];var bin=atob(b64);
    var n=bin.length,u=new Uint8Array(n);for(var i=0;i<n;i++)u[i]=bin.charCodeAt(i);return u;}

  async function downloadPNG(post,slides,idx){
    var dl=await downloads();
    var seq=post.getAttribute('data-seq');
    if(!dl){toast('Descarga no disponible en esta vista');return;}
    try{
      var bytes=dataURItoBytes(slides[idx]);         // JPEG bytes
      // re-encode to PNG via canvas for a true .png
      var img=new Image();img.src=slides[idx];await img.decode();
      var cv=document.createElement('canvas');cv.width=img.naturalWidth;cv.height=img.naturalHeight;
      cv.getContext('2d').drawImage(img,0,0);
      var blob=await new Promise(function(res){cv.toBlob(res,'image/png');});
      await dl.save({filename:'idiem_sep_post'+seq+(slides.length>1?('_lam'+(idx+1)):'')+'.png',data:blob});
      toast('PNG guardado');
    }catch(e){toast(errMsg(e));}
  }

  async function downloadPDF(post,slides){
    var dl=await downloads();
    var seq=post.getAttribute('data-seq');
    if(!dl){toast('Descarga no disponible en esta vista');return;}
    try{
      var pages=slides.map(function(u){return dataURItoBytes(u);});
      var pdf=buildImagePDF(pages,1080,1080);
      await dl.save({filename:'idiem_sep_post'+seq+'.pdf',data:pdf});
      toast('PDF guardado');
    }catch(e){
      if(e&&e.code==='extension_not_enabled'){toast('PDF no habilitado aquí — descarga PNG por lámina');}
      else{toast(errMsg(e));}
    }
  }

  function errMsg(e){var c=e&&e.code;
    if(c==='declined')return 'Descarga cancelada';
    if(c==='too_large')return 'Archivo muy grande';
    if(c==='rate_limited')return 'Espera un momento y reintenta';
    return 'No se pudo descargar';}

  // ---- minimal image PDF (JPEG pages, DCTDecode) ----
  function buildImagePDF(jpegs,w,h){
    var enc=new TextEncoder();
    var chunks=[],offset=0,offsets=[];
    function put(x){var b=(typeof x==='string')?enc.encode(x):x;chunks.push(b);offset+=b.length;}
    function obj(n){offsets[n]=offset;}
    put('%PDF-1.4\n%\xE2\xE3\xCF\xD3\n');
    var N=jpegs.length;
    // object numbering: 1 catalog, 2 pages, then per page: pageObj, imgObj, contentObj
    var pageIds=[],total=2+N*3;
    obj(1);put('1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n');
    var kids='';for(var i=0;i<N;i++){kids+=(3+i*3)+' 0 R ';}
    obj(2);put('2 0 obj\n<< /Type /Pages /Count '+N+' /Kids ['+kids+'] >>\nendobj\n');
    for(var p=0;p<N;p++){
      var pageId=3+p*3,imgId=pageId+1,contId=pageId+2;
      obj(pageId);
      put(pageId+' 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 '+w+' '+h+'] '+
          '/Resources << /XObject << /Im0 '+imgId+' 0 R >> >> /Contents '+contId+' 0 R >>\nendobj\n');
      obj(imgId);
      put(imgId+' 0 obj\n<< /Type /XObject /Subtype /Image /Width '+w+' /Height '+h+
          ' /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length '+jpegs[p].length+' >>\nstream\n');
      put(jpegs[p]);put('\nendstream\nendobj\n');
      var cs='q '+w+' 0 0 '+h+' 0 0 cm /Im0 Do Q\n';
      obj(contId);
      put(contId+' 0 obj\n<< /Length '+enc.encode(cs).length+' >>\nstream\n'+cs+'endstream\nendobj\n');
    }
    var xrefPos=offset;
    var count=total+1;
    put('xref\n0 '+count+'\n0000000000 65535 f \n');
    for(var k=1;k<count;k++){var o=offsets[k]||0;put(('0000000000'+o).slice(-10)+' 00000 n \n');}
    put('trailer\n<< /Size '+count+' /Root 1 0 R >>\nstartxref\n'+xrefPos+'\n%%EOF');
    return new Blob(chunks,{type:'application/pdf'});
  }

  // ---- reviewer identity ----
  var revRole=document.getElementById('revRole');
  var rv=store._reviewer||{};
  if(rv.name&&revName)revName.value=rv.name; if(rv.role&&revRole)revRole.value=rv.role;
  function saveRev(){store._reviewer={name:revName.value.trim(),role:revRole.value.trim(),editedAt:new Date().toISOString()};persist();}
  if(revName)revName.addEventListener('input',saveRev); if(revRole)revRole.addEventListener('input',saveRev);
  function slug(s){return (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'')
    .replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,40)||'revisor';}

  // ---- resumen + filtros (dashboard) ----
  function setTxt(id,v){var e=document.getElementById(id);if(e)e.textContent=v;}
  var curFilter='todos', hidePosted=false;
  function applyFilter(){document.querySelectorAll('.post').forEach(function(p){
    var st=p.getAttribute('data-status')||'publicado';
    var byStatus=curFilter==='todos'||st===curFilter;
    var byLinked=!hidePosted||!p.classList.contains('posted');
    p.classList.toggle('hide', !(byStatus&&byLinked));});}
  function updateDash(){var c={pendiente:0,listo:0,publicado:0},linked=0,approved=0,scheduled=0,total=0;
    document.querySelectorAll('.post').forEach(function(p){var s=p.getAttribute('data-status')||'publicado';
      if(c[s]==null)c[s]=0;c[s]++;total++;if(p.classList.contains('posted'))linked++;
      if(p.classList.contains('approved'))approved++;
      if(p.classList.contains('scheduled'))scheduled++;});
    setTxt('nPend',c.pendiente);setTxt('nReady',c.listo);setTxt('nPub',c.publicado);
    setTxt('nApproved',approved);setTxt('nApTotal',total);
    setTxt('nSched',scheduled);setTxt('nSchTotal',total);
    setTxt('nLinked',linked);setTxt('nTotal',total);applyFilter();}
  var liToggle=document.getElementById('liToggle');
  if(liToggle)liToggle.addEventListener('click',function(){hidePosted=!hidePosted;
    this.classList.toggle('on',hidePosted);
    this.textContent=hidePosted?'Mostrar todos':'Ocultar los ya subidos';applyFilter();});
  var filters=document.getElementById('filters');
  if(filters)filters.addEventListener('click',function(e){var b=e.target.closest('.fchip');if(!b)return;
    curFilter=b.getAttribute('data-f');
    this.querySelectorAll('.fchip').forEach(function(x){x.classList.toggle('on',x===b);});applyFilter();});
  var jn=document.getElementById('jumpNext');
  if(jn)jn.addEventListener('click',function(){
    var t=document.querySelector('.post[data-status="pendiente"]')||document.querySelector('.post[data-status="listo"]');
    if(t)t.scrollIntoView({behavior:'smooth',block:'start'});else toast('No hay posts pendientes.');});

  // "Guardar y compartir" quedó obsoleto: el estado se sincroniza en vivo por la
  // DB del artefacto (ver más abajo). Se eliminó saveCloud/buildCleanHTML/artifactCap.

  // ---- respaldo opcional: descargar JSON ----
  var expBtn=document.querySelector('.xbtn.export');
  if(expBtn)expBtn.addEventListener('click',async function(){
    var out={reviewer:{name:(revName?revName.value.trim():'')||null,role:(revRole?revRole.value.trim():'')||null},
      month:CFG.exportMonth||'2026-10',exported_at:new Date().toISOString(),posts:[]};
    document.querySelectorAll('.post').forEach(function(post){
      var stt=post.getAttribute('data-status');if(stt==='publicado')return;
      var cid=post.getAttribute('data-cid'),r=store[cid]||{},ce=post.querySelector('textarea.copy');
      out.posts.push({content_id:cid,seq:post.getAttribute('data-seq'),status:stt,
        copy:(ce&&ce.value!==ce.defaultValue)?ce.value:null,
        image_note:(r.note&&r.note.trim())?r.note:null,regenerate:!!r.regen,ready:!!r.ready,
        edited_by:r.editedBy||null,edited_at:r.editedAt||null});
    });
    if(!out.posts.length){toast('No hay cambios que respaldar todavía');return;}
    var json=JSON.stringify(out,null,2);
    var fname='idiem_cambios_'+(CFG.exportTag||'oct2026')+'__'+slug(out.reviewer.name||'revisor')+'.json';
    var dl=await downloads();
    if(dl){try{await dl.save({filename:fname,data:json});toast('Respaldo descargado');return;}
      catch(e){if(e&&e.code==='declined'){toast('Descarga cancelada');return;}}}
    try{var blob=new Blob([json],{type:'application/json'});var url=URL.createObjectURL(blob);
      var a=document.createElement('a');a.href=url;a.download=fname;document.body.appendChild(a);a.click();
      setTimeout(function(){document.body.removeChild(a);URL.revokeObjectURL(url);},1500);
      toast('Respaldo descargado');return;}catch(e){}
    var w=document.getElementById('lb');var box=document.createElement('div');
    box.id='exportBox';box.style.cssText='display:flex;flex-direction:column;gap:10px;align-items:center';
    var pre=document.createElement('textarea');pre.readOnly=true;pre.value=json;
    pre.style.cssText='width:min(90vw,720px);height:54vh;font-family:monospace;font-size:12px;padding:10px;border-radius:8px';
    var cp=document.createElement('button');cp.textContent='Copiar JSON';cp.className='xbtn';
    cp.onclick=function(){pre.select();try{document.execCommand('copy');}catch(e){}toast('JSON copiado');};
    box.appendChild(pre);box.appendChild(cp);
    lbImg.style.display='none';w.querySelector('.lbbar').style.display='none';
    w.insertBefore(box,w.querySelector('.close').nextSibling);w.classList.add('on');
  });

  updateDash();

  // ---- conexión a la DB del artefacto (estado compartido en vivo) ----
  function applyAll(){document.querySelectorAll('.post').forEach(function(p){
    if(p._apply)p._apply();});updateDash();}
  (async function(){
    try{db=(window.claude&&claude.use)?await claude.use('db'):null;}catch(e){db=null;}
    if(!db){syncIndicator('local');return;}   // sin DB: modo local (localStorage)
    syncIndicator('sync');
    try{
      db.collection('posts').onSnapshot(function(snap){
        var changed=false;
        snap.docChanges().forEach(function(ch){
          var cid=ch.doc.id;
          var body=ch.type==='removed'?'{}':JSON.stringify(ch.doc.data()||{});
          if(body===dbShadow[cid])return;              // eco de nuestra propia escritura
          dbShadow[cid]=body;
          store[cid]=ch.type==='removed'?{}:Object.assign({},ch.doc.data()||{});
          changed=true;
        });
        if(changed){persistLocal();applyAll();}
        syncIndicator('sync');
      },function(err){syncIndicator('local');});
    }catch(e){syncIndicator('local');}
  })();
})();
