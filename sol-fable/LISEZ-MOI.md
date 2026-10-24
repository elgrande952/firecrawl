# Firecrawl — copie Sol-Fable

Copie du dépôt officiel créée le 24 octobre 2026 pour Fabien, à sa demande. La branche `sol-fable-v2.11.162` conserve le code de la version officielle `v2.11.162`, commit `7666c1f9ae8720a6bba271e0f60b6a217f8a5210`. Les ajouts Sol-Fable sont regroupés dans ce dossier. La licence AGPL et les mentions d'origine sont conservées.

## Améliorations vérifiées le 24 octobre 2026

- Analyse REA élargie : huit exécutions, 160 fichiers distincts examinés ; voir [le rapport](evidence/REA-ANALYSE-ETENDUE.md).
- Service Playwright officiel compilé et lancé : santé HTTP 200, rendu JavaScript réel sur une page de test contrôlée et traitement d’une réponse 404 ; voir [les preuves](runtime-tests/runtime-verification.json).
- [Kit de déploiement](deploy/README.md) : cinq services, volumes persistants, contrôles de santé et lanceur vérifié. Le parcours ci-dessous utilise ce kit.
- [MCP officiel](mcp/README.md) : version 3.34.1 installée, protocole vérifié puis collecte réelle réussie via l'API indépendante. Aucune modification globale de ChatGPT/Codex et aucun raccordement permanent annoncé.

## État réel

- Dépôt GitHub copié et branche dédiée créée.
- Les 1 704 fichiers suivis de la version amont sont conservés sans modification.
- REA est utilisé pour une analyse statique ciblée ; consulter `rea-evidence.json` et `rea-summary.md` pour sa portée et ses limites.
- La pile autonome a été construite et démarrée dans un environnement temporaire GitHub Actions : les cinq services sont devenus sains et une collecte réelle de `https://example.com` a renvoyé du Markdown avec un statut de page 200.
- L'environnement de travail local ne dispose pas de Docker Engine. La vérification complète a donc été effectuée dans GitHub Actions. Aucun hébergement permanent n'est annoncé ; le connecteur Firecrawl existant dans ChatGPT n'a pas été remplacé.
- Consulter [l'état fonctionnel détaillé](ETAT-FONCTIONNEL.md) et [le reçu consolidé](verification-2026-10-24.json) pour distinguer les contrôles réussis des fonctions encore non testées.
- [Vérification complète réussie](https://github.com/elgrande952/firecrawl/actions/runs/40125178187) le 24 octobre 2026 à 21 h 30, heure de Paris : collecte directe et collecte via MCP, page 200 et 958 caractères de Markdown. Les cinq services temporaires ont ensuite été arrêtés.

## Démarrer une évaluation sur un hôte Docker

Ce parcours est destiné à un hôte de confiance. Il nécessite Git, Docker Engine, le plugin Docker Compose v2 et Python 3. Ce n'est pas une configuration de production publique.

```bash
git clone --branch sol-fable-v2.11.162 https://github.com/elgrande952/firecrawl.git firecrawl-sol-fable
cd firecrawl-sol-fable
python3 sol-fable/deploy/control.py --check
python3 sol-fable/deploy/control.py init
python3 sol-fable/deploy/control.py config
python3 sol-fable/deploy/control.py up
python3 sol-fable/deploy/control.py status
```

Le lanceur génère les secrets locaux sans écraser une configuration compatible existante. Il conserve l'API sur `127.0.0.1:3002` et n'hérite pas des variables de fournisseurs du terminal. Aucune clé cloud n'est nécessaire pour ce premier test.

La pile utilise PostgreSQL ; FoundationDB n'est pas démarré. Certaines images auxiliaires et images de base restent à des étiquettes flottantes. Pour une exploitation reproductible, fixer aussi leurs digests après validation sur l'hôte retenu.

## Vérifier le fonctionnement

```bash
python3 sol-fable/deploy/smoke.py
```

Le script vérifie la disponibilité HTTP puis une véritable collecte : `success: true`, Markdown non vide et statut de page 200. Ce parcours a été exécuté contre la copie dans GitHub Actions. Pour arrêter sans supprimer les volumes : `python3 sol-fable/deploy/control.py stop`.

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
