# Preuves UC-08

Sorties de l'exécution réelle du 19/11/2026.

| Fichier / dossier | Ce qu'il démontre |
|---|---|
| `environnement/versions.txt` | Python 3.12.14, PySpark 4.3.0, pandas 2.3.3, Matplotlib 3.11.2, Java 21.0.13 (conteneur `j4-analytics`) |
| `notebook/analyses_kpi.html` | Notebook exécuté (version lisible) : schémas, contrôles de cohérence, KPI, statistiques, graphiques |
| `resultats/inventaire_jeux.csv` | Jeux Silver et Gold utilisés : zone, format, granularité, lignes, colonnes |
| `resultats/kpi.csv` | Valeurs des KPI-08, KPI-09 et KPI-10 |
| `resultats/statistiques.csv`, `repartitions.csv` | Statistiques descriptives et répartitions par catégorie |
| `resultats/clients_par_etat.csv`, `clients_par_tranche_revenu.csv`, `stock_moyen_mensuel.csv`, `distribution_annee_naissance.csv` | Tableaux agrégés derrière les quatre graphiques |
| `resultats/analyses_script_log.txt` | Sortie de `scripts/analyses.py` (même analyse que le notebook) |

Graphiques : `../../visualisations/`. Synthèse des constats, interprétations et limites : `UC08_analyses_visualisations.pdf`. Reproduction : `../../README.md`.
