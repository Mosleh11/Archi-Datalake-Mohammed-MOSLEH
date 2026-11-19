# J4-05 – Visualisations

Quatre graphiques produits avec Matplotlib à partir de petits tableaux calculés par Spark (`toPandas()` appliqué seulement après agrégation : 280, 52, 20 et 69 lignes). Fichiers PNG dans `visualisations/`. Aucun effet 3D, titres et axes explicites, source indiquée sous chaque graphique.

## 1. Stock moyen mensuel par entrepôt

![stock](IMG:stock_moyen_mensuel.png)

Courbe, une ligne par entrepôt. L'axe vertical commence à 0 : un axe zoomé sur 498–503 ferait paraître les écarts de ± 0,5 % comme de fortes variations. **Ce que le graphique montre** : cinq courbes qui oscillent autour de 500 sans tendance. **Interprétation** : pas de saisonnalité ni d'entrepôt différent des autres. **Limites** : voir analyse 1 ; données synthétiques.

## 2. Nombre de clients par état (10 premiers états)

![etat](IMG:clients_par_etat.png)

Barres (comparaison de catégories), valeurs affichées. **Résultat** : TX 8 189, GA 5 081, VA 4 394, puis des états entre 3 057 et 3 848. **Interprétation** : concentration sur quelques états. **Limites** : clients référencés (pas actifs), sans normalisation par la population ; 41 autres états non affichés.

## 3. Nombre de clients par tranche de revenu du foyer

![tranche](IMG:clients_par_tranche_revenu.png)

Barres avec la moyenne (4 947) en pointillés. **Résultat** : toutes les tranches sont entre 4 660 et 5 447. **Interprétation** : répartition quasi uniforme. **Limites** : unité monétaire non précisée ; 60 clients sans tranche non affichés.

## 4. Distribution des clients par année de naissance

![naissance](IMG:distribution_annee_naissance.png)

Histogramme construit sur un comptage par année (une barre par année, 69 années). **Résultat** : de 1 365 à 1 523 clients par année (moyenne 1 434), sans pic. **Interprétation** : distribution plate, typique d'une génération aléatoire uniforme. **Limites** : 30 clients sans année de naissance ; aucune date de référence pour calculer un âge.

Non produit : `ventes_par_magasin.png` et `evolution_ventes_mensuelles.png` (demandés en exemple dans le TP), car les ventes ne sont pas disponibles. Power BI n'a pas été utilisé (complément facultatif).
