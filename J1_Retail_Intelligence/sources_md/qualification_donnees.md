# UC-01 – Qualification des données et des relations

Tout ce qui est ci-dessous a été mesuré avec `preuves/analyse_kit.py` sur les fichiers réellement reçus (résultats dans `preuves/resultats_analyse.json`). Les statuts suivent ceux du TP.

## 1. Inventaire des fichiers

| Table | Domaine | Lignes | Colonnes | Taille (octets) | État |
|---|---|---|---|---|---|
| customer | Clients | 99 000 | 18 | 13 279 063 | Complet |
| customer_address | Adresses | 49 500 | 13 | 5 387 229 | Complet |
| customer_demographics | Démographie | 1 920 800 | 9 | 77 753 083 | Complet |
| date_dim | Dates | 109 573 | 28 | 15 395 800 | Complet |
| household_demographics | Foyers | 7 200 | 5 | 155 100 | Complet |
| income_band | Tranches de revenu | 20 | 3 | 327 | Complet |
| inventory | Stocks | 21 791 808 | 4 | 398 201 945 | **Tronqué** |

Format commun : texte, séparateur `|`, pas d'en-tête, fin de ligne CRLF. Le détail des colonnes (nom, type, vides, min, max) est dans `inventaire_sources.xlsx`, feuille « Colonnes ».

**Noms de colonnes** : pris dans le DDL de la spec TPCx-BB 1.7.0, dans l'ordre. Le nombre de champs par ligne est identique à celui du DDL pour toutes les lignes complètes des 7 tables (**Déduit**). Les types sont ceux de la spec ; aucune valeur non numérique n'a été trouvée dans les colonnes déclarées bigint/int (**Vérifié**).

**Tables absentes** : `item`, `store`, `store_sales`, `web_sales`, `store_returns`, `web_returns`, `warehouse`, `promotion`, `time_dim`, `web_clickstreams`, `web_page`, `web_site`, `ship_mode`, `reason`, `item_marketprices`, `product_reviews`. Elles sont citées dans la spec et dans le projet fil rouge mais pas dans le zip (**Non disponible**).

## 2. Clés

| Table | Clé | Valeurs | Distinctes | Vides | Statut |
|---|---|---|---|---|---|
| customer | c_customer_sk (0 à 98 999) | 99 000 | 99 000 | 0 | Vérifié |
| customer | c_customer_id (texte) | 99 000 | 99 000 | 0 | Vérifié |
| customer_address | ca_address_sk (0 à 49 499) | 49 500 | 49 500 | 0 | Vérifié |
| customer_demographics | cd_demo_sk (0 à 1 920 799) | 1 920 800 | 1 920 800 | 0 | Vérifié |
| date_dim | d_date_sk (0 à 109 572) | 109 573 | 109 573 | 0 | Vérifié |
| household_demographics | hd_demo_sk (0 à 7 199) | 7 200 | 7 200 | 0 | Vérifié |
| income_band | ib_income_band_sk (0 à 19) | 20 | 20 | 0 | Vérifié |
| inventory | (inv_date_sk, inv_item_sk, inv_warehouse_sk) | 21 791 808 | 21 791 808 | 0 | Vérifié : 0 doublon sur le triplet |

## 3. Valeurs vides

On a considéré qu'une valeur vide entre deux `|` correspond à un NULL. Les clés primaires n'ont aucun vide. Les autres colonnes ont un taux très faible et régulier :

| Table | Vides par colonne (hors clé) | Taux |
|---|---|---|
| customer | entre 16 et 30 sur 99 000 | 0,02 à 0,03 % |
| customer_address | entre 10 et 23 sur 49 500 (colonnes texte) | 0,02 à 0,05 % |
| customer_demographics | entre 485 et 544 sur 1 920 800 | ≈ 0,026 % |
| household_demographics | 1 ou 2 sur 7 200 | ≈ 0,02 % |
| inventory | 5 616 vides sur `inv_quantity_on_hand` | ≈ 0,026 % |
| date_dim, income_band | aucun | 0 % |

Ce taux est proche du paramètre NULL_CHANCE de la spec (0,00025). Je le **déduis** : des NULL sont injectés au hasard par le générateur, ce ne sont pas des erreurs métier. Il faudra quand même les traiter en Silver.

## 4. Anomalies et points étonnants

| # | Observation | Statut |
|---|---|---|
| A1 | Le zip est tronqué : pas de fin d'archive, 7 tables récupérées sur plus de 20. | Vérifié |
| A2 | `inventory.dat` est coupé en pleine ligne (dernière ligne `38584\|1180` avec 2 champs au lieu de 4). Le dernier jour (`inv_date_sk` 38 584, soit le 2005-08-22) n'a que 11 808 lignes alors que les autres en ont 90 000 (18 000 articles × 5 entrepôts). Il y a donc des dates en moins après cette coupure, mais on ne sait pas combien. | Vérifié (coupure) / Hypothèse (ce qui manque) |
| A3 | `hd_vehicle_count` contient -1 pour 282 foyers sur 7 200 (3,9 %). La spec ne dit pas ce que -1 veut dire. | Vérifié / À valider (sens) |
| A4 | `date_dim` a 109 573 lignes (1900-01-01 à 2199-12-31). La spec écrit « 73049 (fixed) » pour cette table, mais ses propres bornes (1900 à 2200) donnent 109 573 jours. Les bornes de la spec sont donc cohérentes avec le fichier, la valeur 73 049 non. | Déduit |
| A5 | `d_date_sk` commence à 0 alors que la spec écrit « Key starting at 1 » (elle prévoit aussi un décalage SK_ID_OFFSET). Pas gênant si on garde le même décalage partout. | Vérifié |
| A6 | `customer_demographics` contient 1 920 800 lignes, soit 19 fois plus que `customer` (99 000). Ce n'est pas une table de personnes mais plutôt un catalogue de profils possibles. | Déduit (à confirmer) |
| A7 | `customer` contient nom, prénom, email, login : des données de type personnel, même synthétiques. | Vérifié |
| A8 | Les colonnes de répartition sont presque uniformes (stock moyen ≈ 500 pour chaque entrepôt, ≈ 5 000 clients par tranche de revenu, hommes/femmes ≈ 50/50). C'est typique d'un générateur aléatoire. | Vérifié (chiffres) / Déduit (cause) |
| A9 | `c_last_review_date` est typée texte (CHAR 10) dans la spec : la date n'est pas un vrai type date. | Vérifié (spec) |

## 5. Relations entre les tables

Pour chaque relation on a vérifié : la colonne existe des deux côtés, les types sont compatibles (entiers), la clé cible est unique, on a compté les vides et les valeurs sans correspondance (`preuves/resultats_analyse.json`, rubrique jointures).

| Relation | Lignes | Vides | Sans correspondance | Statut |
|---|---|---|---|---|
| customer.c_current_cdemo_sk → customer_demographics.cd_demo_sk | 99 000 | 18 | 0 | Vérifié |
| customer.c_current_hdemo_sk → household_demographics.hd_demo_sk | 99 000 | 29 | 0 | Vérifié |
| customer.c_current_addr_sk → customer_address.ca_address_sk | 99 000 | 22 | 0 | Vérifié |
| customer.c_first_shipto_date_sk → date_dim.d_date_sk | 99 000 | 25 | 0 | Vérifié |
| customer.c_first_sales_date_sk → date_dim.d_date_sk | 99 000 | 18 | 0 | Vérifié |
| household_demographics.hd_income_band_sk → income_band.ib_income_band_sk | 7 200 | 2 | 0 | Vérifié |
| inventory.inv_date_sk → date_dim.d_date_sk (243 dates distinctes, du 2001-01-01 au 2005-08-22) | 21 791 808 | 0 | 0 | Vérifié |
| inventory.inv_item_sk → item.i_item_sk (valeurs de 0 à 17 999) | – | – | non testable | À valider : `item` absent |
| inventory.inv_warehouse_sk → warehouse.w_warehouse_sk (valeurs de 0 à 4) | – | – | non testable | À valider : `warehouse` absent |
| ventes / retours → item, store, client, date | – | – | non testable | À valider : tables absentes ; relations décrites dans la spec seulement (Hypothèse) |

Cardinalités constatées : un client a 0 ou 1 adresse, 0 ou 1 profil démographique et 0 ou 1 foyer. Un foyer a 0 ou 1 tranche de revenu.

Remarque sur les 243 dates : 242 jours complets (242 × 90 000 = 21 780 000) + 11 808 lignes du dernier jour = 21 791 808, ce qui est exactement le nombre de lignes lues (**Déduit**, très cohérent).

## 6. Contrôles simples réalisés

(`preuves/controles_simples.txt`)

- 22 clients sans adresse ; les 5 premiers états : TX 8 189, GA 5 081, VA 4 394, KY 3 848, KS 3 379.
- Genre : M 961 096, F 959 218, vide 486.
- `hd_vehicle_count` : 2 → 2 514 foyers, 3 → 1 596, 1 → 1 243, 0 → 1 183, 4 → 380, **-1 → 282**, vide → 2.
- Stock moyen par entrepôt : 500,3 / 500,2 / 500,1 / 499,9 / 500,3.

## 7. Granularité (ce que représente une ligne)

| Table | Une ligne = |
|---|---|
| customer | un client |
| customer_address | une adresse |
| customer_demographics | un profil démographique |
| household_demographics | un type de foyer |
| date_dim | un jour |
| inventory | la quantité en stock d'un article dans un entrepôt pour une date (hebdomadaire) |

## 7 bis. Classification des données

Toutes les données reçues sont **structurées** : ce sont des fichiers texte qui exportent des tables relationnelles avec des colonnes définies. Le format `.dat` n'en fait pas du semi-structuré (le TP le précise pour les CSV). Les avis produits (`product_reviews`, texte libre) seraient non structurés, mais ils sont absents du zip.

## 8. Qualité – synthèse

| Dimension | Constat |
|---|---|
| Complétude | tables de ventes, retours, produits, magasins absentes ; `inventory` tronqué |
| Validité | types corrects ; une valeur négative inexpliquée (-1) |
| Cohérence | relations vérifiées OK ; formule de taille de `date_dim` incohérente avec la spec |
| Unicité | clés uniques |
| Intégrité | 0 clé étrangère orpheline sur les relations testables |
| Fraîcheur | sans objet (données synthétiques de 2001 à 2005 pour le stock) |
