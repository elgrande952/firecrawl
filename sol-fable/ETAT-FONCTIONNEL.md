# État fonctionnel de la copie Firecrawl

Vérifications du 24 octobre 2026. Le code de référence est la version open source `v2.11.162`, commit `7666c1f9ae8720a6bba271e0f60b6a217f8a5210`. Les 1 704 fichiers amont sont identiques. Les adaptations d’exploitation et les preuves sont séparées dans `sol-fable/`.

| Élément | Preuve obtenue | Limite |
|---|---|---|
| Code source | Identité des objets Git et des 1 704 chemins amont vérifiée | Identité avec cette version publiée, pas avec les services cloud privés |
| Analyse REA | Huit exécutions, 160 fichiers distincts ; cinq analyses ciblées sans avertissement de budget | Analyse statique ; les graphes des trois grandes analyses sont partiels |
| Service Playwright | Compilation, santé, rendu JavaScript et réponse 404 réels sur une fixture contrôlée | Ce test isolé ne valide pas toute la collecte Internet |
| Pile indépendante | API, Playwright, Redis, RabbitMQ et PostgreSQL construits et déclarés sains dans GitHub Actions | Environnement temporaire de vérification |
| Collecte `/v2/scrape` | Réponse réelle `success: true`, page 200 et Markdown non vide | Un site et un parcours ; ni charge ni couverture de tout le Web |
| MCP officiel | Paquet 3.34.1 installé ; protocole vérifié puis collecte Internet réelle réussie via l'API indépendante : page 200 et 958 caractères | Un appel `firecrawl_scrape` validé ; les autres outils ne sont pas tous fournis par le noyau auto-hébergé |
| Crawl, map, search | Routes et contrôleurs copiés ; chemins observés par REA | Ces trois fonctions n’ont pas fait l’objet d’un test fonctionnel dans ce lot |
| Agent, Browser, Interact | Dépendances distantes identifiées dans les contrôleurs | Services externes absents ; fonctions non validées |
| Mise à disposition continue dans ChatGPT | Aucun réglage global modifié | Hébergement persistant et passerelle HTTPS authentifiée encore nécessaires |

## Résultats d’intégration

Premier passage : [run 40123942884](https://github.com/elgrande952/firecrawl/actions/runs/40123942884). La construction et la collecte ont fonctionné. Le job a été marqué en échec par une assertion trop stricte qui cherchait le titre dans le Markdown ; le titre était correctement présent dans `metadata.title`. Le contrôle a été corrigé et une seconde vérification a été lancée. Le reçu initial est conservé dans `ci/first-run.json`.

Seconde vérification : [run 40124612089](https://github.com/elgrande952/firecrawl/actions/runs/40124612089). La construction, la santé des cinq services et la collecte directe ont réussi. L’appel MCP a révélé une valeur d’intégration personnalisée refusée par l’API. Le lanceur a été corrigé pour ne pas injecter ce paramètre optionnel ; les deux tests locaux du MCP ont ensuite réussi. Le reçu de ce passage est conservé dans `ci/second-run.json`.

Troisième vérification : [run 40125178187](https://github.com/elgrande952/firecrawl/actions/runs/40125178187), commit source `5632ed527d274b503b282558230e060cb5affae1`. **Tous les contrôles du job ont réussi** : huit tests du lanceur, configuration, construction et santé des cinq services, collecte publique directe, puis collecte réelle via MCP. Les deux collectes ont renvoyé un statut de page 200 et 958 caractères de Markdown. Le test MCP s'est terminé le 24 octobre 2026 à 21 h 30 min 30 s, heure de Paris ; l'arrêt des cinq services a été confirmé à 21 h 30 min 32 s. Les preuves sont dans `ci/final-run.json` et `verification-2026-10-24.json`.

Les essais ne publient ni serveur public ni image. Les services temporaires sont arrêtés en fin de job. Aucun achat de crédits d’API ou de modèle. Les deux tâches planifiées reprises du projet d’origine (`npm-audit.yml` et `publish-elixir-sdk.yml`) sont désactivées dans ce fork ; leurs fichiers restent conservés. Le test d’intégration ajouté se déclenche manuellement.

## Utilisation et traçabilité

- [Démarrage de la pile indépendante](deploy/README.md)
- [Serveur MCP officiel fixé et lanceur](mcp/README.md)
- [Rapport REA élargi](evidence/REA-ANALYSE-ETENDUE.md)
- [Preuves Playwright et Chromium](runtime-tests/runtime-verification.json)

Une copie identique au code publié est vérifiable. Une identité complète avec Firecrawl Cloud n’est pas établie : les services internes, le tableau de bord géré et certaines fonctions avancées ne sont pas fournis par ce dépôt.
