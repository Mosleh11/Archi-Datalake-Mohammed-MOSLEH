# J4-04 – Analyses métier

Trois analyses, rattachées aux questions du Jour 1 (`Jour1/sources_md/questions_decisionnelles.md`). Les questions sur les ventes, les produits, les magasins et les canaux (questions 1, 2, 3, 5, 6, 7, 8, 9, 10) restent sans réponse faute de données.

## Analyse 1 – Comment évolue le stock dans le temps ? (question 11, KPI-08)

1. **Question métier** : le niveau de stock évolue-t-il dans le temps, et diffère-t-il selon l'entrepôt ?
2. **Données** : `gold/stock_moyen_entrepot_mois` (5 entrepôts × 56 mois, de janvier 2001 à août 2005), recoupé avec `silver/inventory`.
3. **Méthode** : stock moyen = moyenne de `inv_quantity_on_hand` par entrepôt et par mois, sur les dates complètes. Contrôle croisé : la moyenne pondérée des 280 lignes du Gold (500,16) est identique à la moyenne recalculée sur le Silver (écart 0,0003).
4. **Résultats** : le stock moyen mensuel reste entre 497,7 et 502,8 unités pour les cinq entrepôts ; moyenne par entrepôt de 499,92 à 500,31 ; moyenne globale 500,16.
5. **Interprétation** : aucune tendance, aucune saisonnalité et aucun écart entre entrepôts : les variations sont de l'ordre de ± 0,5 % autour de 500 et se comportent comme du bruit. C'est cohérent avec des quantités tirées au hasard entre 0 et 1 000.
6. **Limites** : la dernière date du fichier est exclue (fichier tronqué) ; 5 611 quantités manquantes ignorées ; pas de libellé d'article ni d'entrepôt ; le stock est hebdomadaire et non par magasin ; un stock moyen seul ne dit rien sur les ruptures ni sur la rotation (il faudrait les ventes).

## Analyse 2 – Où se trouvent les clients ? (question 4, KPI-09)

1. **Question métier** : comment les clients se répartissent-ils géographiquement ?
2. **Données** : `gold/clients_par_etat` (52 lignes : 51 codes d'état et « Non renseigné »), 99 000 clients.
3. **Méthode** : comptage de clients par état de l'adresse courante ; part en % du total ; graphique limité aux 10 premiers états (filtre documenté, le tableau complet est dans `preuves/uc08/resultats/clients_par_etat.csv`).
4. **Résultats** : TX est en tête avec 8 189 clients (8,27 %), devant GA (5 081 ; 5,13 %), VA (4 394), KY (3 848) et KS (3 379). Les 10 premiers états regroupent 41,09 % des clients. 22 clients (0,02 %) n'ont pas d'état.
5. **Interprétation** : la répartition est concentrée : TX compte environ 1,6 fois plus de clients que GA. 
6. **Limites** : on compte des clients référencés, pas des clients actifs ni un chiffre d'affaires ; on ne sait pas si TX a plus de clients parce que sa population est plus grande (aucune donnée de population) ; adresse courante seulement.

## Analyse 3 – Comment les clients se répartissent-ils par tranche de revenu du foyer ? (question 4, KPI-10)

1. **Question métier** : quel est le profil de revenu des clients ?
2. **Données** : `gold/clients_par_tranche_revenu` (20 tranches de 10 000 et « Non renseigné » : 60 clients).
3. **Méthode** : comptage par tranche ; comparaison à la moyenne (4 947 clients par tranche) ; `ib_lower_bound` et `ib_upper_bound` donnent les bornes.
4. **Résultats** : de 4 660 clients (90 001–100 000) à 5 447 (130 001–140 000) ; rapport max / min = 1,17 ; la tranche la plus peuplée représente 5,50 % des clients, pour 5 % attendus si la répartition était parfaitement égale.
5. **Interprétation** : la répartition est presque uniforme : aucune tranche ne domine. Sur ces données, le revenu du foyer ne permet pas de cibler un segment.
6. **Limites** : l'unité monétaire n'est pas précisée par la spec ; le revenu est celui du foyer ; les écarts de ± 10 % ne sont pas testés statistiquement, et un jeu synthétique est généré pour être quasi uniforme.

## Vérification de la cohérence des résultats

- Les sommes des Gold (clients par état, par tranche) retrouvent les 99 000 clients du Silver (cellule de contrôle du notebook).
- La moyenne pondérée du stock Gold est égale à la moyenne recalculée depuis le Silver (écart 0,0003).
- Les compteurs du notebook retrouvent les chiffres du rapport du Jour 3 (22 clients sans adresse, 60 sans tranche, 5 611 quantités manquantes, 21 780 000 lignes de dates complètes).
