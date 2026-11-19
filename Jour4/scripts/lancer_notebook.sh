#!/bin/bash
# usage : bash scripts/lancer_notebook.sh
# execute notebooks/analyses_kpi.ipynb dans le conteneur j4-analytics (docker/Dockerfile)
# lit les Parquet Silver/Gold du Jour 3 (../Jour3/data, montes en lecture seule dans /j3/data)
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.." || exit 1
docker run --rm -v "$PWD:/work" -v "$PWD/../Jour3/data:/j3/data:ro" -w /work/notebooks j4-analytics \
  jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 analyses_kpi.ipynb 2>&1 | grep -v "WARN"
