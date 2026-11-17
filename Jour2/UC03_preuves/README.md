# Preuves UC-03

Toutes les sorties viennent de l'exécution réelle du 17/11/2026 (Docker). Chaque preuve est datée dans son fichier.

## environnement/
| Preuve | Ce qu'elle démontre |
|---|---|
| `environnement.txt` | OS, Java, version Hadoop 3.5.0, configuration, `jps` du NameNode et du DataNode, rapport HDFS : environnement mono-nœud fonctionnel |
| `namenode_overview.png` | Interface web du NameNode : version 3.5.0, état `active`, sécurité désactivée, 2 blocs, capacité |
| `namenode_datanodes.png` | Le DataNode actif, sa capacité et son nombre de blocs |
| `docker_ps.txt` | Les conteneurs de l'environnement et leurs images (`apache/hadoop:3.5.0`) |

## hdfs/
| Preuve | Ce qu'elle démontre |
|---|---|
| `commandes_hdfs.txt` | Commandes `hdfs dfs` (ls, mkdir, du) et leurs résultats : création de l'arborescence |
| `depot_et_controles.txt` | Inspection des sources, `put`, `ls`, `du`, `stat`, `cat`, `fsck`, comparaison SHA-256 et `cmp` source / HDFS |
| `explorer_raw_initial.png` | Les 2 fichiers déposés dans `raw/tpcxbb/initial` : tailles, droits, réplication 1, bloc 128 Mo |

## data_lake/
| Preuve | Ce qu'elle démontre |
|---|---|
| `schema_arborescence.png` | Schéma de l'arborescence `/retail-lake` (zones et état de chaque dossier) |
| `explorer_retail_lake.png` | L'arborescence réellement créée, vue dans l'explorateur HDFS |
