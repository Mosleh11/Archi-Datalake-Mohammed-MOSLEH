#!/bin/bash
# usage : RAW_HOST=<dossier des .dat> bash lancer.sh <script.py> <journal>
# lance un script dans le conteneur j3-pyspark (voir docker/Dockerfile) et garde la sortie dans le journal
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.." || exit 1
docker run --rm -v "$PWD:/work" -v "${RAW_HOST:?dossier contenant customer/, date_dim/, ...}:/data/raw:ro" \
  -w /work/scripts j3-pyspark python "$1" 2>&1 | grep -v "WARN\|^Setting default log\|To adjust logging" | tee "$2"
