# Chariow AI Product Bot V3

Version reconstruite pour Render + iPhone.

## Fonctions
- interface mobile
- création de brouillons de produits digitaux
- titres, promesse, structure, contenu Markdown, CTA
- moteur de prix indicatif XAF/USD/EUR
- plan de validation/rentabilité sans promesse de gains
- intégration serveur Chariow : boutique, produits publiés, ventes
- export Markdown
- health check
- Render Python natif
- Dockerfile inclus pour éviter l'erreur précédente

## Render
Runtime Python recommandé.
Build: pip install -r requirements.txt
Start: uvicorn app:app --host 0.0.0.0 --port $PORT

Variables:
CHARIOW_API_KEY
CHARIOW_BASE_URL=https://api.chariow.com/v1
AI_API_KEY (optionnelle)
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL (optionnelle)

Ne jamais mettre les clés dans GitHub ou dans le navigateur.

## Limite Chariow
La documentation publique consultée documente actuellement la lecture de la boutique, des produits publiés et des ventes, ainsi que d'autres fonctions. Elle ne documente pas de endpoint public de création de produit. Cette V3 ne simule donc pas une publication automatique non documentée : elle prépare le produit et exploite les endpoints réellement documentés.
