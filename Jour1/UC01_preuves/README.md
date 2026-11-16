# Preuves UC-01

Chaque preuve est une sortie réelle des scripts lancés sur les fichiers reçus (zip tronqué : 7 tables).

| # | Preuve | Ce qu'elle démontre |
|---|---|---|
| P1 | `arborescence.txt` | Contenu du zip après récupération : 7 dossiers de tables, tailles en octets. Montre que le zip est tronqué. |
| P2 | `recuperation_zip.py` | Script qui lit les en-têtes locaux du zip pour récupérer les fichiers lisibles. Il explique pourquoi `unzip` échoue. |
| P3 | `apercu_fichiers.txt` | 3 premières lignes de chaque fichier : format texte, séparateur `\|`, pas d'en-tête. |
| P4 | `schema_spec_tpcxbb.json` | Noms et types des colonnes pris dans le DDL de la spec TPCx-BB v1.7.0 (sources consultées). |
| P5 | `analyse_kit.py` + `resultats_analyse.json` | Script et résultats de l'exploration : lignes, colonnes, valeurs vides, min/max, unicité des clés, jointures, doublons. |
| P6 | `inventaire_sources.xlsx` | Inventaire (feuilles Fichiers, Colonnes, Relations, Absents du zip) généré depuis P5. Justifie les relations entre tables. |
| P7 | `controles_simples.py` + `controles_simples.txt` | Contrôles de cohérence (fins de ligne, clients par état, tranches de revenu) qui appuient KPI-09 et KPI-10. |
| P8 | `dictionnaire_KPI.xlsx` | Les 10 KPI avec formule, colonnes utilisées et colonne « calculable avec le zip reçu ? ». |

L'image `Tables Principales.png` donnée par le formateur confirme les tables et clés attendues. Elle n'est pas dans le dépôt.
