# CO-02 – Convention de nommage

Chemin : `/retail-lake/<zone>/<source>/<lot>/<table>.dat`

| Élément | Règle | Exemple |
|---|---|---|
| zone | `raw`, `bronze`, `silver`, `gold`, `quality`, `logs` | `raw` |
| source | origine des données | `tpcxbb` ; `nifi` pour les dépôts faits par le flux |
| lot | `initial` pour la livraison d'origine, `refresh/AAAA-MM-JJ` pour les suivantes | `initial` |
| fichier | nom d'origine du kit, conservé | `household_demographics.dat` |

Justification : le nom du dossier dit d'où vient le fichier et à quelle livraison il appartient, sans renommer les fichiers du kit (on peut les retrouver dans la spec). Le domaine métier est porté par la table (clients, calendrier, stocks). La période n'est pas dans les noms actuels car le kit n'en donne pas ; elle ira dans `refresh/AAAA-MM-JJ`. Un doublon est refusé (stratégie `fail`).
