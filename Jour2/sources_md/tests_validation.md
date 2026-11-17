# Tests et critères de validation

## UC-03 – HDFS

| Test | Résultat observé | Preuve |
|---|---|---|
| Accès HDFS | OK : 1 DataNode actif, NameNode `active` | `UC03_preuves/environnement/environnement.txt`, `UC03_preuves/environnement/namenode_overview.png` |
| Création des répertoires | OK : 11 répertoires sous `/retail-lake` | `UC03_preuves/hdfs/commandes_hdfs.txt`, `UC03_preuves/data_lake/explorer_retail_lake.png` |
| Dépôt de fichier | OK : 2 fichiers (151,46 Ko et 14,68 Mo) | `UC03_preuves/hdfs/depot_et_controles.txt`, `UC03_preuves/hdfs/explorer_raw_initial.png` |
| Lecture / récupération | OK : `-cat` et `-get`, contenu identique (`cmp`) | `UC03_preuves/hdfs/depot_et_controles.txt` |
| Permissions | `-rw-r--r--` propriétaire `hadoop`, groupe `supergroup` | `UC03_preuves/hdfs/depot_et_controles.txt`, capture explorer |
| Intégrité | SHA-256 identique source / HDFS, `fsck` : HEALTHY | `UC03_preuves/hdfs/depot_et_controles.txt` |

## UC-04 – NiFi

| Test | Résultat observé | Preuve |
|---|---|---|
| Lecture source | OK : GetFile a lu 1 fichier de 155 100 octets | `UC04_preuves/execution/execution_flux.txt` |
| Exécution du flux | OK : GetFile → UpdateAttribute → PutHDFS | `UC04_preuves/execution/execution_flux.txt`, `UC04_preuves/execution/statut_flux.json` |
| Dépôt HDFS par le flux | OK : fichier de 155 100 octets dans `/retail-lake/raw/nifi`, SHA-256 identique à la source | `UC04_preuves/execution/depot_nifi_hdfs.txt` |
| Erreur contrôlée | OK : GetFile INVALID (dossier inexistant) et doublon refusé par PutHDFS | `UC04_preuves/erreurs/test_erreur.txt`, `UC04_preuves/erreurs/test_conflit_doublon.txt` |
| Traçabilité | OK : 5 événements de provenance | `UC04_preuves/provenance/provenance_evenements.json` |

## Critères du socle

Rempli : opérations HDFS démontrées, arborescence cohérente, données réellement inspectées, fichier TPCx-BB déposé et vérifié, flux NiFi conçu et exécuté, erreurs et provenance documentées.
Réserve : le flux a été piloté par l'API (pas de captures de l'interface NiFi), et PutHDFS a nécessité l'ajout de NAR officiels absents de l'image.
