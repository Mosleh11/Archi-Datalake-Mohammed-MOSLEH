# J4-06 – Synthèse décisionnelle

## Constats

| # | Résultat observé | Interprétation possible | Limite | Recommandation |
|---|---|---|---|---|
| 1 | Le stock moyen mensuel est de 500 unités ± 0,5 % pour les 5 entrepôts, sur 56 mois, sans tendance (graphique 1). | Aucun entrepôt ni période ne se distingue. Les quantités se comportent comme un tirage uniforme sur 0–1 000. | Données synthétiques ; dernière date exclue ; pas d'article ni de ventes. | Ne pas utiliser ce Gold pour décider d'un réapprovisionnement. Ajouter `item`, `warehouse` et les ventes pour calculer une rotation. |
| 2 | Les clients sont concentrés : TX 8,27 %, GA 5,13 %, 10 états = 41,09 % (graphique 2). | Le portefeuille de clients référencés est plus important au Texas. | Clients référencés (pas actifs) ; aucune population ni vente pour comparer. | Relier les clients aux ventes (`store_sales`) pour mesurer le chiffre d'affaires par état avant d'orienter le marketing. |
| 3 | Les 20 tranches de revenu contiennent entre 4,71 % et 5,50 % des clients (graphique 3). | Aucun segment de revenu ne domine : le revenu seul ne permet pas de cibler. | Écarts non testés ; jeu synthétique quasi uniforme ; unité monétaire inconnue. | Croiser avec d'autres variables (potentiel d'achat, nombre de véhicules) une fois les ventes disponibles. |
| 4 | Les années de naissance sont réparties de façon plate entre 1924 et 1992 (graphique 4). | Pas de classe d'âge dominante. | 30 valeurs manquantes. | Idem constat 3. |

Ces constats décrivent des répartitions : **une corrélation ou un écart observé ne démontre pas une cause**. Les données étant synthétiques, ces résultats servent à démontrer la démarche d'analyse, pas à décrire une entreprise réelle.

## Limites globales

- Zip tronqué : aucune table de ventes, de retours, d'articles ni de magasins → 7 KPI sur 10 non calculables, aucune analyse de ventes, de produits, de magasins ni de canaux.
- `inventory` tronqué : dernière date exclue, 5 611 quantités manquantes ignorées.
- Données synthétiques : répartitions quasi uniformes, aucune conclusion métier réelle.
- Pas de test statistique sur les écarts observés.

## Questions de recul (1 à 7)

1. **Pourquoi vérifier la granularité avant de calculer un KPI ?** Parce que le résultat dépend de ce que représente une ligne. Dans ce TP, un client par ligne (`clients_enrichis`) permet de compter des clients ; si la jointure avait dupliqué des clients, le KPI-09 aurait été faux. C'est pour cela que les jointures du Jour 3 vérifient l'unicité de la clé avant de joindre.
2. **Différence entre un nombre de lignes et un nombre de transactions ?** Une transaction (ticket ou commande) peut contenir plusieurs lignes d'articles. Compter les lignes de ventes surestimerait les transactions et fausserait le panier moyen. Ici aucun ticket n'est disponible, donc ni transactions ni panier moyen ne sont calculés.
3. **Limites rencontrées ?** Zip tronqué (7 tables), `inventory` coupé en cours de fichier, valeurs manquantes (22 adresses, 63 `hd_dep_count`, 4 003 `hd_vehicle_count`), unité monétaire inconnue, données synthétiques très régulières.
4. **Indicateurs non calculés ?** KPI-01 à KPI-07 : les tables de ventes et de retours ne sont pas dans le zip. Aucune marge non plus (pas de coûts).
5. **Comment la cohérence a été vérifiée ?** Clés uniques, sommes des Gold égales au Silver (99 000), moyenne pondérée du stock Gold égale à la moyenne recalculée sur le Silver, comparaison avec les chiffres du rapport du Jour 3.
6. **Constat statistique ou conclusion causale ?** Un constat statistique décrit ce qu'on observe (TX a plus de clients). Une conclusion causale explique pourquoi (TX est plus attractif), ce que ces données ne permettent pas : il faudrait la population, les ventes et un cadre d'analyse.
7. **Pourquoi identifier les données synthétiques ?** Parce que leurs régularités (stock autour de 500, distributions plates) sont des artefacts de génération, pas des comportements de clients. Les présenter comme réels induirait en erreur.
