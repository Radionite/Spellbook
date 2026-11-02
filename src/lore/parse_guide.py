"""Split the Players' Guide HTML into lore entries for the Wereld tab.
Usage: python3 parse_guide.py <players-guide.html> <out.json>
Only the Players' Guide is used: it holds what players may know. Never feed it the DM Guide."""
import json,re,sys
from bs4 import BeautifulSoup,NavigableString
src,out=sys.argv[1],sys.argv[2]
soup=BeautifulSoup(open(src,encoding='utf-8').read(),'html.parser')
ALLOWED={'p','b','strong','i','em','ul','ol','li','table','thead','tbody','tr','th','td','h4','dl','dt','dd','div','br','span'}
def clean(node):
    for t in node.find_all(True):
        if t.name=='img': t.decompose(); continue
        if t.name not in ALLOWED: t.unwrap(); continue
        keep={}
        if t.name in('div','dl') and t.get('class'):
            c=[x for x in t['class'] if x in('box','trait','stat')]
            if c: keep['class']=' '.join(c)
        t.attrs=keep
    return node
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
entries=[]; chapter=None; cur=None; imgs=[]
def flush():
    global cur
    if cur and (cur['parts'] or cur.get('img')):
        html=''.join(cur['parts']).strip()
        if html or cur.get('img'):
            entries.append({'id':cur['id'],'ch':cur['ch'],'t':cur['t'],'h':html,**({'img':cur['img']} if cur.get('img') else {})})
    cur=None
seen=set()
def new(title,ch):
    global cur
    flush(); i=slug(title) or 'x'; base=i; n=2
    while i in seen: i=f'{base}-{n}'; n+=1
    seen.add(i); cur={'id':i,'ch':ch,'t':title,'parts':[]}
body=soup.body
for sec in body.find_all('section'):
    for el in sec.descendants:
        if isinstance(el,NavigableString) or el.name is None: continue
        if el.name=='h2':
            title=el.get_text(' ',strip=True)
            if title=='Contents': chapter=None; flush(); continue
            chapter=re.sub(r'^\d+\.\s*','',title); new(chapter,chapter); cur['intro']=True; continue
        if chapter is None or cur is None: continue
        if el.name=='h3':
            new(el.get_text(' ',strip=True),chapter); continue
        if el.name=='img':
            if not cur.get('img'): cur['img']=el.get('src')
            continue
        # take top-level content blocks only (direct children of section or .cols)
        if el.parent is not None and el.parent.name in('section',) or (el.parent is not None and el.parent.name=='div' and 'cols' in (el.parent.get('class') or [])):
            if el.name in('p','ul','ol','table','dl','div') and not (el.name=='div' and 'cols' in (el.get('class') or [])):
                if el.name=='div' and el.find('h3'): continue
                frag=BeautifulSoup(str(el),'html.parser')
                if el.get('class') and 'lede' in el.get('class'):
                    cur['parts'].append('<p class="lede">'+el.get_text(' ',strip=True)+'</p>'); continue
                clean(frag); cur['parts'].append(str(frag))
flush()
json.dump(entries,open(out,'w'),ensure_ascii=False,indent=0)
print(len(entries),'entries')
for e in entries: print(f"{e['ch'][:28]:28} | {e['t'][:40]:40} | {len(e['h'])} {e.get('img','')}")

# ---- post-processing: pictures, glossary terms, link keys ----
from bs4 import BeautifulSoup as BS
for e in entries: e.pop('img',None)
PICS={'The Lands and Who Rules Them':'guide-map.jpg','New Species: the Taivari':'art-taivari.jpg','New Species: the Fadeborn':'art-fadeborn.jpg',
 'Asper, City of Bridges':'art-asper.jpg','Linnoitus, City of the Hearthfire':'art-linnoitus.jpg','Westermark, the Great Terminus':'art-westermark.jpg',
 'Fylson, the Woven Dome':'art-fylson.jpg','Brennenberg, the Upside-Down City':'art-brennenberg.jpg','Kaigan, the Cloud Pillar':'art-kaigan.jpg'}
for e in entries:
    if e['t'] in PICS: e['img']=PICS[e['t']]
# glossary rows become their own short entries, so searching a word finds its meaning
terms=[]
for e in entries:
    if e['t']=='Words of the World':
        for tr in BS(e['h'],'html.parser').find_all('tr'):
            td=tr.find_all('td')
            if len(td)==2:
                t=td[0].get_text(' ',strip=True); terms.append({'id':'term-'+slug(t),'ch':'Words of the World','t':t,'h':'<p>'+td[1].decode_contents()+'</p>','term':True})
entries+=terms
# link keys: short names that appear in bold in other entries
def keys(e):
    t=e['t']; ks=set()
    if e.get('term'):
        for p in re.split(r'\s*[/,]\s*|\s*\(|\)',t):
            p=p.strip()
            if len(p)>2: ks.add(p)
    elif e['ch'] in('The Lands and Who Rules Them','The Six Great Cities','Orders, Guilds and Factions','Magic, Devinum and Relics','Peoples of Eidolon Vhar','Faith, Death and the Gods') and not e.get('intro'):
        parts=re.split(r',| and |:',t)
        for i,k in enumerate(parts):
            k=re.sub(r'^(the|The) ','',k.strip())
            # the bit after a comma is a nickname ("City of Bridges"), skip it
            if i>0 and ',' in t and ' and ' not in t: continue
            if len(k)>2: ks.add(k)
    for sp in('Taivari','Fadeborn'):
        if t=='New Species: the '+sp: ks.add(sp)
    return sorted(ks)
# extra names that should open a page (alias -> entry title)
ALIAS={'Sariel':'The Sacrifice of the Moon','Sariel, Angel of the Waning Moon':'The Sacrifice of the Moon','Varjohalli, the Unlit Hall':'Death and Varjohalli','Varjohalli':'Death and Varjohalli',
 'Hearthfire':'Linnoitus, City of the Hearthfire','Hearthmoot':'Linnoitus, City of the Hearthfire','Fracture of Names':'The First Age: the Descent of Form','Dissolution':'The First Age: the Descent of Form',
 'Severance Wars':'The Second Age: the Age of Iron Psalms','Silence of Heaven':'The Second Age: the Age of Iron Psalms','Vast':'Odilon, the Gentle Vast','Columns of light':'The Wounds and the light columns',
 'Nilith, the Toadstool Queen':'Nilith Territory','Lord Aurelian Vesk':'Asper and the Dusk Court','Lady Isolde Karmine':'Asper and the Dusk Court','Hrafn Ulvedal':'Asper and the Dusk Court','Old Nachtmar':'Asper and the Dusk Court','Lady Asagiri':'Asper and the Dusk Court',
 'Drowned Cathedral':'Asper, City of Bridges','Bridge of Lanterns':'Asper, City of Bridges','Rune magic':'Rune Magic','Runes':'Rune Magic'}
byt={e['t']:e for e in entries}
for al,t in ALIAS.items():
    if t in byt: byt[t].setdefault('xk',[]).append(al)
for e in entries:
    k=keys(e)+e.pop('xk',[])
    if k: e['k']=k
    e.pop('intro',None)
json.dump(entries,open(out,'w'),ensure_ascii=False,separators=(',',':'))
print('final',len(entries),'with keys',sum(1 for e in entries if 'k' in e))
