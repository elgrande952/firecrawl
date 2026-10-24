# Analyse REA du service Playwright

REA 6.7.0 a analysé statiquement `apps/playwright-service-ts` de Firecrawl v2.11.162. La commande a terminé avec le code 0. Aucun navigateur ni serveur Firecrawl n’a été exécuté.

- `/scrape` : déclaration `app.post` observée dans `api.ts`, lignes 372–559.
- `/health` : candidat `app.get` inféré par REA, confiance faible, `api.ts`, lignes 347–370.
- Les relations dynamiques et la résolution des dépendances restent incomplètes.
- Le graphe contient des catégories heuristiques, notamment `electron-main` : cela ne démontre pas que ce microservice est une application Electron.

Cette preuve porte sur un composant du dépôt. Elle ne valide ni l’exécution de ses routes, ni la sécurité du produit, ni le fonctionnement de toute la pile.

Commande utilisée :

```bash
node /home/user/sol-fable-rea/runtime/node_modules/rea-agents/scripts/rea.mjs analyze-javascript-application /home/user/firecrawl-rea-analysis/source/apps/playwright-service-ts --analysis-timeout-ms 30000 --max-heap-mb 512 --json
```

Preuve complète : `rea-evidence.json`.

Identifiant : `ev_3d953fd07f9e44032040e3ae7b2afa8fefeaecb95f2895df85b88c6b6a9fa1bc`.

SHA-256 : `6e05da6eda3b437dc8241f72c1c85a6c305e5c9fc741d518437074f45d4ee299`.
