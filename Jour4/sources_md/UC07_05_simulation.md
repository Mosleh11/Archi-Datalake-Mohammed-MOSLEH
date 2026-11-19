# J4-10 – Preuves et dossier de simulation

## Preuves de réalisation (locales)

| Preuve | Fichier |
|---|---|
| Arborescence `retail-intelligence/` réellement créée sur disque (bronze, silver, gold, quality, documentation) | `preuves/uc07/arborescence_lake_local.txt` |
| Manifeste des 10 fichiers déposés : chemin, taille, SHA-256 | `preuves/uc07/manifeste_lake_local.json` |
| Journal d'exécution : 10 déposés, 10 vérifiés, 0 écart | `preuves/uc07/uc07_arborescence_locale_log.txt` |
| Script | `scripts/uc07_arborescence_locale.py` |
| Fichiers déposés | `preuves/uc07/lake_local/retail-intelligence/` |

**Il n'y a aucune capture d'écran du portail Azure : aucune ressource Azure n'a été créée.**

## Dossier de simulation Azure

1. **Organisation cible** : conteneur `retail-intelligence` avec `bronze/`, `silver/`, `gold/`, `quality/`, `documentation/` (voir J4-08).
2. **Ressources nécessaires** : un groupe de ressources, un compte de stockage avec HNS activé, un conteneur ; en option Data Factory et un espace Synapse (non exigés).
3. **Opérations de création et de dépôt** : commandes listées dans `preuves/uc07/simulation_commandes/commandes_azure_non_executees.md`.
4. **Contrôles qui seraient effectués** : HNS activé sur le compte ; répertoires présents ; fichier listé avec la même taille (26 305 octets) que dans le manifeste ; refus pour un compte de test sans droit sur `gold/` ; aucun secret dans le dépôt ; groupe de ressources supprimé à la fin.
5. **Distinction faite / non fait** :

| Étape | Statut |
|---|---|
| Création de la hiérarchie de dossiers et dépôt de 10 fichiers avec vérification d'intégrité | **faite en local** |
| Création du compte ADLS Gen2, du conteneur, dépôt sur Azure, test des droits | **non faite** (simulation) |
| Pipeline ADF, espace Synapse, Spark Pool | **non faits** (étude) |
| MinIO, Iceberg, Trino, Airflow, Superset | **non installés** (étude) |

## Coûts, quotas et risques (étude)

- Aucune estimation chiffrée n'est donnée : les tarifs et l'offre gratuite sont à vérifier au moment de l'inscription, et le volume du kit complet est inconnu (le zip reçu fait environ 510 Mo et est tronqué).
- Postes de coût à surveiller : volume stocké et redondance choisie, nombre d'opérations, calcul (pools Spark, Synapse SQL), exécutions de pipelines, transferts. Le calcul reste le poste le plus facile à laisser tourner par erreur : un pool Spark non arrêté est facturé.
- Règles retenues : budget et alertes à définir, ressources de test supprimées après usage, vérification des ressources persistantes (disques, IP, pools), **un seul compte Azure** (pas de second compte pour contourner l'offre gratuite).
- Sécurité en production : droits excessifs, secrets dans le code, absence de journalisation, données personnelles même synthétiques ; région et conformité à valider.

## Justification des choix et limites

Le parcours B a été choisi parce qu'aucun abonnement autorisé n'est disponible et que le TP demande de préférer le local en cas de doute. La matérialisation locale de l'arborescence permet de vérifier l'organisation, les noms et l'intégrité des fichiers, mais **ne prouve rien sur le comportement d'Azure** (HNS, ACL, RBAC, coûts) : ces points restent à valider sur un compte autorisé.

## Questions de recul (8 à 14)

8. **Rôle d'ADLS Gen2 dans l'architecture ?** C'est le stockage du Data Lake : il conserve les zones bronze, silver et gold et les met à disposition d'ADF, de Spark et de Synapse. Il ne calcule pas.
9. **Intérêt du HNS ?** Des répertoires réels : renommer ou supprimer un dossier de fichiers Parquet en une opération, et poser des ACL par répertoire, ce que le stockage Blob à plat ne permet pas.
10. **RBAC et ACL ?** Le RBAC donne des rôles sur les ressources Azure (compte, conteneur) ; les ACL fixent lecture, écriture et exécution sur chaque répertoire et fichier. Ils se complètent, et il faut contrôler les droits effectifs.
11. **Quand ADF est utile ?** Quand il faut déplacer des données de façon planifiée ou déclenchée par un événement, enchaîner des étapes, gérer les erreurs et superviser. Ici : copier les fichiers du kit vers `bronze/`, ce que NiFi a fait en local au Jour 2.
12. **Rôle de Synapse ?** Réunir un espace de travail d'analyse : Spark pour exécuter les scripts du Jour 3 sur ADLS, SQL pour interroger `gold/`, Studio pour les notebooks et les pipelines.
13. **Réellement déployé / théorique ?** Déployé en local : Spark, Parquet, Jupyter, Matplotlib, NiFi et HDFS (Jour 2), arborescence locale. Théorique : tout ce qui est Azure (ADLS, ADF, Synapse, Entra ID, RBAC, ACL, Key Vault) et MinIO, Iceberg, Trino, Airflow, Superset.
14. **Risques de coût ou de sécurité en production ?** Coût : calcul laissé allumé, volume et redondance, absence d'alerte budgétaire. Sécurité : droits trop larges, secrets dans le code, pas de journalisation, données personnelles dans la mauvaise zone, accès public ouvert.
