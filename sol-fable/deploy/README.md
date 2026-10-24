# Démarrage isolé de la copie Firecrawl

Ce kit conserve les Dockerfiles et le code de Firecrawl **v2.11.162**. Il remplace uniquement la configuration d'exploitation pour faciliter une évaluation indépendante : cinq services, stockage persistant, contrôles de santé, attente des dépendances et API publiée sur `127.0.0.1:3002`.

Les services sont `api`, `playwright-service`, `redis`, `rabbitmq` et `nuq-postgres`. FoundationDB n'est pas démarré. Le client FoundationDB reste installé par le Dockerfile officiel de l'API ; ce kit ne modifie pas ses dépendances. Les images auxiliaires et images de base conservent leurs étiquettes amont flottantes : un gel par digest reste à faire après un premier déploiement validé.

## Utilisation

Depuis la racine du dépôt, sur un hôte disposant de Python 3, Git, Docker Engine et du plugin Docker Compose :

```bash
python3 sol-fable/deploy/control.py --check
python3 sol-fable/deploy/control.py init
python3 sol-fable/deploy/control.py config
python3 sol-fable/deploy/control.py up
python3 sol-fable/deploy/control.py status
```

`init` génère deux secrets locaux aléatoires dans `.state/credentials.env` (permissions 0600). Une configuration existante compatible est conservée, jamais écrasée. Le dossier `.state` est exclu de Git. Les secrets ne sont pas affichés par le lanceur et les variables de fournisseurs présentes dans le terminal ne sont pas transmises aux services. Les paramètres Docker de connexion sont conservés pour permettre le contexte choisi par l'opérateur.

`config` valide la configuration sans afficher ses secrets. `up` construit le code officiel puis attend la disponibilité des cinq services. Les contrôles de santé ne remplacent pas un vrai test d'extraction. Les limites de concurrence sont réduites à deux pour cette première évaluation ; aucune quantité minimale de RAM n'est affirmée.

```bash
curl --fail-with-body --max-time 75 \
  -X POST http://127.0.0.1:3002/v2/scrape \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com","formats":["markdown"],"timeout":60000}'
```

Un succès fonctionnel exige `success: true`, du Markdown non vide et un statut de page 200. Si une fonction nécessite un fournisseur optionnel, son absence doit être rapportée, pas masquée par une réponse fictive.

Pour arrêter sans supprimer données ni conteneurs :

```bash
python3 sol-fable/deploy/control.py stop
```

Aucune action du lanceur ne supprime les volumes. Les volumes persistants ne constituent pas une sauvegarde : leur export, leur restauration et le plan de reprise doivent être définis et testés avant une exploitation continue. Ne pas changer les secrets après initialisation des bases sans procédure de rotation adaptée.

## Limites de ce livrable

L'API n'a pas d'authentification et reste accessible uniquement depuis la boucle locale de l'hôte Docker. Ne pas modifier la publication de port pour la rendre publique sans authentification et HTTPS. Le projet Compose réservé est `firecrawl-sol-fable` ; ne pas l'employer pour une autre pile.

La validation réalisée porte sur le lanceur et le contrat Compose. **Le démarrage complet, les migrations, les extractions et le comportement sous charge ne sont pas validés dans l'environnement courant, qui ne dispose pas d'un moteur Docker.** Consulter `validation.json` pour les contrôles effectivement exécutés.

Tests du lanceur, sans Docker ni accès payant :

```bash
python3 -m unittest discover -s sol-fable/deploy/tests -v
```
