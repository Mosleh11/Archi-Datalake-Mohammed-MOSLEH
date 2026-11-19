# J4-07 – Architecture Azure cible

![azure](IMG:schema_architecture.png)

Schéma `architecture/schema_architecture.dot` (rendus `.png` et `.svg`). Vert : utilisé (données du kit). Orange en pointillés : étudié / proposé, **non déployé**. Les sources sont celles du kit TPCx-BB (7 tables reçues) ; les données complémentaires, s'il y en avait, seraient séparées dans leur propre dossier `bronze/complements/` (aucune ici).

## Les composants Azure et leurs relations

| Composant | Rôle dans le projet | Relation |
|---|---|---|
| Abonnement | cadre de facturation et d'accès ; ce n'est pas un serveur | contient les groupes de ressources |
| Groupe de ressources | conteneur logique des ressources du projet (ex. `rg-retail-intelligence`) ; sa suppression supprime tout | contient le compte de stockage, Data Factory, Synapse, Key Vault |
| Compte de stockage | ressource qui fournit le stockage ; avec HNS activé, il devient un ADLS Gen2 | contient les conteneurs |
| Conteneur (système de fichiers) | espace logique : `retail-intelligence` | contient les répertoires `bronze/`, `silver/`, `gold/`… |
| ADLS Gen2 | stockage du Data Lake, construit sur le stockage Blob, avec l'organisation hiérarchique | lu et écrit par ADF et Spark |
| Hierarchical Namespace (HNS) | arborescence réelle de répertoires et de fichiers | choisi à la création du compte |
| Microsoft Entra ID | identités : utilisateurs, groupes, applications, identités managées | reçoit les rôles RBAC et les ACL |
| Azure RBAC | autorise des actions sur une ressource Azure (compte, conteneur) selon un rôle | porté par une identité Entra |
| ACL | permissions (lecture, écriture, exécution) sur les répertoires et les fichiers | affinent le RBAC dans le Data Lake |

## Correspondance Azure / open source (responsabilités, pas seulement les noms)

| Fonction | Parcours Azure (étudié) | Parcours local (retenu) | Composant non déployé | Limite de l'équivalence |
|---|---|---|---|---|
| Stockage du lake | ADLS Gen2 | disque local et dossiers (Parquet) ; HDFS au Jour 2 | MinIO (stockage objet compatible S3) | un dossier local n'a ni redondance, ni gestion d'identité, ni montée en charge |
| Tables analytiques | fichiers Parquet / tables du Lakehouse | fichiers Parquet seuls | Apache Iceberg (format de table) | Parquet seul n'offre ni transaction ACID, ni historique, ni évolution du schéma gérée |
| Traitement distribué | Synapse Spark | Spark / PySpark local[4] (Docker) | cluster Spark | un seul nœud : pas de distribution réelle |
| Requêtes SQL | Synapse SQL | Spark SQL possible, non utilisé | Trino | Trino ne remplace pas à lui seul Synapse |
| Catalogue / métadonnées | catalogue des services Azure | aucun (chemins en dur dans les scripts) | Nessie ou Hive Metastore | pas de découverte ni de gestion centralisée des schémas |
| Ingestion / orchestration | Azure Data Factory | NiFi (Jour 2) et scripts lancés à la main (`lancer_tout.sh`) | Airflow | pas de déclenchement planifié ni de supervision centralisée |
| Visualisation | Power BI | Matplotlib dans Jupyter | Superset | graphiques statiques, pas de tableau de bord interactif |
| Identités et droits | Entra ID, RBAC, ACL | comptes et droits du système, conteneur Docker | — | pas de rôles fins ni de journal d'accès |
| Exécution | services managés | Docker sur le poste | — | pas de haute disponibilité |

Plusieurs briques open source sont nécessaires pour couvrir ce qu'offre Synapse seul : Spark pour le calcul, Trino ou Spark SQL pour les requêtes, Iceberg pour le format de table, un catalogue pour les métadonnées, un stockage objet ou fichier, Airflow pour l'orchestration. **Iceberg n'est pas « le Synapse open source »** : c'est un format de table.

## Architecture du parcours B (ce qui a vraiment tourné)

![local](IMG:parcours_b_local.png)

Schéma `architecture/parcours_b_local.dot`. Au Jour 3, Spark a lu des fichiers `.dat` locaux (cas 1 du TP) et non HDFS ; NiFi a alimenté HDFS au Jour 2.

## Rôle d'Azure Data Factory et de Synapse (étude)

| Service | Fonction | Éléments | Ne fait pas |
|---|---|---|---|
| ADLS Gen2 | stocker les données | conteneurs, répertoires, fichiers | ne calcule pas, n'orchestre pas |
| Azure Data Factory | intégrer, déplacer, orchestrer | pipeline, activité, jeu de données, service lié, déclencheur, supervision | ne remplace pas le moteur des transformations complexes |
| Synapse Analytics | analyser : espace de travail réunissant SQL, notebooks, Spark, pipelines | Synapse Studio, Spark Pool, capacités SQL | ne stocke pas les données (elles restent dans ADLS) |
| Spark (Synapse Spark Pool) | moteur de traitement distribué | PySpark, notebooks | un pool créé et laissé allumé est facturé |

Outils de visualisation Azure : Power BI se connecterait à `gold/` (via Synapse SQL ou des exports CSV) pour les usages analytiques ; il n'a pas été utilisé ici, les graphiques du Jour 4 sont faits avec Matplotlib.

Dans ce projet, ADF copierait les fichiers du kit vers `bronze/` (équivalent de NiFi au Jour 2), Synapse Spark exécuterait les scripts du Jour 3 (équivalent de `nettoyage.py` et `transformations.py` sur ADLS), Synapse SQL interrogerait `gold/` et Power BI présenterait les résultats. La création d'un pipeline ADF ou d'un espace Synapse n'est pas exigée dans le socle ; ils n'ont pas été créés.
