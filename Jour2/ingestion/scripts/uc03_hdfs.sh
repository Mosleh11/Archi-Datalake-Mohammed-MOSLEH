#!/bin/bash
# UC-03 : verification de Hadoop, arborescence du Data Lake, depot manuel et controles
cd "$(dirname "$0")" && . ./lib.sh
U=../../UC03_preuves
NN=j2-namenode

H=$U/environnement/environnement.txt; : > $H
run $H $NN "cat /etc/os-release | head -2; uname -r; java -version; python3 --version"
run $H $NN "hadoop version"
run $H $NN "echo HADOOP_HOME=\$HADOOP_HOME; echo HADOOP_CONF_DIR=\$HADOOP_CONF_DIR; whoami"
run $H $NN "jps"
run $H $NN "cat \$HADOOP_CONF_DIR/core-site.xml \$HADOOP_CONF_DIR/hdfs-site.xml"
run $H j2-datanode "jps"
run $H $NN "hdfs dfsadmin -report | head -n 25"

C=$U/hdfs/commandes_hdfs.txt; : > $C
run $C $NN "hdfs dfs -ls /"
for d in raw/tpcxbb/initial raw/tpcxbb/refresh raw/nifi bronze/tpcxbb silver gold quality logs; do
  run $C $NN "hdfs dfs -mkdir -p /retail-lake/$d"
done
run $C $NN "hdfs dfs -ls -R /retail-lake"
run $C $NN "hdfs dfs -du -h /retail-lake"
run $C $NN "hdfs dfs -ls -d /retail-lake /retail-lake/raw"

# etape 4 : inspection avant depot (sources dans le conteneur : /data/tpcxbb, copie du kit local)
D=$U/hdfs/depot_et_controles.txt; : > $D
for f in household_demographics date_dim; do
  run $D $NN "ls -l /data/tpcxbb/$f.dat; wc -l < /data/tpcxbb/$f.dat; head -n 2 /data/tpcxbb/$f.dat; awk -F'|' 'NR==1{print NF\" colonnes\"}' /data/tpcxbb/$f.dat; sha256sum /data/tpcxbb/$f.dat"
  run $D $NN "hdfs dfs -put -f /data/tpcxbb/$f.dat /retail-lake/raw/tpcxbb/initial/"
done

# etape 5 : verification du stockage
run $D $NN "hdfs dfs -ls -h /retail-lake/raw/tpcxbb/initial"
run $D $NN "hdfs dfs -du -h /retail-lake/raw/tpcxbb/initial"
run $D $NN "hdfs dfs -stat '%n %b octets, replication %r, bloc %o, modifie %y' /retail-lake/raw/tpcxbb/initial/*"
run $D $NN "hdfs dfs -cat /retail-lake/raw/tpcxbb/initial/household_demographics.dat | head -n 3"
run $D $NN "hdfs fsck /retail-lake/raw/tpcxbb/initial -files -blocks -locations"
for f in household_demographics date_dim; do
  run $D $NN "rm -f /tmp/$f.verif; hdfs dfs -get /retail-lake/raw/tpcxbb/initial/$f.dat /tmp/$f.verif && sha256sum /tmp/$f.verif /data/tpcxbb/$f.dat && cmp /tmp/$f.verif /data/tpcxbb/$f.dat && echo IDENTIQUE"
done
run $D $NN "ls -l /data/tpcxbb"
