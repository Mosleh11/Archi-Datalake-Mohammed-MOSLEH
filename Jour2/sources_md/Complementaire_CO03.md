# CO-03 – Contrôle d'intégrité local / HDFS

Méthode : comparaison d'empreintes SHA-256 et de contenu (`cmp`) entre le fichier source (poste, puis copie dans le conteneur) et le fichier relu depuis HDFS avec `hdfs dfs -get` (ou `-cat | sha256sum`).

| Fichier | Taille | SHA-256 source (poste) | SHA-256 relu depuis HDFS | Résultat |
|---|---|---|---|---|
| `household_demographics.dat` (dépôt manuel, `raw/tpcxbb/initial`) | 155 100 | `915aa15e…faf7` | `915aa15e…faf7` | identique (`cmp` : IDENTIQUE) |
| `date_dim.dat` (dépôt manuel) | 15 395 800 | `325c8922…56af` | `325c8922…56af` | identique (`cmp` : IDENTIQUE) |
| `household_demographics.dat` (dépôt NiFi, `raw/nifi`) | 155 100 | `915aa15e…faf7` | `915aa15e…faf7` | identique (empreinte seulement) |

Preuves : `UC03_preuves/hdfs/depot_et_controles.txt`, `UC04_preuves/execution/depot_nifi_hdfs.txt`.

Limites : une empreinte identique prouve que le contenu n'a pas changé, pas qu'il est correct (la source elle-même vient d'un zip tronqué, voir Jour 1). Avec une seule copie (réplication 1), HDFS ne peut pas réparer un bloc corrompu. Je n'ai pas utilisé `hdfs dfs -checksum`.
