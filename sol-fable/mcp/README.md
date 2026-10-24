# MCP officiel pour la copie indépendante

Le serveur officiel `firecrawl-mcp` est fixé à **3.34.1** avec un verrou npm. Son code est fourni par Firecrawl, sous licence MIT ; il n'est pas une réimplémentation de l'API. Source inspectée : commit `da436cccdf3f51da530350b3c15753b4742aa8a2` du dépôt `firecrawl/firecrawl-mcp-server`.

Installation depuis ce dossier, avec Node >=22 et Python 3 :

```bash
npm ci --ignore-scripts --no-audit --no-fund
python3 run.py --api-url http://127.0.0.1:3002
```

`run.py` vérifie d'abord la disponibilité HTTP de l'API indépendante. Il conserve le transport standard MCP sur stdin/stdout. L'URL est obligatoire : aucune bascule automatique vers Firecrawl Cloud. Les clés cloud du terminal ne sont pas héritées. Si une passerelle d'authentification a été installée devant cette API, fournir uniquement sa clé dédiée dans `FIRECRAWL_SELF_HOSTED_API_KEY`. Ne pas inscrire de clé dans le dépôt.

Un client MCP local peut utiliser `python3` comme commande, avec le chemin absolu de `run.py` et les arguments `--api-url http://127.0.0.1:3002`. Aucun paramètre global du compte ChatGPT/Codex n'a été changé. Pour un raccordement distant à ChatGPT, il reste à déployer une passerelle HTTPS authentifiée sur un hébergement persistant.

## Tests réellement effectués

`python3 test_protocol.py -v` lance le véritable paquet officiel contre une API locale simulée. Il vérifie initialisation MCP, liste des outils, appel `firecrawl_scrape`, routage vers `/v2/scrape`, retour de la réponse et absence de transmission d'une clé cloud héritée. Les deux tests ont réussi. Voir `protocol-verification.json`.

Ce contrôle simulé est complété par `live_check.py`, qui a réellement appelé le MCP officiel contre la pile Firecrawl indépendante dans [GitHub Actions](https://github.com/elgrande952/firecrawl/actions/runs/40125178187). Le 24 octobre 2026 à 21 h 30, heure de Paris, `firecrawl_scrape` a récupéré `https://example.com` : statut de page 200, 958 caractères de Markdown, sans API simulée. Le test a réussi et les services temporaires ont été arrêtés. Le contrôle est reproductible depuis la racine du dépôt, après démarrage de la pile et installation npm :

```bash
python3 sol-fable/mcp/live_check.py
```

Le lanceur ne définit pas `FIRECRAWL_INTEGRATION` : une valeur personnalisée avait été refusée par l'API v2.11.162 pendant la seconde vérification. Cette incompatibilité a été corrigée et le parcours réel a été revérifié.

Les 26 outils annoncés par le paquet ne sont pas 26 fonctions auto-hébergées validées. Certains, dont Agent et Interact, requièrent des services externes non inclus. Le lanceur désactive les outils de retour d'expérience du cloud, sans modifier le paquet officiel.
