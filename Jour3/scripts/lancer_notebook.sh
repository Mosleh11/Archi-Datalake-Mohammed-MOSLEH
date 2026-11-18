#!/bin/bash
# genere puis execute le notebook d'exploration dans le conteneur ; ecrit aussi une version HTML dans preuves/exploration/
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.." || exit 1
docker run --rm -v "$PWD:/work" -v "${RAW_HOST:?dossier des .dat}:/data/raw:ro" -w /work j3-pyspark bash -c "
  python outils/creer_notebook.py &&
  jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 notebooks/exploration.ipynb &&
  jupyter nbconvert --to html notebooks/exploration.ipynb --output-dir preuves/exploration --output exploration.html" 2>&1 | tail -n 5
