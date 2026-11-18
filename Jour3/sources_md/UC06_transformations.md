# UC-06 – Transformations, Silver et Gold

Script : `scripts/transformations.py` (log : `preuves/transformations/transformations_log.txt`). Les jeux Silver nettoyés sont lus, joints, puis agrégés en Gold. Parquet est le format de sortie de toutes les zones.

## Jointures vérifiées

Les relations viennent du DDL de la spec (colonnes `*_sk`) et ont été vérifiées au Jour 1 (0 orphelin). Avant chaque jointure, le script vérifie que **la clé de droite est unique** (sinon il s'arrête : la jointure dupliquerait des lignes), puis compte les lignes avant et après et les clés non rapprochées. Toutes sont des jointures gauches, de cardinalité N:1.

{{TABLE_JOINTURES}}

Colonnes `null` à gauche : clients sans adresse, sans foyer ou sans tranche de revenu (clé absente à la source). On ne joint ni les ventes, ni les avis, ni la navigation web (absents du zip), ni `inventory` à `item` ou `warehouse` (absents).

## Jeux Silver produits (`data/silver/`)

| Jeu | Contenu | Lignes | Clé | Schéma |
|---|---|---|---|---|
| `customer` | clients nettoyés, sans données personnelles | 99 000 | `c_customer_sk` | `preuves/silver_gold/zones_silver_gold.txt` |
| `customer_address` | adresses nettoyées | 49 500 | `ca_address_sk` | idem |
| `household_demographics` | foyers, `hd_vehicle_count` corrigé + indicateur | 7 200 | `hd_demo_sk` | idem |
| `income_band` | tranches de revenu + libellé `tranche` | 20 | `ib_income_band_sk` | idem |
| `date_dim` | calendrier, `d_date` en date | 109 573 | `d_date_sk` | idem |
| `inventory` | stocks hebdomadaires + `date_complete` (non versionné : 111 Mo, régénérable) | 21 791 808 | triplet | idem |
| `clients_enrichis` | clients + adresse + foyer + tranche (une ligne par client) | 99 000 | `c_customer_sk` | idem |
| `_rejets/inventory` | ligne incomplète écartée | 1 | | motif dans la colonne `motif` |

## Jeux Gold produits (`data/gold/`)

Les questions viennent du Jour 1 (`dictionnaire_KPI.xlsx`). Les KPI de ventes ne sont pas calculables (tables absentes) : les trois Gold répondent aux KPI qui le sont.

| Gold | Question métier (KPI) | Sources | Granularité | Mesures et règles de calcul | Limites d'interprétation |
|---|---|---|---|---|---|
| `clients_par_etat` | Où sont les clients ? (KPI-09) | `clients_enrichis` | 1 ligne par état | `nb_clients` = nombre de clients ; `part_pct` = `nb_clients` / total × 100. Les clients sans adresse sont comptés dans « Non renseigne » | Clients **référencés**, pas actifs (aucune vente disponible) |
| `clients_par_tranche_revenu` | Quel est le profil de revenu des clients ? (KPI-10) | `clients_enrichis` | 1 ligne par tranche de revenu du foyer | `nb_clients`, `part_pct` ; sans tranche → « Non renseigne » | Répartition quasi uniforme (~5 % par tranche) : données synthétiques |
| `stock_moyen_entrepot_mois` | Quel est le niveau de stock par entrepôt ? (KPI-08) | `inventory` (dates complètes) + `date_dim` | entrepôt × année × mois | `stock_moyen` = moyenne de `inv_quantity_on_hand` (les `null` sont ignorés) ; `nb_dates`, `nb_lignes`, `nb_quantites_nulles` | Dernière date exclue (incomplète) ; pas de libellé d'entrepôt ni d'article (tables absentes) ; stock ~500 partout car tirage aléatoire entre 0 et 1000 |

Résultats (extraits des fichiers `preuves/silver_gold/gold_*.csv`) :

{{TABLE_GOLD}}
