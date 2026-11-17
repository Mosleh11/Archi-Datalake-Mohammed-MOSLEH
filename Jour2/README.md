# TP Jour 2 – Hadoop, HDFS et ingestion (UC-03, UC-04)

Mastère Développement, Data & IA – IPSSI – Mohammed Mosleh. Date des manipulations : 17/11/2026.

## Ce qui a été réellement exécuté

| Élément | État |
|---|---|
| HDFS (Hadoop 3.5.0, 1 NameNode + 1 DataNode) | **Exécuté** : arborescence, dépôts, contrôles, fsck |
| NiFi 2.12.0, flux GetFile → UpdateAttribute → **PutHDFS** | **Exécuté** : fichier déposé dans HDFS par NiFi, provenance, deux erreurs contrôlées |
| PutHDFS | Absent de l'image officielle : ajout des 2 NAR Apache `nifi-hadoop-nar` et `nifi-hadoop-libraries-nar` 2.12.0 (SHA-1 vérifié) |
| Complémentaire | Faits : CO-01 à CO-05. Avancé : non fait |

L'environnement tourne dans **Docker Desktop** (mono-nœud) et pas sur une Ubuntu installée à la main. Détails dans la fiche d'environnement (`UC03_Hadoop_HDFS.pdf`). Les captures de NiFi ont été prises avec un navigateur piloté par script (Selenium).

## Contenu

```
Jour2/
|-- README.md, README_Jour2.pdf
|-- UC03_Hadoop_HDFS.pdf
|-- UC03_preuves/        environnement/, hdfs/, data_lake/ (+ README.md)
|-- UC04_ingestion_NiFi.pdf
|-- UC04_preuves/        configuration/, execution/, erreurs/, provenance/ (+ README.md)
|-- Complementaire/      CO-01 blocs et réplication, CO-02 convention, CO-03 intégrité, CO-04 supervision, CO-05 reprise
|-- ingestion/           docker/ (compose, config Hadoop et NiFi sans mot de passe), scripts/
|-- sources_md/          textes d'origine des PDF (Markdown)
|-- outils/              build_pdf.py, schémas Graphviz (.dot)
```

Les questions de recul sont dans `UC04_ingestion_NiFi.pdf` (dernière partie). Pas de dossier `Avance/` : défi avancé non réalisé.

## Reproduire

```
cd ingestion/docker
copy nifi.env.exemple nifi.env        # puis choisir un mot de passe (12 caractères min)
docker compose up -d                  # démarre HDFS puis NiFi (https://localhost:8443/nifi, HDFS : http://localhost:9870)
```

Les fichiers de données ne sont pas dans le dépôt. Ils viennent du zip du formateur (7 tables récupérables, voir Jour 1). Il faut les copier dans le conteneur :

```
docker exec -u root j2-namenode bash -c "mkdir -p /data/tpcxbb && chown hadoop /data/tpcxbb"
docker cp household_demographics.dat j2-namenode:/data/tpcxbb/
docker cp date_dim.dat j2-namenode:/data/tpcxbb/
docker exec -u root j2-nifi bash -c "mkdir -p /data/nifi/input /data/nifi/archive /data/nifi/error && chown -R nifi /data/nifi"
docker cp household_demographics.dat j2-nifi:/data/nifi/input/
```

Puis, depuis `ingestion/scripts/` : `bash uc03_hdfs.sh`, `bash uc04_installer_nar.sh`, `python uc04_nifi.py ../../UC04_preuves/execution`, `python uc04_run.py ../../UC04_preuves/execution`, `python uc04_erreur.py ../../UC04_preuves/execution`, `python uc04_conflit.py`.
Pour rejouer le dépôt NiFi, vider `/retail-lake/raw/nifi` (`hdfs dfs -rm`) : la stratégie `fail` refuse sinon le doublon.

Arrêt : arrêter les processeurs NiFi, puis `docker compose down` (les données HDFS ne sont pas conservées : pas de volume).

## Chemins HDFS

`/retail-lake/{raw/tpcxbb/initial, raw/tpcxbb/refresh, raw/nifi, bronze/tpcxbb, silver, gold, quality, logs}`
Paramètres NiFi non sensibles : GetFile `/data/nifi/input` (Keep Source File = false), PutHDFS `/retail-lake/raw/nifi` (conflit = fail, config Hadoop dans `/opt/hadoop-conf`), UpdateAttribute `source=tpcxbb, zone=raw, ingere_par=nifi_j2`.
