# J4-03 – Statistiques descriptives

Calculées avec Spark (`preuves/uc08/resultats/statistiques.csv`, `preuves/uc08/resultats/repartitions.csv`). Médiane approchée avec `percentile_approx`.

{{TABLE_STATS}}

Lecture :

- `inv_quantity_on_hand` : 21 774 389 valeurs, de 0 à 1 000, moyenne 500,16, médiane 500, écart-type 288,97. Pour une loi uniforme sur [0 ; 1 000], l'écart-type théorique est 1 000 / √12 ≈ 288,7 : la quantité en stock se comporte comme un tirage aléatoire uniforme, ce qui est attendu d'un jeu synthétique.
- `c_birth_year` : de 1924 à 1992, moyenne 1958,05 ; 30 valeurs manquantes.
- `hd_vehicle_count` : 4 003 manquantes, dont 282 valeurs -1 de la source mises à `null` au Jour 3 (une valeur négative n'a pas de sens) ; `hd_dep_count` : de 0 à 9, médiane 1 mais moyenne 2,43 (distribution étalée vers les grandes valeurs).

Répartitions des variables qualitatives (clients, 99 000 lignes) :

{{TABLE_REPARTITIONS}}

Évolution temporelle : le calendrier de `date_dim` existe, mais la seule date exploitable pour une évolution est la date de stock (jan. 2001 – août 2005, 56 mois). La date de première vente des clients (`c_first_sales_date_sk`) s'étale sur les années 1900 et suivantes, ce qui n'a pas de sens métier : elle n'est pas utilisée comme axe temporel.
