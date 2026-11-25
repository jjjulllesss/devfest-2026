#!/usr/bin/env python3
"""Génère le site HTML du guide participant (docs/guide-participant.md) dans build/.

Mise en page inspirée de la documentation Google Cloud : bandeau supérieur,
sommaire latéral, encadrés Note / Important, blocs à copier, palette Google.
Document pédagogique non officiel. Un seul fichier HTML par guide, CSS et JS
intégrés. Seule dépendance externe : les polices Roboto (repli système si
hors ligne).

Le dossier produit est publié sur GitHub Pages par .github/workflows/pages.yml :
la page d’accueil est index.html, et les fichiers que les participants doivent
télécharger (FAQ, brief Arc) sont copiés à côté, avec les mêmes chemins relatifs
que dans docs/.

Usage : python scripts/build_guides_html.py [--out build]  (nécessite le paquet « markdown »)
"""
import argparse
import html
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]

REPO_URL = "https://github.com/jjjulllesss/devfest-2026"
FEEDBACK_URL = "https://openfeedback.io/sBSRvQdfgZv87UJ1Zr8p/2026-11-27/df26-006"

# (source docs/<slug>.md, libellé, titre de la page, fichier HTML produit)
GUIDES = [
    ("guide-participant", "Guide participant", "Construire le concierge DevFest avec Arc", "index.html"),
]

# Présentation d’introduction (diaporama HTML autonome), publiée à côté du guide
PRESENTATION = "presentation/introduction.html"

# Fichiers que les participants téléchargent depuis le guide (chemins relatifs à docs/)
DOWNLOADS = ["datastore/faq-devfest-2026.txt", "brief-arc-concierge.txt"]

CSS = """
:root{
  --blue:#1a73e8;--blue-dark:#174ea6;--blue-bg:#e8f0fe;
  --red:#ea4335;--yellow:#fbbc04;--green:#34a853;--green-dark:#188038;--green-bg:#e6f4ea;
  --warn-bg:#fef7e0;--warn-border:#f9ab00;
  --text:#202124;--text2:#5f6368;--border:#dadce0;--bg2:#f8f9fa;--bg3:#f1f3f4;
  --font:"Google Sans","Google Sans Text",Roboto,"Segoe UI","Helvetica Neue",Arial,sans-serif;
  --mono:"Roboto Mono","SF Mono",Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:76px}
body{margin:0;font-family:var(--font);color:var(--text);background:#fff;line-height:1.6;font-size:16px;-webkit-font-smoothing:antialiased}
/* Bandeau */
.topbar{position:sticky;top:0;z-index:20;height:56px;display:flex;align-items:center;gap:16px;padding:0 24px;background:#fff;border-bottom:1px solid var(--border)}
.ident{display:flex;align-items:baseline;min-width:0}
.brand{display:flex;align-items:baseline;gap:12px;font-size:1.125rem;line-height:1;color:var(--text2);text-decoration:none;font-weight:500}
.dots{display:inline-flex;align-self:center;gap:3px}
.dots i{width:9px;height:9px;border-radius:50%;display:block}
.dots i:nth-child(1){background:var(--blue)}.dots i:nth-child(2){background:var(--red)}
.dots i:nth-child(3){background:var(--yellow)}.dots i:nth-child(4){background:var(--green)}
.name{display:flex;align-items:baseline;gap:12px}
.brand b{color:var(--text);font-weight:500}
.sep{align-self:center;width:1px;height:16px;flex:none;background:var(--border);margin:0 14px}
.slides{color:var(--text2);text-decoration:none;font-size:.85rem;line-height:1;font-weight:500;white-space:nowrap}
.slides:hover{color:var(--blue)}
/* Où j’en suis : position courante + barre de progression */
.where{margin-left:auto;display:flex;align-items:center;gap:14px;min-width:0}
.where .pos{display:flex;flex-direction:column;align-items:flex-end;min-width:0;line-height:1.25}
.where .pos b{font-size:.92rem;font-weight:500;color:var(--blue-dark);white-space:nowrap}
.where .pos span{font-size:.75rem;color:var(--text2);max-width:380px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.where .pct{font-size:.85rem;font-weight:500;color:var(--text2);min-width:2.9em;text-align:right;font-variant-numeric:tabular-nums}
.progress{position:absolute;left:0;right:0;bottom:-1px;height:4px;background:var(--bg3)}
.progress .bar{position:absolute;left:0;top:0;bottom:0;width:0;background:linear-gradient(90deg,var(--blue),var(--green));transition:width .12s linear}
.progress .tick{position:absolute;top:0;bottom:0;width:2px;margin-left:-1px;background:#fff}
main li.here{background:linear-gradient(90deg,var(--blue-bg),transparent 75%);border-radius:6px}
main li.here::marker{color:var(--blue);font-weight:700}
/* Mise en page */
.layout{display:flex;align-items:flex-start;padding:0 20px 0 12px}
.sidebar{position:sticky;top:60px;align-self:flex-start;width:168px;flex:none;max-height:calc(100vh - 60px);overflow:auto;padding:16px 6px 16px 0;border-right:1px solid var(--border);margin-right:20px;scrollbar-width:thin}
.sidebar h4{margin:0 0 6px 10px;font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--text2);font-weight:500}
.sidebar a{display:block;padding:4px 6px 4px 9px;margin:1px 0;border-radius:0 14px 14px 0;color:var(--text2);text-decoration:none;font-size:.8rem;line-height:1.3;border-left:3px solid transparent}
.sidebar a:hover{background:var(--bg3);color:var(--text)}
.sidebar a.active{background:var(--blue-bg);color:var(--blue-dark);border-left-color:var(--blue);font-weight:500}
.sidebar a.sub{padding-left:20px;font-size:.76rem}
.sidebar a.done{color:var(--green-dark)}
.sidebar a.done:before{content:"✓";display:inline-block;margin-right:.35em;font-weight:700}
.sidebar .grp{display:none}.sidebar .grp.open{display:block}
main{flex:1;min-width:0;max-width:860px;margin:0 auto;padding:32px 0 80px}
/* Titres */
main h1{font-size:2.25rem;line-height:1.2;font-weight:400;margin:0 0 .6em;color:var(--text);letter-spacing:-.01em}
main h2{font-size:1.625rem;line-height:1.3;font-weight:400;margin:2.4em 0 .7em;padding-top:1.1em;border-top:1px solid var(--border);display:flex;flex-wrap:wrap;align-items:center;gap:10px}
main h2:first-of-type{margin-top:1.8em}
main h3{font-size:1.2rem;font-weight:500;margin:1.9em 0 .6em}
.task{display:inline-block;background:var(--blue);color:#fff;border-radius:16px;padding:2px 14px;font-size:.85rem;font-weight:500;letter-spacing:.01em}
.chip{display:inline-flex;align-items:center;gap:5px;background:var(--bg3);color:var(--text2);border-radius:12px;padding:2px 11px;font-size:.8rem;font-weight:500}
.chip:before{content:"";width:10px;height:10px;border:2px solid var(--text2);border-radius:50%;box-sizing:border-box}
main p,main li{font-size:1rem}
main a{color:var(--blue);text-decoration:none}main a:hover{text-decoration:underline}
main ul,main ol{padding-left:1.6em}main li{margin:.3em 0}
main a[download]:before{content:"\\2B07\\FE0E";margin-right:.35em;font-size:.9em}
hr{display:none}
main img{display:block;max-width:100%;height:auto;margin:1.2em 0;border:1px solid var(--border);border-radius:8px}
/* Code */
code{font-family:var(--mono);font-size:.875em;background:var(--bg3);padding:.12em .4em;border-radius:4px;color:#3c4043}
pre{position:relative;font-family:var(--mono);background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:16px 18px;overflow-x:auto;line-height:1.5;font-size:.85rem}
pre code{background:none;padding:0;white-space:pre-wrap;word-break:break-word}
/* Tableaux */
.tablewrap{overflow-x:auto;margin:1.2em 0;border:1px solid var(--border);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th{background:var(--bg2);text-align:left;font-weight:500;color:var(--text);border-bottom:1px solid var(--border)}
th,td{padding:10px 14px;vertical-align:top}
td{border-top:1px solid var(--border)}tbody tr:first-child td{border-top:0}
tbody tr:hover td{background:#fafbfc}
/* Encadrés Note / Important */
blockquote.callout{margin:1.4em 0;padding:14px 18px 14px 52px;border-radius:8px;position:relative;border:1px solid transparent}
blockquote.callout:before{position:absolute;left:16px;top:13px;width:24px;height:24px;border-radius:50%;color:#fff;font-weight:700;font-size:.9rem;text-align:center;line-height:24px}
blockquote.callout p{margin:.5em 0}blockquote.callout p:first-child{margin-top:0}blockquote.callout p:last-child{margin-bottom:0}
blockquote.note{background:var(--blue-bg);border-color:#d2e3fc}blockquote.note:before{content:"i";background:var(--blue)}
blockquote.important{background:var(--warn-bg);border-color:#fde293}blockquote.important:before{content:"!";background:var(--warn-border)}
/* Messages à envoyer (copier) */
blockquote.prompt{margin:1.2em 0;padding:0;background:var(--bg2);border:1px solid var(--border);border-radius:8px;overflow:hidden}
blockquote.prompt:before{content:"Message à envoyer";display:block;padding:7px 16px;background:var(--bg3);color:var(--text2);font-size:.72rem;font-weight:500;letter-spacing:.06em;text-transform:uppercase;border-bottom:1px solid var(--border)}
blockquote.prompt p{position:relative;margin:0;padding:12px 64px 12px 16px;font-size:.95rem;border-top:1px solid var(--border)}
blockquote.prompt p:first-of-type{border-top:0}
/* Bouton Copier */
.copy{position:absolute;top:8px;right:8px;border:1px solid var(--border);background:#fff;color:var(--blue);font:500 .78rem var(--font);border-radius:14px;padding:3px 11px;cursor:pointer}
.copy:hover{background:var(--blue-bg)}.copy.done{background:var(--green-bg);color:var(--green-dark);border-color:#ceead6}
/* Points de contrôle (Je vérifie) */
.checkpoint{margin:1.4em 0;border:1px solid #ceead6;border-radius:8px;overflow:hidden}
.checkpoint>.cp-title{display:flex;align-items:center;gap:8px;background:var(--green-bg);color:var(--green-dark);padding:8px 16px;font-weight:500;font-size:.95rem}
.checkpoint>.cp-title:before{content:"✓";display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;background:var(--green-dark);color:#fff;font-size:.75rem}
.checkpoint .tablewrap{margin:0;border:0;border-radius:0}
.checklist li{list-style:none;margin-left:-1.2em}
/* Fin de l’atelier : pastilles du logo, puis un jet de confettis aux quatre couleurs */
h2.finale .mark{display:inline-flex;gap:4px}
h2.finale .mark i{width:9px;height:9px;border-radius:50%;display:block}
h2.finale .mark i:nth-child(1){background:var(--blue)}
h2.finale .mark i:nth-child(2){background:var(--red)}
h2.finale .mark i:nth-child(3){background:var(--yellow)}
h2.finale .mark i:nth-child(4){background:var(--green)}
.confetti{position:fixed;inset:0;pointer-events:none;z-index:30}
.confetti i{position:fixed;border-radius:50%;opacity:0;animation:burst 1.5s cubic-bezier(.15,.7,.3,1) forwards}
.confetti i.sq{border-radius:2px}
@keyframes burst{0%{opacity:1;transform:translate(0,0) scale(1)}100%{opacity:0;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(.7)}}
@media(prefers-reduced-motion:reduce){.confetti{display:none}}
/* Section Contact et feedback, en bas de page */
.contact{margin:1.2em 0 0;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.35fr);gap:16px}
.carte{display:flex;align-items:center;gap:20px;padding:22px 24px;background:var(--bg2);border:1px solid var(--border);border-radius:8px}
.carte.avis{border-left:4px solid var(--blue)}
.carte .lab{font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--text2);font-weight:500;margin-bottom:2px}
.carte .nom{font-size:1.15rem;font-weight:500;color:var(--text);line-height:1.35}
.carte .poste{font-size:.9rem;color:var(--text2);margin-top:2px}
.carte .texte{font-size:.92rem;color:var(--text2);margin:6px 0 0;line-height:1.5}
.carte .photo{width:84px;height:84px;flex:none;margin:0;border:0;border-radius:50%;object-fit:cover}
.carte .qr{flex:none;display:block}
.carte .qr img{width:150px;height:150px;margin:0;border:1px solid var(--border);border-radius:8px;background:#fff}
.carte .liens{margin-top:12px;display:flex;gap:8px;flex-wrap:wrap}
.carte .liens a{font-size:.85rem;border:1px solid var(--border);border-radius:14px;padding:3px 12px;background:#fff}
.carte .btn{display:inline-block;margin-top:12px;padding:7px 18px;border-radius:16px;background:var(--blue);color:#fff;font-size:.88rem;font-weight:500}
main .carte .btn{color:#fff}.carte .btn:hover{background:var(--blue-dark);text-decoration:none}
@media(max-width:700px){.contact{grid-template-columns:1fr}.carte.avis{flex-wrap:wrap}}
/* Responsive / impression */
@media(max-width:960px){.sidebar{display:none}.layout{padding:0 18px}main{padding-top:24px}main h1{font-size:1.8rem}.topbar{padding:0 14px}.brand span.long{display:none}}
@media(max-width:600px){.brand b{display:none}.where .pos span{max-width:42vw}.where{gap:10px}}
@media print{.topbar,.sidebar,.copy,.confetti{display:none}.layout{display:block;padding:0}main{max-width:none}main h2{break-after:avoid}.checkpoint,blockquote,pre,table{break-inside:avoid}}
"""

JS = """
(function(){
  var side=document.getElementById('toc'),sb=side.parentNode;
  var bar=document.getElementById('bar'),pct=document.getElementById('pct'),
      track=document.getElementById('progress'),
      posMain=document.getElementById('pos-main'),posSub=document.getElementById('pos-sub');
  var heads=[].slice.call(document.querySelectorAll('main h2, main h3')).filter(function(h){return h.id});
  var steps=[].slice.call(document.querySelectorAll('main ol > li'));

  // Sommaire latéral : titres h2, sous-titres h3 dépliés seulement dans la section en cours
  var items=[],grp=null;
  heads.forEach(function(h){
    var a=document.createElement('a');a.href='#'+h.id;
    a.textContent=h.getAttribute('data-toc')||h.textContent;
    if(h.tagName==='H2'){side.appendChild(a);grp=document.createElement('div');grp.className='grp';side.appendChild(grp)}
    else{a.className='sub';(grp||side).appendChild(a)}
    items.push({h:h,a:a,grp:h.tagName==='H2'?grp:null,top:0});
  });
  var stepInfo=steps.map(function(li){
    var ol=li.parentNode;
    return {li:li,n:ol.start+[].indexOf.call(ol.children,li),top:0};
  });

  // Positions mesurées une fois (puis à chaque redimensionnement ou chargement d’image)
  var maxScroll=1,ticks=[];
  function absTop(el){return el.getBoundingClientRect().top+window.scrollY}
  function measure(){
    items.forEach(function(it){it.top=absTop(it.h)});
    stepInfo.forEach(function(st){st.top=absTop(st.li)});
    maxScroll=Math.max(1,document.documentElement.scrollHeight-window.innerHeight);
    ticks.forEach(function(t){t.el.style.left=Math.max(0,Math.min(100,(t.it.top-ANCHOR)/maxScroll*100))+'%'});
    update();
  }
  var ANCHOR=120;

  // Repères des tâches sur la barre de progression
  items.forEach(function(it){
    if(it.h.tagName==='H2'&&it.h.getAttribute('data-task')){
      var t=document.createElement('i');t.className='tick';t.title=it.h.getAttribute('data-task');
      track.appendChild(t);ticks.push({el:t,it:it});
    }
  });

  var lastStep=null,lastCur=-2;
  function update(){
    var y=window.scrollY,anchor=y+ANCHOR;
    // progression de lecture
    var p=Math.max(0,Math.min(100,Math.round(y/maxScroll*100)));
    bar.style.width=p+'%';pct.textContent=p+' %';
    // section courante. Une section en fin de page, trop courte pour que son titre
    // atteigne la ligne de lecture, est tout de même marquée une fois le bas atteint.
    var ci=-1,c2=-1,limit=maxScroll+ANCHOR;
    items.forEach(function(it,k){if(Math.min(it.top,limit)<=anchor){ci=k;if(it.h.tagName==='H2')c2=k}});
    var cur=ci>=0?items[ci]:null,cur2=c2>=0?items[c2]:null;
    // étape courante : dernier pas numéroté démarré dans la section en cours
    var step=null;
    if(cur){stepInfo.forEach(function(st){if(st.top<=anchor&&st.top>=cur.top-1)step=st})}
    // texte « Où j’en suis »
    var main,sub='';
    if(!cur2){main='Introduction'}
    else{
      var task=cur2.h.getAttribute('data-task');
      main=task||cur2.a.textContent;
      if(task)sub=cur2.h.getAttribute('data-title')||'';
      if(cur&&cur.h.tagName==='H3')sub=cur.h.textContent;
    }
    if(step)main+=' · étape '+step.n;
    if(posMain.textContent!==main)posMain.textContent=main;
    if(posSub.textContent!==sub){posSub.textContent=sub;posSub.title=sub}
    // étape surlignée dans le texte
    if(lastStep!==step){
      if(lastStep)lastStep.li.classList.remove('here');
      if(step)step.li.classList.add('here');
      lastStep=step;
    }
    // sommaire : section active, sections terminées, groupe déplié
    if(lastCur!==ci){
      items.forEach(function(it,k){
        it.a.classList.toggle('active',k===ci);
        if(it.h.tagName==='H2')it.a.classList.toggle('done',k<c2);
        if(it.grp)it.grp.classList.toggle('open',k===c2);
      });
      if(ci>=0){
        var r=items[ci].a.getBoundingClientRect(),s=sb.getBoundingClientRect();
        if(r.top<s.top+8||r.bottom>s.bottom-8)sb.scrollTop+=r.top-s.top-60;
      }
      lastCur=ci;
    }
  }
  var queued=false;
  function onScroll(){if(queued)return;queued=true;requestAnimationFrame(function(){queued=false;update()})}
  window.addEventListener('scroll',onScroll,{passive:true});
  window.addEventListener('resize',measure);
  window.addEventListener('load',measure);
  [].slice.call(document.querySelectorAll('main img')).forEach(function(im){if(!im.complete)im.addEventListener('load',measure)});
  measure();

  // Boutons Copier
  function addCopy(host,getText){
    var b=document.createElement('button');b.className='copy';b.type='button';b.textContent='Copier';
    b.addEventListener('click',function(){
      var t=getText();
      (navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).catch(function(){
        var ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();
        try{document.execCommand('copy')}catch(e){}document.body.removeChild(ta);
      }).then(function(){b.textContent='Copié !';b.classList.add('done');
        setTimeout(function(){b.textContent='Copier';b.classList.remove('done')},1600)});
    });
    host.appendChild(b);
  }
  [].slice.call(document.querySelectorAll('pre')).forEach(function(p){addCopy(p,function(){return p.innerText.replace(/\\n$/,'')})});
  [].slice.call(document.querySelectorAll('blockquote.prompt > p')).forEach(function(p){
    addCopy(p,function(){var c=p.cloneNode(true);var x=c.querySelector('.copy');if(x)c.removeChild(x);return c.innerText.trim()});
  });

  // Confettis une seule fois, quand la section Félicitations entre dans l’écran
  var finale=document.querySelector('main h2.finale');
  if(finale && !window.matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window){
    var played=false;
    var io=new IntersectionObserver(function(entries){
      if(played || !entries.some(function(e){return e.isIntersecting})) return;
      played=true; io.disconnect();
      var r=finale.getBoundingClientRect();
      var layer=document.createElement('div');
      layer.className='confetti'; layer.setAttribute('aria-hidden','true');
      var colors=['#1a73e8','#ea4335','#fbbc04','#34a853'];
      for(var n=0;n<32;n++){
        var p=document.createElement('i');
        if(n%4===0) p.className='sq';
        var size=7+Math.round(Math.random()*4);
        var x=Math.round((Math.random()-0.5)*520), y=Math.round(-180+Math.random()*150);
        p.style.cssText='left:'+Math.round(r.left+20)+'px;top:'+Math.round(r.top+r.height/2)+'px;width:'+size+'px;height:'+size+'px;background:'+colors[n%4]+';--x:'+x+'px;--y:'+y+'px;--r:'+Math.round(Math.random()*240-120)+'deg;animation-delay:'+(Math.random()*0.12).toFixed(2)+'s';
        layer.appendChild(p);
      }
      document.body.appendChild(layer);
      setTimeout(function(){layer.remove()},1800);
    },{threshold:0.6});
    io.observe(finale);
  }
})();
"""


def convert(md_text: str) -> str:
    # Liens .md entre guides -> .html
    md_text = re.sub(r"\]\((guide-[a-z]+)\.md\)", r"](\1.html)", md_text)
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "toc", "sane_lists"])

    # Encadrés : blockquote dont le premier paragraphe commence par Note / Important
    def classify(match: re.Match) -> str:
        inner = match.group(1)
        first = re.search(r"<p>\s*<strong>\s*(Important|Note)", inner)
        if first:
            kind = "important" if first.group(1) == "Important" else "note"
            return f'<blockquote class="callout {kind}">{inner}</blockquote>'
        return f'<blockquote class="prompt">{inner}</blockquote>'

    body = re.sub(r"<blockquote>(.*?)</blockquote>", classify, body, flags=re.S)

    # Fichiers à télécharger : téléchargement direct au lieu d’un affichage dans le navigateur
    body = re.sub(r'<a href="([^"#?:]+\.(?:txt|yaml))">', r'<a href="\1" download>', body)

    # Tableaux dans un conteneur défilant
    body = re.sub(r"<table>(.*?)</table>", r'<div class="tablewrap"><table>\1</table></div>', body, flags=re.S)

    # Points de contrôle : « Je vérifie » suivi d’un tableau
    body = re.sub(
        r"<p><strong>Je vérifie</strong></p>\s*(<div class=\"tablewrap\">.*?</div>)",
        r'<div class="checkpoint"><div class="cp-title">Je vérifie</div>\1</div>',
        body,
        flags=re.S,
    )

    # Titres h2 : pastille « Tâche N » / « Section N » et durée en puce
    def h2(match: re.Match) -> str:
        attrs, text = match.group(1), match.group(2)
        plain = html.unescape(re.sub(r"<[^>]+>", "", text))
        dur = re.search(r"\s*\((\d+ min)\)\s*$", text)
        chip = ""
        if dur:
            chip = f'<span class="chip">{dur.group(1)}</span>'
            text = text[: dur.start()]
        plain = re.sub(r"\s*\(\d+ min\)\s*$", "", plain)
        extra = ""
        task = re.match(r"(Tâche (\d+))\.\s*(.*)", text)
        section = re.match(r"(Section (\d+))\.\s*(.*)", text) if not task else None
        step = task or section
        if step:
            toc_label = f"{step.group(2)}. {html.unescape(re.sub(r'<[^>]+>', '', step.group(3)))}"
            extra = (
                f' data-task="{step.group(1)}"'
                f' data-title="{html.escape(html.unescape(re.sub(r"<[^>]+>", "", step.group(3))), quote=True)}"'
            )
            text = f'<span class="task">{step.group(1)}</span><span>{step.group(3)}</span>'
        else:
            toc_label = plain.split(" : ")[0]
        text += chip
        if toc_label == "Félicitations":
            extra += ' class="finale"'
            text += '<span class="mark" aria-hidden="true"><i></i><i></i><i></i><i></i></span>'
        return f'<h2{attrs} data-toc="{html.escape(toc_label, quote=True)}"{extra}>{text}</h2>'

    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", h2, body, flags=re.S)
    return body


FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Ccircle cx='7' cy='16' r='4' fill='%231a73e8'/%3E%3Ccircle cx='13.5' cy='16' r='4' fill='%23ea4335'/%3E"
    "%3Ccircle cx='20' cy='16' r='4' fill='%23fbbc04'/%3E%3Ccircle cx='26.5' cy='16' r='4' fill='%2334a853'/%3E%3C/svg%3E"
)
DESCRIPTION = (
    "Atelier de 90 minutes : construire un concierge multi-agents dans Google CX Agent Studio "
    "avec Arc (DevFest Paris 2026)."
)


def page(slug: str, title: str, body: str) -> str:
    full_title = f"{title} · DevFest Paris 2026"
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(DESCRIPTION, quote=True)}">
<meta property="og:title" content="{html.escape(full_title, quote=True)}">
<meta property="og:description" content="{html.escape(DESCRIPTION, quote=True)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#1a73e8">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body>
<header class="topbar">
  <div class="ident">
    <a class="brand" href="./"><span class="dots"><i></i><i></i><i></i><i></i></span><span class="name"><b>DevFest Paris 2026</b><span class="long">Atelier CX Agent Studio</span></span></a>
    <span class="sep" aria-hidden="true"></span>
    <a class="slides" href="{PRESENTATION}">Voir la présentation</a>
  </div>
  <div class="where" aria-live="polite"><div class="pos"><b id="pos-main">Introduction</b><span id="pos-sub"></span></div><div class="pct" id="pct">0 %</div></div>
  <div class="progress" id="progress" aria-hidden="true"><i class="bar" id="bar"></i></div>
</header>
<div class="layout">
  <aside class="sidebar"><h4>Sur cette page</h4><div id="toc"></div></aside>
  <main>
{body}
    <h2 id="contact" data-toc="Contact et feedback">Contact et feedback</h2>
    <div class="contact">
      <section class="carte">
        <img class="photo" src="images/auteur.jpg" alt="Jules Mermet-Husson" width="84" height="84">
        <div>
          <div class="lab">Atelier conçu par</div>
          <div class="nom">Jules Mermet-Husson</div>
          <div class="poste">Senior Cloud &amp; AI Architect, <a href="https://www.valtech.com/">Valtech</a></div>
          <div class="liens"><a href="https://www.linkedin.com/in/jmermethusson/">LinkedIn</a><a href="https://jules.sh">jules.sh</a></div>
        </div>
      </section>
      <section class="carte avis">
        <a class="qr" href="{FEEDBACK_URL}"><img src="images/qr-feedback.png" alt="QR code : évaluer l’atelier sur OpenFeedback" width="150" height="150"></a>
        <div>
          <div class="lab">Votre avis</div>
          <div class="nom">Évaluez l’atelier</div>
          <p class="texte">Merci d’avoir suivi l’atelier. Scannez le QR code ou ouvrez le lien : votre retour m’aide à l’améliorer.</p>
          <a class="btn" href="{FEEDBACK_URL}">Donner mon avis</a>
        </div>
      </section>
    </div>
  </main>
</div>
<script>{JS}</script>
</body></html>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="build", help="dossier de sortie (défaut : build)")
    args = ap.parse_args()
    out = ROOT / args.out
    if out.exists() and out != ROOT and ROOT in out.parents:
        shutil.rmtree(out)  # pas de fichiers périmés dans le site publié
    out.mkdir(parents=True, exist_ok=True)
    # Captures et fichiers à télécharger, référencés par le guide (liens relatifs)
    docs = ROOT / "docs"
    shutil.copytree(docs / "images", out / "images", dirs_exist_ok=True, ignore=shutil.ignore_patterns(".DS_Store"))
    shutil.copytree(docs / "presentation", out / "presentation", dirs_exist_ok=True, ignore=shutil.ignore_patterns(".DS_Store"))
    for rel in DOWNLOADS:
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(docs / rel, dest)
    for slug, _label, title, filename in GUIDES:
        src = (docs / f"{slug}.md").read_text(encoding="utf-8")
        (out / filename).write_text(page(slug, title, convert(src)), encoding="utf-8")
        print("écrit", (out / filename).relative_to(ROOT))
    (out / ".nojekyll").touch()


if __name__ == "__main__":
    main()
