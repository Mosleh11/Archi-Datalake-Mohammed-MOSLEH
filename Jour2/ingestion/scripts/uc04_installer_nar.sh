#!/bin/bash
# PutHDFS n'est pas dans l'image apache/nifi:2.12.0 : ajout des 2 NAR officiels Apache (Maven Central), empreinte SHA-1 verifiee
export MSYS_NO_PATHCONV=1
V=2.12.0; M=https://repo1.maven.org/maven2/org/apache/nifi
mkdir -p nars && cd nars
for a in nifi-hadoop-libraries-nar nifi-hadoop-nar; do
  curl -sfLO $M/$a/$V/$a-$V.nar
  echo "$(curl -sfL $M/$a/$V/$a-$V.nar.sha1) *$a-$V.nar" | sha1sum -c - || exit 1
  docker cp $a-$V.nar j2-nifi:/opt/nifi/nifi-current/nar_extensions/
done
docker exec -u root j2-nifi bash -c "chown nifi /opt/nifi/nifi-current/nar_extensions/*.nar"
# NiFi charge les NAR tout seul (nifi.nar.library.autoload.directory) : PutHDFS apparait apres quelques secondes
