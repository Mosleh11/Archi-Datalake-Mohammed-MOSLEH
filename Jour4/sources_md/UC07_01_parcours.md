# UC-07 – Transposition de la plateforme sur Azure

TP Jour 4 – Retail Intelligence Platform – Mastère Développement, Data & IA – IPSSI – Mohammed Mosleh. Réalisé le 19/11/2026.

## Parcours choisi : B (local / open source) avec étude de la déclinaison Azure

Je n'ai pas d'abonnement Azure autorisé pour ce TP, et le TP demande de ne créer aucune ressource payante sans validation du formateur : **aucune ressource Azure n'a été créée, aucun fichier n'a été déposé sur Azure, aucune capture du portail Azure n'est fournie.** La déclinaison Azure est donc une **étude et une simulation documentaire** ; la partie réellement exécutée est locale (parcours B).

## Ce qui est réalisé, simulé, étudié

| Élément | Statut | Preuve |
|---|---|---|
| Spark / PySpark 4.3.0 en mode local (Docker) : traitements Silver, Gold et analyses | **Réalisé** (Jours 3 et 4) | `Jour3/`, `Jour4/notebooks/` |
| Parquet comme format des zones Silver et Gold | **Réalisé** (Jour 3) | `Jour3/preuves/parquet/` |
| Jupyter + Matplotlib | **Réalisé** (Jour 4) | notebook exécuté, graphiques |
| HDFS et NiFi (stockage et ingestion locaux) | **Réalisé** au Jour 2 (HDFS non utilisé comme source au Jour 3) | `Jour2/` |
| Arborescence `retail-intelligence/` (bronze, silver, gold, quality, documentation) matérialisée sur disque local avec 10 fichiers du projet, relus et vérifiés par SHA-256 | **Réalisé** (équivalent local du dépôt ADLS) | `preuves/uc07/` |
| Compte de stockage ADLS Gen2, HNS, conteneur, dépôt d'un fichier | **Simulé** : conception et commandes décrites, non exécutées | `preuves/uc07/simulation_commandes/` |
| Entra ID, RBAC, ACL, Key Vault | **Étudié** (matrice et règles proposées) | ce rapport |
| Azure Data Factory, Synapse (Studio, Spark Pools, SQL) | **Étudié** (pas de déploiement, non exigé) | ce rapport |
| MinIO, Apache Iceberg, Trino, Airflow, Superset | **Étudié**, non installé | ce rapport |

Les données ne contiennent aucune donnée complémentaire hors TPCx-BB.
