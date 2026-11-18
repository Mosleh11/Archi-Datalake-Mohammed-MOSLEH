# UC-06 – Rapport de contrôles qualité

`scripts/controles_qualite.py` (log : `preuves/qualite/controles_qualite_log.txt`, résultats : `controles_qualite.json`). Les contrôles portent sur les jeux **Silver et Gold produits** : ils vérifient que les règles de nettoyage ont bien fonctionné (par exemple, `hd_vehicle_count >= 0` est vrai parce que les -1 ont été corrigés, ce que la remarque indique).

{{SYNTHESE_QUALITE}}

## Résultats détaillés

{{TABLE_QUALITE}}

## Anomalies, mises à l'écart et limites

- **Anomalie restante : une date d'inventaire incomplète** (11 808 lignes sur 90 000), conséquence du fichier source tronqué. La date est conservée en Silver (`date_complete = false`) et exclue du Gold ; la ligne incomplète est dans `data/silver/_rejets/inventory`.
- **Mises à l'écart** : 1 ligne (inventory). 282 `hd_vehicle_count` = -1 corrigés en `null` ; 5 616 quantités nulles conservées telles quelles.
- **Valeurs manquantes** : toutes sous 0,05 % ; non remplacées.
- **Non vérifiable** : relation `inventory` vers `item` et `warehouse` (tables absentes du zip) ; `customer` vers `customer_demographics` (non traitée au Jour 3, vérifiée au Jour 1 : 0 orphelin).
- **Limites des contrôles** : un contrôle « OK » prouve la cohérence interne des données, pas leur exactitude métier (jeu synthétique : les répartitions sont quasi uniformes) ; les seuils (1 % de nulls, plages de valeurs) sont mes choix, justifiés par la spec et les observations.
- **Corrections éventuelles** : obtenir le fichier `inventory` complet auprès du formateur pour retrouver la dernière date.
