# J4-09 – Sécurité et gestion des accès

## Matrice des droits (principe du moindre privilège)

| Profil | Bronze | Silver | Gold | Quality / documentation |
|---|---|---|---|---|
| Équipe ingestion (NiFi / ADF, identité de service) | écriture contrôlée (dépôt de nouveaux fichiers, pas de suppression) | lecture limitée | aucun accès par défaut | aucun |
| Équipe data engineering | lecture ; écriture seulement pour les reprises | lecture / écriture | écriture contrôlée | lecture / écriture |
| Analyste métier | aucun accès par défaut | lecture selon besoin | lecture | lecture |
| Administrateur | gestion selon habilitation | gestion selon habilitation | gestion selon habilitation | gestion selon habilitation |

Les droits sont donnés à des **groupes** (pas à des personnes) et aux identités de service plutôt qu'à des comptes partagés. Aucun droit d'administration n'est donné « par simplicité ».

## Quatre notions à ne pas confondre

| Notion | Rôle | Exemple dans ce projet |
|---|---|---|
| **Azure RBAC** | autorise des actions sur une ressource Azure, selon un rôle et un périmètre (abonnement, groupe de ressources, compte, conteneur) | rôle *Storage Blob Data Reader* au groupe des analystes sur le conteneur |
| **ACL du Data Lake** | permissions lecture / écriture / exécution sur chaque répertoire et fichier ; l'exécution est nécessaire sur les répertoires parents pour atteindre un fichier | lecture sur `gold/`, aucune ACL sur `bronze/` pour les analystes |
| **Identité et authentification** | prouver qui agit : utilisateurs, groupes, applications, identités managées dans Microsoft Entra ID | un pipeline ADF utilise une identité managée plutôt qu'un mot de passe dans un script |
| **Secrets et informations sensibles** | mots de passe, clés, jetons ; ne vont jamais dans le code, les notebooks ni Git | stockés dans Key Vault ; en local, fichier d'environnement ignoré par Git (`nifi.env`, comme au Jour 2) |

RBAC et ACL ne sont pas interchangeables : ils se complètent, et il faut vérifier les **droits effectifs** de l'identité utilisée (un rôle RBAC de données peut suffire, sinon ce sont les ACL qui décident).

## Règles de gouvernance proposées

- Séparation des environnements : un compte de stockage (ou un conteneur) de test distinct de celui de production, avec des droits distincts.
- Séparation des responsabilités : l'équipe qui ingère n'écrit pas dans Gold ; celle qui analyse ne modifie pas Bronze.
- Classification : les données TPCx-BB sont synthétiques, mais elles incluent des champs de type personnel (nom, e-mail, date de naissance). Au Jour 3, Silver ne conserve que le domaine de l'e-mail ; la même règle de minimisation s'applique à la sortie vers Azure.
- Chiffrement en transit (TLS 1.2 minimum) et accès public aux données désactivé.
- Journalisation : activer les journaux d'accès du compte de stockage pour savoir qui a lu ou écrit quoi.
- Aucun secret, mot de passe, clé ou jeton dans le dépôt Git ni dans un document partagé.

## Équivalent local (parcours B)

Comptes et droits du système (dossiers `bronze/` en écriture seulement pour le traitement d'ingestion), fichier d'environnement ignoré par Git pour les mots de passe, conteneur Docker pour séparer l'environnement d'exécution. Limites : pas de rôles fins, pas de journal d'accès, pas de séparation réelle entre développement et production sur un seul poste.
