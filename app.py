import os,re,uuid
from datetime import datetime,timezone
from fastapi import FastAPI,HTTPException
from fastapi.responses import HTMLResponse,Response
from pydantic import BaseModel,Field
import httpx

VERSION='3.0.0'
CHARIOW_BASE=os.getenv('CHARIOW_BASE_URL','https://api.chariow.com/v1').rstrip('/')
CHARIOW_KEY=os.getenv('CHARIOW_API_KEY','')
AI_BASE=os.getenv('AI_BASE_URL','https://api.openai.com/v1').rstrip('/')
AI_KEY=os.getenv('AI_API_KEY','')
AI_MODEL=os.getenv('AI_MODEL','')
app=FastAPI(title='Chariow AI Product Bot',version=VERSION)

class Generate(BaseModel):
    niche:str=Field(min_length=2,max_length=120); audience:str=Field(min_length=2,max_length=160)
    problem:str=''; product_type:str='downloadable'; currency:str='XAF'; language:str='fr'
class Price(BaseModel):
    currency:str='XAF'; perceived_value:int=Field(7,ge=1,le=10); differentiation:int=Field(6,ge=1,le=10)
    complexity:int=Field(5,ge=1,le=10); delivery_cost:float=Field(0,ge=0); target_price:float=Field(0,ge=0)

def slug(s): return re.sub(r'[-\s]+','-',re.sub(r'[^a-zA-Z0-9\s-]','',s.lower())).strip('-')[:70]
def price_engine(r):
    base={'XAF':2500,'USD':7,'EUR':6}.get(r.currency.upper(),2500)
    score=(r.perceived_value*.45+r.differentiation*.35+r.complexity*.20)/10
    p=r.target_price or base*(.65+score*1.15)
    if r.delivery_cost:p=max(p,r.delivery_cost*2.5)
    p=max(1000,round(p/500)*500) if r.currency.upper()=='XAF' else round(p,2)
    return {'recommended_price':p,'currency':r.currency.upper(),'confidence':round(min(95,max(35,45+score*50))), 'note':'Estimation stratégique, jamais une garantie de ventes.'}

def draft(r):
    title=f'{r.niche.strip()} : guide pratique pour {r.audience.strip()}'
    problem=r.problem.strip() or f'obtenir un résultat concret dans {r.niche.strip()}'
    p=price_engine(Price(currency=r.currency))['recommended_price']
    text=f'''# {title}\n\n## Promesse\nUne méthode simple et immédiatement applicable pour {r.audience} afin de {problem}.\n\n## Contenu\n1. Comprendre le problème\n2. Préparer les outils\n3. Méthode étape par étape\n4. Exemple concret\n5. Checklist\n6. Plan d’action sur 7 jours\n7. Erreurs à éviter\n\n## Offre\nPrix indicatif : {p} {r.currency.upper()}\n\n## CTA\nCommence aujourd’hui avec une méthode claire et directement applicable.\n'''
    return {'id':'draft_'+uuid.uuid4().hex[:10],'title':title,'slug':slug(title),'type':r.product_type,'niche':r.niche,'audience':r.audience,'problem':problem,'price':p,'currency':r.currency.upper(),'content_markdown':text,'marketing':{'headline':f'Une méthode simple pour {r.audience} qui veut progresser en {r.niche}.','benefits':['Gain de temps','Étapes concrètes','Modèles prêts à adapter','Résultat mesurable'],'cta':'Découvrir le produit'},'created_at':datetime.now(timezone.utc).isoformat()}

async def chariow(path,params=None):
    if not CHARIOW_KEY: raise HTTPException(400,'CHARIOW_API_KEY non configurée dans Render.')
    async with httpx.AsyncClient(timeout=20) as c:
        r=await c.get(CHARIOW_BASE+path,headers={'Authorization':f'Bearer {CHARIOW_KEY}','Accept':'application/json'},params=params)
    if r.status_code==401: raise HTTPException(401,'Clé Chariow invalide ou révoquée.')
    if r.status_code>=400: raise HTTPException(r.status_code,r.text[:500])
    return r.json()

@app.get('/health')
def health(): return {'status':'ok','version':VERSION,'chariow_configured':bool(CHARIOW_KEY),'ai_configured':bool(AI_KEY and AI_MODEL)}
@app.get('/api/config')
def config(): return {'version':VERSION,'chariow_configured':bool(CHARIOW_KEY),'ai_configured':bool(AI_KEY and AI_MODEL)}
@app.post('/api/generate')
def generate(r:Generate): return draft(r)
@app.post('/api/price')
def price(r:Price): return price_engine(r)
@app.get('/api/chariow/store')
async def store(): return await chariow('/store')
@app.get('/api/chariow/products')
async def products(search:str='',category:str='',type:str='',per_page:int=20):
    q={'per_page':min(max(per_page,1),100)}
    if search:q['search']=search
    if category:q['category']=category
    if type:q['type']=type
    return await chariow('/products',q)
@app.get('/api/chariow/sales')
async def sales(per_page:int=20): return await chariow('/sales',{'per_page':min(max(per_page,1),100)})
@app.post('/api/export')
def export(p:dict):
    if not p.get('title'): raise HTTPException(400,'Produit invalide')
    return Response(p.get('content_markdown',''),media_type='text/markdown',headers={'Content-Disposition':f'attachment; filename="{slug(p["title"]) or "produit"}.md"'})

HTML='''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Chariow AI Product Bot V3</title><style>:root{--bg:#0b0d12;--card:#121620;--text:#f5f7fa;--muted:#9aa4b2;--line:#293345;--a:#8b5cf6}*{box-sizing:border-box}body{margin:0;background:linear-gradient(180deg,#0b0d12,#101522);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}main{max-width:1050px;margin:auto;padding:20px}.top{display:flex;justify-content:space-between;gap:12px;align-items:center}.tag{border:1px solid #4c3a73;border-radius:99px;padding:6px 10px;color:#c4b5fd;font-size:12px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.card{background:#121620;border:1px solid var(--line);border-radius:18px;padding:18px;margin:16px 0}h1{font-size:25px}h2{font-size:18px}label{display:block;color:#cbd5e1;font-size:13px;margin:12px 0 6px}input,select,textarea{width:100%;padding:12px;background:#0d1119;color:#fff;border:1px solid #303a4d;border-radius:10px;font-size:15px}textarea{min-height:90px}button{border:0;border-radius:10px;padding:12px 15px;background:var(--a);color:#fff;font-weight:700;margin-top:12px}.secondary{background:#222a39}.muted{color:var(--muted);font-size:13px}pre{white-space:pre-wrap;background:#0a0d13;border:1px solid var(--line);padding:14px;border-radius:12px;max-height:500px;overflow:auto}.metric{font-size:28px;font-weight:800}.ok{color:#86efac}.warn{color:#fbbf24}.row{display:flex;gap:8px;flex-wrap:wrap}@media(max-width:760px){.grid{grid-template-columns:1fr}main{padding:14px}.top{align-items:flex-start;flex-direction:column}}</style></head><body><main><div class="top"><div><h1>🤖 Chariow AI Product Bot</h1><div class="muted">V3 — création, prix, marketing et pilotage</div></div><span class="tag">iPhone friendly</span></div><div class="card"><b>État du système</b><div id="status" class="muted">Vérification…</div></div><div class="grid"><section class="card"><h2>1. Créer un produit</h2><label>Niche</label><input id="niche" placeholder="ex. Excel, CV, marketing"><label>Public cible</label><input id="audience" placeholder="ex. étudiants camerounais"><label>Problème à résoudre</label><textarea id="problem"></textarea><label>Type</label><select id="ptype"><option value="downloadable">Téléchargeable</option><option value="course">Formation</option><option value="bundle">Bundle</option><option value="service">Service</option><option value="coaching">Coaching</option></select><label>Devise</label><select id="currency"><option>XAF</option><option>USD</option><option>EUR</option></select><button onclick="generate()">Créer le brouillon</button></section><section class="card"><h2>2. Prix</h2><label>Valeur perçue (1–10)</label><input id="value" type="number" min="1" max="10" value="7"><label>Différenciation (1–10)</label><input id="diff" type="number" min="1" max="10" value="6"><label>Profondeur (1–10)</label><input id="complex" type="number" min="1" max="10" value="5"><label>Coût de livraison</label><input id="cost" type="number" min="0" value="0"><button class="secondary" onclick="price()">Suggérer le prix</button><div id="priceOut"></div></section></div><section class="card"><h2>3. Produit généré</h2><div id="productOut" class="muted">Aucun produit.</div><button id="download" class="secondary" style="display:none" onclick="downloadProduct()">Télécharger le brouillon</button></section><div class="grid"><section class="card"><h2>4. Chariow</h2><div class="muted">La clé reste sur Render. Fonctions API publiques documentées : boutique, produits publiés, ventes.</div><div class="row"><button class="secondary" onclick="call('/api/chariow/store')">Tester boutique</button><button class="secondary" onclick="call('/api/chariow/products')">Mes produits</button><button class="secondary" onclick="call('/api/chariow/sales')">Mes ventes</button></div><pre id="out">Pas encore testé.</pre></section><section class="card"><h2>5. Rentabilité</h2><div class="muted">Score stratégique indicatif, jamais une garantie.</div><pre id="plan">Après création : valider le problème, tester le prix, publier, mesurer les ventes et améliorer.</pre></section></div></main><script>let current=null;async function api(u,o={}){let r=await fetch(u,{headers:{'Content-Type':'application/json'},...o}),t=await r.text(),d;try{d=JSON.parse(t)}catch{d={detail:t}}if(!r.ok)throw Error(d.detail||'Erreur');return d}async function init(){try{let c=await api('/api/config');status.innerHTML=`Version ${c.version} — Chariow: <span class="${c.chariow_configured?'ok':'warn'}">${c.chariow_configured?'connecté':'clé absente'}</span> — IA: <span class="${c.ai_configured?'ok':'warn'}">${c.ai_configured?'connectée':'mode local'}</span>`}catch(e){status.textContent=e.message}}async function generate(){try{current=await api('/api/generate',{method:'POST',body:JSON.stringify({niche:niche.value,audience:audience.value,problem:problem.value,product_type:ptype.value,currency:currency.value,language:'fr'})});productOut.innerHTML=`<h3>${current.title}</h3><p>${current.marketing.headline}</p><p><b>${current.price} ${current.currency}</b></p><pre>${current.content_markdown}</pre>`;download.style.display='inline-block';plan.textContent='1. Vérifier que le problème est réel.\n2. Tester l’offre auprès de prospects.\n3. Tester le prix proposé.\n4. Publier sur Chariow.\n5. Suivre ventes et retours.\n6. Améliorer le produit.\n\nAucune rentabilité n’est garantie.'}catch(e){alert(e.message)}}async function price(){try{let d=await api('/api/price',{method:'POST',body:JSON.stringify({currency:currency.value,perceived_value:+value.value,differentiation:+diff.value,complexity:+complex.value,delivery_cost:+cost.value})});priceOut.innerHTML=`<p class="metric">${d.recommended_price} ${d.currency}</p><div class="muted">Confiance indicative : ${d.confidence}%</div>`}catch(e){alert(e.message)}}async function downloadProduct(){let r=await fetch('/api/export',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(current)}),b=await r.blob(),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=(current.slug||'produit')+'.md';a.click()}async function call(u){try{out.textContent=JSON.stringify(await api(u),null,2)}catch(e){out.textContent=e.message}}init();</script></body></html>'''
@app.get('/',response_class=HTMLResponse)
def home(): return HTML
