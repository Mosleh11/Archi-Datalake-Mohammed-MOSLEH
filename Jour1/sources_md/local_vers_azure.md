# UC-02 – Du local vers Azure

Cette partie est une **conception logique**. Aucune ressource Azure n'a été créée ni testée au Jour 1 (le Jour 4 couvre la déclinaison). Les points marqués « à valider » seront vérifiés dans la documentation Azure et sur un vrai compte.

## 1. Comparaison des deux environnements

| Élément | Local (parcours) | Cible cloud (Azure) |
|---|---|---|
| Système | Linux / Ubuntu | Services managés |
| Stockage | Hadoop / HDFS | Azure Data Lake Storage Gen2 (ADLS Gen2) |
| Zones | dossiers `/datalake/bronze`, `/silver`, `/gold` | conteneurs ou dossiers `bronze`, `silver`, `gold` |
| Ingestion | Apache NiFi | Azure Data Factory (étudié) |
| Traitements | Spark / PySpark, Python | Spark managé (ex. dans Synapse), à étudier |
| Analyse | requêtes Spark / SQL | Azure Synapse (étudié) |
| Format | Parquet | Parquet |
| Sécurité | droits HDFS, comptes Linux | identités Azure, RBAC et ACL |
| Coûts | matériel et temps d'administration | paiement à l'usage (stockage, opérations, calcul) |
| Montée en charge | ajout de nœuds à la main | extension du stockage et du calcul par service |
| Reprise sur panne | réplication des blocs HDFS (facteur à confirmer dans la configuration du cluster) | redondance du compte de stockage (à choisir) |

## 2. Cible cloud : éléments à définir

| Élément | Proposition |
|---|---|
| **Compte de stockage** | Un compte de stockage dédié au projet, avec l'espace de noms hiérarchique activé (ce qui en fait un ADLS Gen2). Une région unique proche des utilisateurs. Niveau de redondance à choisir selon le coût et le besoin de reprise (à valider). |
| **Espace de stockage et conteneurs** | Un conteneur par zone : `bronze`, `silver`, `gold` (+ `complements` si nécessaire). Chaque zone a ses droits propres. |
| **Organisation des données** | Même plan qu'en local : `bronze/tpcxbb/<table>/ingest_date=AAAA-MM-JJ/`, `silver/<table>/`, `gold/<sujet>/`. Mêmes règles de nommage pour que les traitements soient portables. |
| **Gestion des identités et accès** | Utilisateurs et groupes gérés dans Microsoft Entra ID (anciennement Azure AD). Pas de comptes partagés. Les services (ADF, Spark) utilisent une identité managée plutôt qu'un mot de passe. |
| **Permissions RBAC et ACL** | RBAC au niveau du compte ou du conteneur avec des rôles de type *Storage Blob Data Reader / Contributor / Owner*. ACL sur les dossiers pour affiner (ex. un groupe « magasins » en lecture sur un sous-dossier Gold). Règle : écriture Bronze réservée à l'ingestion, Gold en lecture pour le métier. |
| **Sécurité des secrets** | Aucun secret dans le code ni dans les fichiers : stockage dans Azure Key Vault, accès par identité managée. Clés du compte de stockage non utilisées si possible. |
| **Coûts et quotas** | Coût = volume stocké + nombre d'opérations + calcul utilisé. Leviers : Parquet compressé, niveaux d'accès froid pour Bronze ancien, suppression des intermédiaires, arrêt des ressources de calcul inutilisées, alertes budgétaires. Les quotas et limites par compte ou par région sont à vérifier dans la documentation Azure. |

## 3. Correspondance des flux

| Étape locale | Équivalent cloud |
|---|---|
| NiFi dépose le fichier en HDFS Bronze | ADF copie le fichier vers le conteneur `bronze` (ou dépôt direct) |
| Spark écrit Silver en Parquet sur HDFS | Spark écrit Silver en Parquet sur ADLS Gen2 |
| Spark écrit Gold en Parquet | idem, conteneur `gold` |
| Requêtes sur Gold | Synapse lit les Parquet de `gold` |
| Journaux locaux | journalisation et surveillance Azure (à étudier au Jour 4) |

## 4. Points d'attention

- Le volume réel du kit est inconnu : l'estimation du coût Azure est impossible aujourd'hui. On peut seulement dire que les 510 Mo reçus coûteraient très peu en stockage ; le coût dépendra surtout du kit complet et du calcul.
- Les données (même synthétiques) incluent des champs de type personnel : le choix de la région et des règles d'accès doit en tenir compte.
- Si Azure n'est pas accessible, cette conception reste une **simulation**, à distinguer d'un déploiement réel.
