import json,os,sys
from PIL import Image,ImageDraw
src=sys.argv[1]; out=sys.argv[2]
os.makedirs(out,exist_ok=True)
core=open(os.path.join(src,'core.html')).read()
data=open(os.path.join(src,'srd.json')).read().replace('</','<\\/')
core=core.replace('/*SPELLS*/[]',data)
camp=open(os.path.join(src,'campaign.json')).read().replace('</','<\\/')
core=core.replace('/*CAMPAIGN*/[]',camp.strip())
ver=sys.argv[3] if len(sys.argv)>3 else '1'
# artifact preview version: body content only
open(os.path.join(src,'artifact.html'),'w').write(core)
# icon: gold diamond on void, with a thin ring
def icon(n,pad):
  im=Image.new('RGB',(n,n),(11,10,13)); d=ImageDraw.Draw(im); c=n/2; r=n*(0.5-pad)
  d.ellipse([c-r,c-r,c+r,c+r],outline=(201,164,90),width=max(2,n//64))
  k=r*0.62; d.polygon([(c,c-k),(c+k*0.62,c),(c,c+k),(c-k*0.62,c)],fill=(201,164,90))
  d.line([(c,c-k),(c,c+k)],fill=(11,10,13),width=max(2,n//90))
  return im
icon(192,0.12).save(os.path.join(out,'icon-192.png')); icon(512,0.12).save(os.path.join(out,'icon-512.png')); icon(180,0.1).save(os.path.join(out,'apple-touch-icon.png'))
man={"name":"Eidolon Vhar Spellbook","short_name":"Spellbook","start_url":"./","scope":"./","display":"standalone","background_color":"#0b0a0d","theme_color":"#0b0a0d","orientation":"portrait",
 "icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png","purpose":"any maskable"},{"src":"icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}]}
json.dump(man,open(os.path.join(out,'manifest.webmanifest'),'w'),indent=1)
head='''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:0}[hidden]{display:none!important}img{max-width:100%}</style>
'''
sw_reg='''<script>if('serviceWorker' in navigator){addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));}</script>
'''
html=head+core.replace('<header class="top">','</head><body>\n<header class="top">',1)+sw_reg+'</body></html>\n'
open(os.path.join(out,'index.html'),'w').write(html)
sw='''// Offline cache for the Eidolon Vhar Spellbook. Bump VERSION after changing the app.
const VERSION='ev-spellbook-'''+ver+''''';
const CORE=['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png','apple-touch-icon.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(VERSION).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==VERSION).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  const u=new URL(e.request.url);
  if(u.origin===location.origin){
    // app files: network first so updates arrive, cache when offline
    e.respondWith(fetch(e.request).then(r=>{const cp=r.clone();caches.open(VERSION).then(c=>c.put(e.request,cp));return r;}).catch(()=>caches.match(e.request).then(r=>r||caches.match('index.html'))));
  } else if(/fonts\\.(googleapis|gstatic)\\.com$/.test(u.hostname)){
    // fonts: cache first
    e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(res=>{const cp=res.clone();caches.open(VERSION).then(c=>c.put(e.request,cp));return res;})));
  }
});
'''
open(os.path.join(out,'sw.js'),'w').write(sw)
print('ok',os.path.getsize(os.path.join(out,'index.html')))
