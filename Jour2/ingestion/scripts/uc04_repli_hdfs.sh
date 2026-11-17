#!/bin/bash
# SOLUTION DE REPLI : PutHDFS n'est pas disponible dans NiFi 2.12.0 (image officielle).
# Le fichier traite par NiFi (archive) est envoye dans HDFS /retail-lake/raw/nifi avec hdfs dfs -put, sans ecrasement.
cd "$(dirname "$0")" && . ./lib.sh
L=../../UC04_preuves/erreurs/essai_sans_puthdfs/repli_hdfs.txt; : > $L
F=household_demographics.dat
run $L j2-nifi "ls -l /data/nifi/archive/$F; sha256sum /data/nifi/archive/$F"
{ echo "[$(date '+%F %T')] pipe : conteneur nifi -> hdfs dfs -put (sans -f)"; docker exec j2-nifi cat /data/nifi/archive/$F | docker exec -i j2-namenode hdfs dfs -put - /retail-lake/raw/nifi/$F 2>&1; echo "-> code retour $?"; echo; } | tee -a $L
run $L j2-namenode "hdfs dfs -ls -h /retail-lake/raw/nifi; hdfs dfs -du -h /retail-lake/raw/nifi"
run $L j2-namenode "hdfs dfs -cat /retail-lake/raw/nifi/$F | sha256sum"
# relance : doit echouer, le fichier existe deja (pas de doublon)
{ echo "[$(date '+%F %T')] relance sans controle : doit echouer"; docker exec j2-nifi cat /data/nifi/archive/$F | docker exec -i j2-namenode hdfs dfs -put - /retail-lake/raw/nifi/$F 2>&1; echo "-> code retour $?"; echo; } | tee -a $L
