# Analyse REA élargie de Firecrawl

Analyse statique du code officiel v2.11.162 (`7666c1f9ae8720a6bba271e0f60b6a217f8a5210`), réalisée le 24 octobre 2026 avec REA 6.7.0. Aucun code applicatif ni navigateur n’a été exécuté pour cette analyse.

## Couverture réelle

| Périmètre | Fichiers lus | Sortie | Limite |
|---|---:|---|---|
| `apps/api/src/routes` | 7 | 0 | Graphe sémantique partiel : budget de résultat atteint |
| `apps/api/src/controllers/v2` | 56 | 0 | Graphe sémantique partiel : budget de résultat atteint |
| `apps/api/src/scraper/scrapeURL` | 97 | 0 | Graphe sémantique partiel : budget de résultat atteint |
| `apps/api/src/routes/v2.ts` | 1 | 0 | Pas d’avertissement de budget ; relations dynamiques non prouvées |
| `apps/api/src/controllers/v2/scrape.ts` | 1 | 0 | Pas d’avertissement de budget ; relations dynamiques non prouvées |
| `apps/api/src/controllers/v2/crawl.ts` | 1 | 0 | Pas d’avertissement de budget ; relations dynamiques non prouvées |
| `apps/api/src/controllers/v2/map.ts` | 1 | 0 | Pas d’avertissement de budget ; relations dynamiques non prouvées |
| `apps/api/src/controllers/v2/search.ts` | 1 | 0 | Pas d’avertissement de budget ; relations dynamiques non prouvées |

Les trois premiers périmètres couvrent **160 fichiers distincts** sans échec de parsing. Les cinq analyses ciblées portent sur des copies isolées dont les SHA-256 correspondent aux originaux ; elles ne constituent pas cinq fichiers supplémentaires.

REA a produit 63 observations de routes dans `routes/v2.ts` : {'inferred': 33, 'observed': 30}. Les catégories « observed » et « exact » décrivent une observation syntaxique, pas une requête HTTP réussie. Le préfixe `/v2` est monté dans `apps/api/src/index.ts:133`.

## Quatre fonctions centrales

| Méthode / chemin | Localisation | Résultat REA |
|---|---|---|
| `POST /v2/search` | `routes/v2.ts:180–187` | observed / exact |
| `POST /v2/scrape` | `routes/v2.ts:225–232` | observed / exact |
| `POST /v2/map` | `routes/v2.ts:264–270` | observed / exact |
| `POST /v2/crawl` | `routes/v2.ts:272–280` | observed / exact |

## Dépendances vérifiées dans le code

- Agent : `controllers/v2/agent.ts:160–166` relaie vers `EXTRACT_V3_BETA_URL + "/internal/extracts"` avec un secret d’interopérabilité. Copier le contrôleur ne fournit pas le service appelé.
- Browser : `controllers/v2/browser.ts:226–232` renvoie un statut 503 lorsque `BROWSER_SERVICE_URL` manque. `scrape-browser.ts:534–540` applique la même limite à Interact.
- Le moteur Playwright appelle `PLAYWRIGHT_MICROSERVICE_URL` (`scraper/scrapeURL/engines/playwright/index.ts:12–35`). La réponse exploitée contient le contenu, le code HTTP, le type de contenu et une erreur éventuelle ; le résultat indique un proxy de type basic.
- `scraper/scrapeURL/engines/index.ts:378–399` déclare `actions: false` et `screenshot: false` pour Playwright. Déclarer ces fonctions actives sans les implémenter puis les tester serait incorrect.

Ces constats de dépendances proviennent de la lecture des fichiers sources en complément de REA. Ils ne sont pas des résultats de tests en exécution.

## Preuves et limites

- `extended-summary.json` : reçus, statistiques, empreintes, limites et observations de routes.
- `rea-extended-evidence.zip` : les huit résultats REA complets et leurs reçus.
- SHA-256 de l’archive : `2f1351aa00d12f7b7932febb5d19b701899490c36c758a90a7179a2f222d50ae`.
- Aucun fonctionnement du serveur complet, comportement cloud identique, disponibilité permanente ou performance n’est établi par cette analyse.
- Aucun achat, appel d’API payante, modèle ou moteur natif supplémentaire.
