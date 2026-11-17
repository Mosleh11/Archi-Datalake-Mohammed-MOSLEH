# Preuves UC-04

Les captures d'écran viennent de l'interface NiFi réelle (prises avec un navigateur piloté par script). Le flux a été créé et lancé par l'API REST de NiFi ; l'identifiant de connexion n'est pas dans le dépôt.

## configuration/
| Preuve | Ce qu'elle démontre |
|---|---|
| `schema_flux_nifi.png` | Schéma du flux GetFile → UpdateAttribute → PutHDFS, avec la relation `failure` vers LogAttribute |
| `getfile_proprietes.png` | Propriétés de GetFile : dossier source, `Keep Source File` = false |
| `puthdfs_proprietes.png` | Propriétés de PutHDFS : configuration Hadoop, destination `/retail-lake/raw/nifi`, stratégie `fail` |
| `flux_j2.json` | Export du flux (définition des 4 processeurs et des 3 connexions) |
| `nifi_about.json` | Version de NiFi : 2.12.0 |
| `processeurs_hdfs_disponibles.txt` | PutHDFS et les autres processeurs HDFS, disponibles après l'ajout des NAR Apache |

## execution/
| Preuve | Ce qu'elle démontre |
|---|---|
| `canvas_flux_compteurs.png` | Le flux dans NiFi : compteurs 5 min, files d'attente (1 FlowFile dans la file `failure`) |
| `execution_flux.txt`, `statut_flux.json` | Compteurs des processeurs et événements de provenance du 1er run (`household_demographics.dat`) |
| `run2_income_band_execution.txt`, `run2_income_band_statut.json` | 2e run (`income_band.dat`, 327 octets) fait pour les captures |
| `depot_nifi_hdfs.txt` | Le fichier déposé par PutHDFS est dans HDFS : taille, `fsck`, SHA-256 identique à la source |
| `ids.json` | Identifiants internes des composants (utilisés par les scripts) |

## erreurs/
| Preuve | Ce qu'elle démontre |
|---|---|
| `test_erreur.txt` | GetFile INVALID avec un dossier inexistant, puis retour à l'état VALID |
| `test_conflit_doublon.txt` | PutHDFS refuse un fichier de même nom (message du journal NiFi), 1 FlowFile en file `failure` |
| `essai_sans_puthdfs/` | Essai préalable (PutFile et dépôt HDFS par script) avant l'ajout des NAR ; plus le flux retenu |

## provenance/
| Preuve | Ce qu'elle démontre |
|---|---|
| `provenance_liste.png` | Événements de provenance de PutHDFS dans l'interface NiFi |
| `provenance_evenement_SEND.png` | Détail de l'événement SEND : FlowFile, taille, composant, durée |
| `provenance_evenements.json`, `provenance_evenements_apres_run2.json` | Événements bruts de l'API NiFi |
