# UC-01 – Limites et hypothèses

## 1. Limites

| # | Limite | Conséquence | Statut |
|---|---|---|---|
| L1 | Le zip est tronqué : 7 tables sur plus de 20, aucune table de ventes ou de retours. | Les KPI de chiffre d'affaires, transactions, panier, quantités, remise et retours ne peuvent pas être calculés. | Vérifié |
| L2 | `inventory` est coupé (dernier jour à 11 808 lignes sur 90 000). | Le stock de la dernière semaine est faux, et on ne sait pas combien de semaines manquent. À exclure ou signaler. | Vérifié |
| L3 | Les `.dat` n'ont pas d'en-tête. | Les noms viennent du DDL de la spec, pas des fichiers. Si le kit réel diffère de la spec (la spec dit que le kit prime), les noms seraient faux. | Vérifié / Déduit |
| L4 | Données synthétiques. | Répartitions presque uniformes, aucune conclusion métier réelle (« le magasin X vend mieux » n'aurait pas de sens). | Vérifié (cours, TP) |
| L5 | Une table présente n'a pas tous ses champs renseignés : ≈ 0,02 % de valeurs vides sur les colonnes non clés. | Prévoir un traitement des NULL en Silver. | Vérifié |
| L6 | Valeur -1 dans `hd_vehicle_count` (3,9 %). | À ne pas moyenner telle quelle tant que son sens n'est pas connu. | À valider |
| L7 | Une vente magasin et une vente web ne sont pas modélisées pareil (ticket / commande, client facturé / client). | On ne les additionne pas sans règle commune. | Déduit (spec) |
| L8 | Vente, commande, ligne de vente, transaction et ticket sont des notions différentes. | KPI-02 compte des tickets et des commandes distincts, pas des lignes. | Déduit (cours) |
| L9 | Un clic web n'est pas un ajout au panier ni un achat. | `web_clickstreams` ne mesure pas les ventes (la colonne `wcs_sales_sk` pourrait lier un clic à une vente, non vérifié). | Hypothèse |
| L10 | Les retours sont distincts des ventes. | Le CA se calcule sans retours ; le taux de retour se calcule à part. | Déduit |
| L11 | Une corrélation entre deux KPI ne prouve pas une causalité. | Aucune recommandation causale à partir des seuls graphiques. | Cours |
| L12 | Le stock est par entrepôt, pas par magasin (`inv_warehouse_sk`, 5 entrepôts). | Le responsable de magasin ne peut pas suivre le stock de son magasin. | Vérifié |
| L13 | Données personnelles synthétiques dans `customer` (nom, email, login). | Même fictives, on les traite comme sensibles (masquage en Gold). | Vérifié |
| L14 | Provenance, version du kit, date et outil de génération non communiqués. | Traçabilité incomplète : marqué « non communiqué ». | À valider |

## 2. Hypothèses (à confirmer)

| # | Hypothèse | Comment la vérifier |
|---|---|---|
| H1 | Les tables absentes existent dans le kit complet du prof (le projet fil rouge les liste comme « observées »). | Demander au formateur le zip complet ou les fichiers manquants. |
| H2 | Dans les ventes, `ss_ticket_number` + `ss_item_sk` identifient une ligne de vente (idem `ws_order_number` + `ws_item_sk`). | Tester l'unicité dès que `store_sales` et `web_sales` sont reçus. |
| H3 | Les valeurs vides sont des NULL du générateur (NULL_CHANCE). | Comparer avec la spec ; taux constant → plausible. |
| H4 | -1 dans `hd_vehicle_count` veut dire « inconnu ». | Demander au formateur. |
| H5 | `customer_demographics` est un catalogue de profils et non une liste de personnes. | Compter les `cd_demo_sk` réellement utilisés par `customer` (99 000 clients, 1,9 M profils). |
| H6 | `inventory` contient d'autres semaines après la coupure. | Fichier complet nécessaire. |
| H7 | Les montants des ventes sont HT et après remise. | Vérifier dans les colonnes `*_ext_sales_price`, `*_net_paid`, `*_ext_list_price` sur les vraies données. |
| H8 | Le facteur d'échelle (volume) du kit est inconnu. | Les formules de taille de la spec dépendent d'un SF non communiqué. |

## 3. Questions de recul (UC-01)

**1. Quels besoins métier sont réellement couverts par les données ?**
Seulement « caractériser les clients » (clients, adresses, démographie, foyers, tranches de revenu), et partiellement le stock. Les besoins sur les ventes, les magasins, les produits et les retours ne sont pas couverts avec le zip reçu.

**2. Quels KPI ne peuvent pas être calculés de manière fiable ?**
KPI-01 à KPI-07 (CA, transactions, panier, quantités, évolution, remise, retours) car les tables de ventes et de retours sont absentes. KPI-08 (stock moyen) est calculable mais pas fiable sur la dernière semaine. KPI-09 et KPI-10 sont calculables.

**3. Quelle différence entre une donnée disponible et une donnée exploitable ?**
Disponible : le fichier est là. Exploitable : on connaît sa structure, ses clés, sa granularité, et sa qualité est suffisante. Exemple : `inventory` est disponible mais tronqué et sans libellé d'article, donc seulement partiellement exploitable. `hd_vehicle_count` est disponible mais -1 n'est pas expliqué.

**4. Quelles relations entre domaines restent à vérifier ?**
Toutes les relations avec les ventes et les retours (article, magasin, client, date, ticket, commande), `inventory` → `item` et `warehouse`, et le lien clic web → vente.

**5. Quelles limites du jeu synthétique faut-il prendre en compte ?**
Répartitions uniformes, NULL injectés au hasard, dates artificielles (1900 à 2199 dans `date_dim`), aucune réalité commerciale. On valide les méthodes et l'architecture, pas des résultats métier.

**6. Quelles données complémentaires seraient utiles à l'entreprise ?**
Prix de revient réels, saisonnalité et calendrier commercial, stock par magasin, motifs de retour, données de campagnes marketing, coûts logistiques, et pour le web des sessions qui relient clics et commandes. Si on en ajoute, elles restent séparées de TPCx-BB et marquées synthétiques.
