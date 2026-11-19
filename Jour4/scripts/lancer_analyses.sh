#!/bin/bash
# usage : bash scripts/lancer_analyses.sh
# meme analyse que le notebook, en script (conteneur j4-analytics, Parquet du Jour 3 montes en lecture seule)
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.." || exit 1
docker run --rm -v "$PWD:/work" -v "$PWD/../Jour3/data:/j3/data:ro" -w /work/scripts j4-analytics python analyses.py 2>&1 | grep -v "WARN\|^Setting default log\|To adjust logging" | tee preuves/uc08/resultats/analyses_script_log.txt
