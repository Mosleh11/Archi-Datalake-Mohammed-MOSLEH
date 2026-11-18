# UC-06 – Inventaire technique des sources

6 sources réellement utilisées sur les 7 du kit (`customer_demographics`, 77 Mo, n'est pas utilisée). Lecture avec `scripts/commun.py` : séparateur `|`, pas d'en-tête, CRLF, tout en texte ; noms et types des colonnes pris dans le DDL de la spec TPCx-BB v1.7.0 (`scripts/schema_spec_tpcxbb.json`).

| Information | customer | customer_address | household_demographics | income_band | date_dim | inventory |
|---|---|---|---|---|---|---|
| Nom du fichier | `customer.dat` | `customer_address.dat` | `household_demographics.dat` | `income_band.dat` | `date_dim.dat` | `inventory.dat` |
| Emplacement | `/data/raw/customer/` | `/data/raw/customer_address/` | `/data/raw/household_demographics/` | `/data/raw/income_band/` | `/data/raw/date_dim/` | `/data/raw/inventory/` |
| Format | texte `\|`, structuré | idem | idem | idem | idem | idem |
| Taille (octets) | 13 279 063 | 5 387 229 | 155 100 | 327 | 15 395 800 | 398 201 945 (tronqué) |
| Lignes | 99 000 | 49 500 | 7 200 | 20 | 109 573 | 21 791 809 (dont 1 incomplète) |
| Colonnes | 18 | 13 | 5 | 3 | 28 | 4 |
| Colonnes principales | `c_customer_sk`, `c_current_addr_sk`, `c_current_hdemo_sk`, `c_birth_year`, `c_preferred_cust_flag` | `ca_address_sk`, `ca_state`, `ca_zip`, `ca_city` | `hd_demo_sk`, `hd_income_band_sk`, `hd_vehicle_count` | `ib_income_band_sk`, `ib_lower_bound`, `ib_upper_bound` | `d_date_sk`, `d_date`, `d_year`, `d_moy` | `inv_date_sk`, `inv_item_sk`, `inv_warehouse_sk`, `inv_quantity_on_hand` |
| Types observés | tout `string` à la lecture ; types de la spec après conversion (bigint, int, string) | idem (+ `decimal(5,2)`) | bigint, int, string | bigint, int | bigint, int, string, date après conversion | bigint, int |
| Clé candidate | `c_customer_sk` | `ca_address_sk` | `hd_demo_sk` | `ib_income_band_sk` | `d_date_sk` | (`inv_date_sk`, `inv_item_sk`, `inv_warehouse_sk`) |
| Granularité | 1 ligne = 1 client | 1 ligne = 1 adresse | 1 ligne = 1 profil de foyer | 1 ligne = 1 tranche de revenu | 1 ligne = 1 jour | 1 ligne = 1 article, 1 entrepôt, 1 date (hebdomadaire) |
| Anomalies | ~0,02 à 0,03 % de valeurs manquantes ; colonnes personnelles (noms, e-mail, login) | ~0,02 à 0,05 % de valeurs manquantes | `hd_vehicle_count` = -1 (282 lignes) | aucune | `d_date` en texte ; calendrier 1900 à 2199 | dernière ligne incomplète, dernière date à 11 808 lignes sur 90 000, 5 616 quantités nulles |

## Questions techniques

1. **Structurés ou non ?** Les six fichiers sont structurés (texte délimité) ; il n'y a pas de JSON ni de non structuré dans le kit.
2. **Colonnes correctement typées ?** Le fichier ne porte aucun type : tout est lu en texte et converti selon la spec. Aucune valeur ne résiste à la conversion (0 échec, voir règles de nettoyage).
3. **Valeurs nulles ?** Oui, en très faible proportion (voir exploration).
4. **Identifiants uniques ?** Oui pour les six clés candidates (0 doublon).
5. **Granularité connue ?** Oui, voir tableau (elle vient de la spec et des données).
6. **Adaptées aux questions du Jour 1 ?** Pour les clients (KPI-09 et KPI-10) et le stock (KPI-08) : oui. Pour le chiffre d'affaires, les transactions, le panier, les quantités vendues, la remise et le retour (KPI-01 à KPI-07) : **non**, les tables de ventes et de retours ne sont pas dans le zip.
