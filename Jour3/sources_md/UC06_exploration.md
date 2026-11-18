# UC-06 – Exploration des données avec PySpark

Notebook exécuté : `notebooks/exploration.ipynb` (version HTML lisible : `preuves/exploration/exploration.html`). Pour chaque source il affiche le schéma, 5 lignes, le nombre de lignes, les valeurs manquantes par colonne, les doublons sur la clé candidate et les min/max des colonnes numériques.

## Contrôles initiaux (résultats du notebook)

| Source | Lignes | Colonnes | Doublons sur la clé | Valeurs manquantes (colonnes concernées) |
|---|---|---|---|---|
| customer | 99 000 | 18 | 0 | 14 colonnes entre 16 et 30 valeurs (0,016 à 0,030 %) |
| customer_address | 49 500 | 13 | 0 | 5 colonnes entre 10 et 23 valeurs (0,020 à 0,046 %) |
| household_demographics | 7 200 | 5 | 0 | 7 valeurs au total (2 + 1 + 2 + 2 selon la colonne) |
| income_band | 20 | 3 | 0 | aucune |
| date_dim | 109 573 | 28 | 0 | aucune |
| inventory | 21 791 809 | 4 | 0 | `inv_quantity_on_hand` : 5 617 (0,026 %), dont celle de la ligne incomplète ; la ligne incomplète n'a ni entrepôt ni quantité |

## Constats

- Les valeurs manquantes sont rares et dispersées : elles ressemblent à du bruit injecté, pas à un défaut métier. Elles sont conservées à `null`, sans remplacement.
- `hd_vehicle_count` contient **-1** pour 282 foyers sur 7 200 (3,9 %) : valeur incohérente pour un nombre de véhicules.
- `inventory` : la dernière ligne du fichier est incomplète (`38584|1180`, deux champs sur quatre) et la dernière date n'a que 11 808 lignes au lieu de 90 000 : le fichier est coupé en cours d'écriture.
- `date_dim` est un calendrier complet de 1900 à 2199 (109 573 jours) ; `d_date_sk` commence à 0.
- Les répartitions (clients par tranche de revenu, stock moyen) sont presque uniformes : signe de données générées au hasard, à ne pas interpréter comme du comportement réel.
- Les colonnes `c_first_name`, `c_last_name`, `c_login`, `c_email_address` ressemblent à des données personnelles (même si le jeu est synthétique) : traitées dans les règles de nettoyage.

Valeurs atypiques : rien d'autre que ce qui précède dans les min/max (par exemple `c_birth_year` de 1924 à 1992, `inv_quantity_on_hand` de 0 à 1000, `hd_dep_count` de 0 à 9).
