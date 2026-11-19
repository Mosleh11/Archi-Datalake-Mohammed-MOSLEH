# J4-01 – Inventaire des jeux de données utilisés

{{TABLE_INVENTAIRE}}

Provenance : sources `customer`, `customer_address`, `household_demographics`, `income_band`, `date_dim`, `inventory` du kit TPCx-BB, nettoyées et jointes au Jour 3 (UC-06). Les colonnes sont celles de la spec TPCx-BB v1.7.0 plus les colonnes de traçabilité `_source` et `_traite_le`.

| Jeu | Contrôles qualité du Jour 3 (49 contrôles : 46 OK, 1 anomalie, 2 non vérifiables) | Pourquoi il convient à l'analyse |
|---|---|---|
| `silver/clients_enrichis` | clé `c_customer_sk` unique, jointures sans doublon, 22 clients sans adresse et 29 sans foyer (constatés au Jour 1) | un client par ligne : permet de compter des clients sans double compte |
| `silver/inventory` | **anomalie connue** : la dernière date est incomplète (11 808 lignes sur 90 000), le fichier source est tronqué ; 5 611 quantités manquantes sur les dates complètes | seule table de mesure quantitative disponible ; on n'utilise que les dates complètes (21 774 389 valeurs de quantité) |
| `silver/date_dim` | 109 573 jours (1900 à 2199), clé unique | donne l'année et le mois des dates de stock |
| `gold/clients_par_etat`, `gold/clients_par_tranche_revenu` | somme des clients = 99 000 (total du Silver) | agrégats prêts à tracer, petite taille (52 et 21 lignes) |
| `gold/stock_moyen_entrepot_mois` | stock moyen dans [0, 1000], lignes du Gold = lignes des dates complètes (21 780 000) | 280 lignes (5 entrepôts × 56 mois), une par entrepôt et par mois |

**Vérifications faites dans le notebook avant tout calcul** : un client par ligne (`c_customer_sk` unique), un état par ligne dans `clients_par_etat`, un entrepôt et un mois par ligne dans `stock_moyen_entrepot_mois`, somme des clients du Gold = nombre de clients du Silver (99 000) pour les deux jeux clients. Les cinq contrôles sont passés (le notebook s'arrête sinon).

**Jeu Gold de ventes absent.** Il manque pour le construire : `store_sales` / `web_sales` (montants, quantités, tickets), `item` (produits), `store` (magasins). Sans ces tables, aucun Gold de ventes n'est possible ; les trois Gold du Jour 3 sont utilisés.

# J4-02 – Dictionnaire des KPI (mis à jour)

Repris du dictionnaire du Jour 1 (`Jour1/UC01_preuves/dictionnaire_KPI.xlsx`). Les valeurs calculées sont dans `preuves/uc08/resultats/kpi.csv`.

| KPI | Définition métier | Formule | Champs | Filtres | Granularité | Unité | Limites d'interprétation | Calculé ? |
|---|---|---|---|---|---|---|---|---|
| KPI-09 Nombre de clients | Nombre de clients référencés | `COUNT(DISTINCT c_customer_sk)` ; par état : comptage groupé par `ca_state` | `c_customer_sk`, `ca_state` | aucun ; clients sans adresse regroupés dans « Non renseigné » | global et par état | clients | ne dit rien sur les clients actifs (aucune vente) ; adresse courante seulement | **oui** : 99 000 (dont 22 sans adresse) |
| KPI-10 Clients par tranche de revenu | Nombre de clients par tranche de revenu du foyer | comptage groupé par tranche (`income_band` via `household_demographics`) | `c_current_hdemo_sk`, `hd_income_band_sk`, `tranche` | 60 clients sans tranche exclus du graphique | 20 tranches de 10 000 | clients | unité monétaire non précisée par la spec ; revenu du foyer, pas du client | **oui** |
| KPI-08 Stock moyen | Quantité moyenne en stock | `AVG(inv_quantity_on_hand)` | `inv_quantity_on_hand`, `inv_warehouse_sk`, `inv_date_sk` | dates complètes uniquement ; quantités manquantes ignorées par la moyenne | entrepôt × mois (Gold) ; global (Silver) | unités | pas de stock par magasin ; pas de libellé d'article ni d'entrepôt (`item`, `warehouse` absents) ; dernière date exclue | **oui** : 500,16 |
| KPI-01 Chiffre d'affaires | Montant des ventes de la période | `SUM(ss_ext_sales_price)` | tables de ventes | — | — | — | — | **non** : tables absentes |
| KPI-02 Transactions | Tickets / commandes distincts | `COUNT(DISTINCT ss_ticket_number)` | tables de ventes | — | — | — | un ticket n'est ni une ligne ni un article | **non** : tables absentes |
| KPI-03 Panier moyen | Montant moyen par transaction | KPI-01 / KPI-02 | — | — | — | — | faux sans le même périmètre pour les deux | **non** |
| KPI-04 Quantités vendues | Unités vendues | `SUM(ss_quantity)` | tables de ventes | — | — | — | — | **non** |
| KPI-05 Évolution des ventes | Variation du CA entre deux périodes | (CA N − CA N-1) / CA N-1 | ventes + `date_dim` | — | — | — | — | **non** (seul l'axe temps existe) |
| KPI-06 Taux de remise | Remise / prix de liste | `SUM(ss_ext_discount_amt) / SUM(ss_ext_list_price)` | tables de ventes | — | — | — | base de calcul à confirmer | **non** |
| KPI-07 Taux de retour | Quantités retournées / vendues | `SUM(sr_return_quantity) / SUM(ss_quantity)` | ventes + retours | — | — | — | numérateur et dénominateur à préciser | **non** |

Aucune marge n'est calculée (pas de coûts). Aucun panier moyen n'est calculé (pas de transactions).

{{TABLE_KPI}}
