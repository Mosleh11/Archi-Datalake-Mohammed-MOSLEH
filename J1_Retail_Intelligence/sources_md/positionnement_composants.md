# UC-02 – Positionnement des composants

Le statut vient du référentiel du TP et du cours. La colonne « État dans ce TP » dit honnêtement ce qui a été fait : **aucun composant n'est installé ni déployé au Jour 1**. Seul Python a été utilisé (scripts d'analyse).

| Composant | Statut dans le parcours | Rôle dans l'architecture | Zone / couche | État dans ce TP | Repli si indisponible |
|---|---|---|---|---|---|
| Linux / Ubuntu | Obligatoire | Environnement local de référence | tout | Non utilisé (analyse faite sous Windows avec Python) | VM ou WSL |
| Python | Obligatoire | Exploration, scripts de contrôle, traitements | Bronze → Silver | **Utilisé** : `analyse_kit.py`, `controles_simples.py`, `recuperation_zip.py` | – |
| Hadoop / HDFS | Obligatoire | Stockage distribué local des zones Bronze, Silver, Gold | Stockage | Conçu seulement (Jour 2) | Dossiers du système de fichiers local, avec le même plan de chemins (repli documenté) |
| Apache NiFi | Obligatoire | Ingestion et orchestration des flux de fichiers | Ingestion | Conçu seulement (Jour 2) | Scripts Python + planificateur (repli documenté) |
| Apache Spark / PySpark | Obligatoire | Transformations distribuées : typage, contrôles, jointures, Parquet | Silver, Gold | Conçu seulement (Jour 3) | Python (pandas) sur échantillon |
| Parquet | Format de référence | Stockage colonnaire des zones Silver et Gold | Silver, Gold | Conçu seulement | – |
| HBase | **Facultatif** | Approfondissement NoSQL ; pas nécessaire pour nos besoins (pas de lecture à la clé à faible latence) | – | Non retenu | Sans objet |
| PDGF | Selon kit disponible | Générateur de données | Source | Non utilisé : le kit est fourni déjà généré | Sans objet |
| Delta Lake | **Facultatif** | Approfondissement Lakehouse (transactions sur Parquet) | Silver, Gold (évolution) | Non retenu, évoqué comme évolution | Parquet simple |
| ADLS Gen2 | Objectif obligatoire (cible cloud) | Stockage cloud des zones, équivalent de HDFS | Stockage cloud | Conçu seulement ; déclinaison au Jour 4 | Conception logique sans déploiement |
| Azure Data Factory | Présentation / étude | Orchestration et intégration cloud, équivalent de NiFi | Ingestion cloud | Étudié (conception) | – |
| Azure Synapse | Présentation / étude | Services analytiques cloud (requêtes sur Gold) | Exposition cloud | Étudié (conception) | – |

## Remarques

- HBase et Delta Lake ne conditionnent pas la validation. Ils ne sont donc pas dans la solution de base.
- HDFS et NiFi sont obligatoires mais avec « repli documenté » dans le cours : si l'environnement ne permet pas de les faire tourner, on documente la solution de remplacement.
- ADLS Gen2 est un objectif obligatoire, mais son déploiement se fait au Jour 4 ; ici on fait seulement sa conception logique (voir `local_vers_azure`).
- ADF et Synapse sont à présenter et étudier, pas à déployer.
