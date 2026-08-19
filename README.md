# Chariot-bot
Un beau capable de commencer sur le chariot, il contrôle le tout, écris des fichiers pouvoir ou des produits
import os, httpx
async def generate(prompt):
    base=os.getenv("AI_BASE_URL","").rstrip("/")
    key=os.getenv("AI_API_KEY"); model=os.getenv("AI_MODEL")
    if not all([base,key,model]): raise RuntimeError("Configure AI_BASE_URL, AI_API_KEY et AI_MODEL")
    payload={"model":model,"messages":[
        {"role":"system","content":"Tu es un expert en produits numériques. Crée du contenu original. Ne garantis jamais des revenus."},
        {"role":"user","content":prompt}
    ],"temperature":0.7}
    async with httpx.AsyncClient(timeout=120) as c:
        r=await c.post(base+"/chat/completions",headers={"Authorization":f"Bearer {key}"},json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from chariow import ChariowClient
from pricing import recommend_price
from ai import generate

load_dotenv()
app=FastAPI(title="Chariow AI Bot v2")

class ProductRequest(BaseModel):
    niche:str
    audience:str
    product_type:str="ebook"
    currency:str="XAF"

HTML="""<!doctype html><html lang="fr"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chariow AI Bot</title><style>
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:760px;margin:auto;padding:20px;background:#f6f6f6}
.card{background:white;border-radius:18px;padding:18px;margin:12px 0;box-shadow:0 2px 12px #0001}
input,select,button{width:100%;padding:14px;margin:7px 0;border-radius:12px;border:1px solid #ddd;font-size:16px}
button{background:#111;color:white;font-weight:700}.ok{color:green}.err{color:#b00020}
pre{white-space:pre-wrap}
</style><div class=card><h1>🤖 Chariow AI Bot</h1><button onclick="connect()">Tester Chariow</button><div id=status></div></div>
<div class=card><h2>Créer un produit</h2>
<input id=n placeholder="Niche (ex: Excel pour entrepreneurs)">
<input id=a placeholder="Audience (ex: petits commerçants)">
<select id=t><option>ebook</option><option>template</option><option>mini-course</option><option>guide</option></select>
<select id=c><option>XAF</option><option>USD</option></select>
<button onclick="create()">Créer le produit</button><pre id=out></pre></div>
<script>
async function connect(){let r=await fetch('/api/chariow');let j=await r.json();status.innerHTML=r.ok?'<span class=ok>✓ Chariow connecté</span>':'<span class=err>✗ '+j.detail+'</span>'}
async function create(){out.textContent='Génération...';let r=await fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({niche:n.value,audience:a.value,product_type:t.value,currency:c.value})});let j=await r.json();out.textContent=JSON.stringify(j,null,2)}
</script></html>"""

@app.get("/",response_class=HTMLResponse)
def home(): return HTML

@app.get("/api/chariow")
async def chariow():
    try:return await ChariowClient().store()
    except Exception as e: raise HTTPException(400,str(e))

@app.get("/api/products")
async def products():
    try:return await ChariowClient().products()
    except Exception as e: raise HTTPException(400,str(e))

@app.post("/api/generate")
async def gen(req:ProductRequest):
    prompt=f"""Crée un produit numérique original.
Niche: {req.niche}; audience: {req.audience}; type: {req.product_type}.
Donne : titre, promesse, plan détaillé, contenu, bonus, description de vente,
SEO, mots-clés, 5 angles marketing et limites. Ne promets pas de rentabilité garantie."""
    try:
        content=await generate(prompt)
        return {"product":content,"pricing":recommend_price(req.currency)}
    except Exception as e: raise HTTPException(400,str(e))
import os, httpx
BASE="https://api.chariow.com/v1"

class ChariowClient:
    def __init__(self):
        key=os.getenv("CHARIOW_API_KEY")
        if not key: raise RuntimeError("CHARIOW_API_KEY manquante")
        self.headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"}

    async def store(self):
        async with httpx.AsyncClient(timeout=30) as c:
            r=await c.get(f"{BASE}/store",headers=self.headers); r.raise_for_status(); return r.json()

    async def products(self):
        async with httpx.AsyncClient(timeout=30) as c:
            r=await c.get(f"{BASE}/products",params={"per_page":100},headers=self.headers)
            r.raise_for_status(); return r.json()
# Utilisation sur iPhone

L'iPhone n'a pas besoin d'exécuter Python.

1. Déploie le dossier sur un serveur avec HTTPS.
2. Configure les variables `.env` sur le serveur.
3. Lance `uvicorn app:app --host 0.0.0.0 --port 8000` (ou utilise la commande de démarrage de ton hébergeur).
4. Ouvre l'URL HTTPS dans Safari.
5. Appuie sur « Tester Chariow ».
6. Renseigne une niche et une audience.
7. Appuie sur « Créer le produit ».

Pour un vrai fonctionnement 24/7, le serveur doit rester en ligne.
def recommend_price(currency="XAF", value_score=75, competition_score=50, audience_score=75):
    score = value_score*.45 + (100-competition_score)*.20 + audience_score*.35
    bands = [3000,5000,7500,10000,15000,20000,30000,50000] if currency=="XAF" else [7,9,12,17,24,29,39,59]
    idx=min(len(bands)-1,max(0,int(score/100*len(bands))))
    return {"score":round(score,1),"recommended_price":bands[idx],"currency":currency}
# Chariow AI Product Bot v2 — iPhone/Web

Cette version est pensée pour être utilisée depuis Safari sur iPhone :
le bot tourne sur un serveur, et l'iPhone sert d'interface web.

Fonctions :
- connexion Chariow côté serveur avec API key ;
- test de connexion ;
- lecture de la boutique et des produits publiés ;
- génération de produit numérique avec IA ;
- recommandation de prix en XAF/USD ;
- brouillon de page de vente et marketing ;
- bouton de publication isolé, activable seulement lorsqu'un endpoint officiel de création Chariow est confirmé.

Sécurité :
- la clé Chariow ne doit jamais être envoyée au navigateur ;
- elle est conservée côté serveur dans .env ;
- ne partage jamais ta clé API dans le chat.

Lancement :
1. installer Python 3.11+
2. pip install -r requirements.txt
3. cp .env.example .env
4. remplir .env
5. uvicorn app:app --host 0.0.0.0 --port 8000

Pour l'iPhone, déployer ce serveur sur un hébergeur HTTPS puis ouvrir son URL dans Safari.
fastapi
uvicorn[standard]
httpx
python-dotenv
pydantic
