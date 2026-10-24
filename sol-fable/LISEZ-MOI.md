# Firecrawl — copie Sol-Fable

Copie du dépôt officiel créée le 24 octobre 2026 pour Fabien, à sa demande. La branche `sol-fable-v2.11.162` conserve le code de la version officielle `v2.11.162`, commit `7666c1f9ae8720a6bba271e0f60b6a217f8a5210`. Les ajouts Sol-Fable sont regroupés dans ce dossier. La licence AGPL et les mentions d'origine sont conservées.

## État réel

- Dépôt GitHub copié et branche dédiée créée.
- Les 1 704 fichiers suivis de la version amont sont conservés sans modification.
- REA est utilisé pour une analyse statique ciblée ; consulter `rea-evidence.json` et `rea-summary.md` pour sa portée et ses limites.
- Aucun serveur Firecrawl autonome n'a été démarré : Docker Engine et Compose sont absents des environnements d'exécution vérifiés.
- Aucun test HTTP de cette copie n'a donc été validé. Le connecteur Firecrawl existant dans ChatGPT n'a pas été remplacé.

## Démarrer une évaluation sur un hôte Docker

Ce parcours est destiné à un hôte de confiance. Il nécessite Git, Docker Engine, Docker Compose v2, Python 3 et curl. Ce n'est pas une configuration de production publique.

```bash
git clone --branch sol-fable-v2.11.162 https://github.com/elgrande952/firecrawl.git firecrawl-sol-fable
cd firecrawl-sol-fable
python3 - <<'PY'
import os, secrets
# Création exclusive : ne remplace aucun fichier de configuration existant.
fd = os.open('.env', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w') as f:
    f.write('USE_DB_AUTHENTICATION=false\n')
    f.write('POSTGRES_USER=postgres\nPOSTGRES_DB=postgres\n')
    f.write('POSTGRES_PASSWORD=' + secrets.token_hex(32) + '\n')
    f.write('PORT=127.0.0.1:3002\nINTERNAL_PORT=3002\n')
PY
```

La valeur `PORT` ci-dessus conserve l'API sur la boucle locale, au lieu de l'exposer sur toutes les interfaces. Utiliser un terminal sans variables de fournisseurs héritées ; ne pas ajouter de clés OpenAI, Firecrawl, de proxy ou de fournisseur payant pour ce premier test.

Vérifier d'abord la configuration rendue. Cette commande affiche des valeurs sensibles : ne pas publier sa sortie.

```bash
docker compose config --quiet
docker compose up --build -d api playwright-service redis rabbitmq nuq-postgres
docker compose ps --all
```

La liste de services est volontairement explicite : le fichier amont déclare également un backend FoundationDB expérimental. Ne pas définir `NUQ_BACKEND` pour ce parcours PostgreSQL. Les images auxiliaires du Compose amont utilisent certaines étiquettes flottantes ; seule la version du code source est ici fixée. Pour une exploitation reproductible, fixer aussi les images par digest après validation sur l'hôte retenu.

## Vérifier le fonctionnement

```bash
curl --fail --silent --show-error --max-time 5 \
  http://127.0.0.1:3002/v0/health/readiness

curl --fail-with-body --silent --show-error --max-time 75 \
  -X POST http://127.0.0.1:3002/v2/scrape \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com","formats":["markdown"],"timeout":60000}'
```

Le premier résultat ne prouve que la disponibilité HTTP. Le second doit renvoyer `success: true`, du Markdown non vide et un statut de page 200. Ces commandes sont fournies pour l'hôte cible : elles n'ont pas été exécutées contre une instance de cette copie.

## Ce que la copie comprend

Le noyau open source inclut API, workers, collecte de pages, crawl, map et routes de recherche, ainsi que le service Playwright. La recherche dépend des moteurs accessibles. Les fonctions utilisant un modèle nécessitent une configuration supplémentaire.

Les services cloud Agent, Browser/Interact et le tableau de bord géré ne sont pas reproduits par cette copie. Fire-engine, nécessaire à certaines fonctions avancées, n'est pas inclus dans la pile par défaut. Conserver la distinction entre disponibilité du code, démarrage du serveur et tests fonctionnels réussis.

## Raccordement futur à ChatGPT/Codex

Le serveur MCP officiel distinct est `firecrawl/firecrawl-mcp-server`. Il peut cibler une API auto-hébergée avec `FIRECRAWL_API_URL`. Cette variable doit être explicite pour éviter un départ vers le cloud par défaut. Son installation seule ne démarre pas le moteur Firecrawl.

Un raccordement distant nécessite d'abord un hébergement persistant, des tests réels, une authentification adaptée et HTTPS. Ne pas exposer publiquement le démarrage local sans authentification. Prévoir aussi stockage durable et sauvegardes avant une exploitation continue. Aucun achat, raccordement à Ollama ni nouveau modèle n'a été effectué pour cette copie.

## Sources

- Dépôt : https://github.com/firecrawl/firecrawl
- Guide officiel : https://docs.firecrawl.dev/contributing/self-host
- Comparaison : https://docs.firecrawl.dev/contributing/open-source-or-cloud
- MCP officiel : https://github.com/firecrawl/firecrawl-mcp-server
