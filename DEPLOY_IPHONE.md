# Déploiement depuis iPhone
1. Déposer tous les fichiers à la racine d'un dépôt GitHub privé.
2. Render -> New -> Web Service -> Git Provider -> dépôt.
3. Runtime Python.
4. Build: pip install -r requirements.txt
5. Start: uvicorn app:app --host 0.0.0.0 --port $PORT
6. Free pour test.
7. Ajouter les variables Render sans les envoyer dans le chat.
8. Deploy.
9. Tester /health puis l'URL principale.
