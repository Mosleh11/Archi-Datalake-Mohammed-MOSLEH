# UC-02 – Comparaison des architectures

## 1. Contraintes tirées de UC-01

| Contrainte | Constat (source) |
|---|---|
| Formats | texte `.dat` délimité par `\|`, sans en-tête, CRLF (vérifié) ; JSON/logs possibles en complément (à valider) |
| Volumes constatés | 510 Mo pour 7 tables, dont `inventory` 398 Mo (21,8 M lignes) tronqué. Volume du kit complet **inconnu** (hypothèse : bien plus grand avec les ventes et les clics) |
| Diversité des domaines | clients, dates, stocks observés ; ventes, retours, produits, magasins, web, avis attendus |
| Historisation | oui : comparer les périodes, évolution des ventes et du stock |
| Qualité | NULL injectés (0,02 %), valeur -1 inexpliquée, fichier tronqué : contrôles obligatoires |
| Usages analytiques | KPI de ventes, stocks, clients ; exploration ; traitements PySpark (cours) |
| Sécurité et accès | données personnelles synthétiques (nom, email) à masquer ; accès par profil |
| Évolution | nouvelles sources prévues (JSON, logs), passage au cloud Azure (ADLS Gen2) au Jour 4 |

## 2. Les trois approches

| Critère | Data Warehouse | Data Lake en zones | Data Lakehouse |
|---|---|---|---|
| Principe | Entrepôt central intégré, historisé, modélisé (étoile / flocon). Données transformées avant chargement (ETL) | Stockage de données variées dans leur format d'origine, organisé en zones (Bronze / Silver / Gold), schéma appliqué à la lecture | Stockage de type lake avec une couche de gestion de tables (schéma, transactions, métadonnées) inspirée du warehouse |
| Types de données adaptés | Structurées | Structurées, semi-structurées (JSON), non structurées (avis, images) | Idem lake, avec tables gérées |
| Avantages | Modèle clair, requêtes BI simples et rapides, données fiables | Conserve le brut, très flexible, coût de stockage faible, nouveaux usages possibles | Fiabilité (schéma, évolutions, éventuellement transactions), un seul stockage pour BI et traitements |
| Limites | Rigide si les sources changent, intégration longue, mal adapté aux données non structurées, évolution coûteuse | Sans gouvernance : « data swamp ». Pas de garanties transactionnelles avec des fichiers seuls | Plus complexe, dépend de la technologie de table choisie (Delta, Iceberg, Hudi), compétences à acquérir |
| Usages | Reporting, tableaux de bord, KPI stables | Exploration, data science, conservation de l'historique brut | BI + traitements + exploration sur les mêmes tables |
| Gouvernance | Règles d'intégration et de qualité strictes | Catalogue, métadonnées, droits par zone indispensables | Catalogue + gestion des schémas et versions |
| Pertinence pour Retail Intelligence | Bien pour la couche finale de KPI (faits et dimensions) mais seul il ne conserve pas le brut ni les futurs JSON/logs | Très pertinent : le cours impose Hadoop/HDFS, NiFi, Spark, Parquet et la conservation de la provenance | Pertinent plus tard (Jour 3, facultatif) ; Delta Lake n'est pas obligatoire |

## 3. Choix retenu

**Un Data Lake organisé en zones Bronze / Silver / Gold, avec une zone Gold modélisée en étoile (esprit Data Warehouse).** Le Lakehouse reste une évolution possible.

Pourquoi :

1. **Le brut doit être conservé** avec sa provenance : le zip est incomplet, la version du kit n'est pas connue, il faut pouvoir rejouer les traitements quand les fichiers manquants arriveront.
2. **Les contrôles qualité sont indispensables** (fichier tronqué, NULL, -1) : la zone Silver existe pour ça.
3. **Les composants imposés par le parcours** (HDFS, NiFi, Spark, Parquet) correspondent naturellement à un lake en zones.
4. **Les KPI ont besoin d'un modèle clair** : on garde la logique faits/dimensions dans Gold.
5. **Évolutivité** : d'autres sources (JSON, logs) pourront entrer en Bronze sans refaire le modèle.

Limites de ce choix : demande de la discipline de gouvernance (catalogue, droits), les garanties transactionnelles ne viennent pas des fichiers Parquet seuls, et le volume réel du kit est inconnu donc le dimensionnement reste une hypothèse.

## 4. Questions de recul (UC-02)

**1. Pourquoi un Data Lake peut-il compléter un Data Warehouse ?**
Le warehouse sert les KPI propres et stables, mais il ne garde pas facilement le brut ni les formats variés. Le lake conserve tout et alimente le warehouse. Les deux coexistent.

**2. Dans quels cas un Lakehouse est-il pertinent ?**
Quand on veut BI et traitements sur le même stockage avec des garanties (schéma, historique des versions, mises à jour fiables), ou quand plusieurs moteurs lisent les mêmes tables. Ici : si on doit corriger ou mettre à jour des données de Silver/Gold (ex. arrivée tardive des ventes).

**3. Pourquoi conserver les données brutes ?**
Pour rejouer les transformations après une erreur ou un changement de règle, pour prouver la provenance, et parce qu'une donnée transformée ne se reconstruit pas toujours. Dans notre cas : le brut permettra de relancer l'analyse quand les fichiers complets seront disponibles.

**4. Pourquoi organiser les données en zones ?**
Chaque zone a un rôle, un niveau de confiance et des droits d'accès différents (brut en lecture seule, Silver pour l'équipe Data, Gold pour les utilisateurs métier). Ça évite de mélanger données brutes et chiffres officiels.

**5. Quelles garanties le seul stockage Parquet n'apporte-t-il pas ?**
Pas de transactions (écritures atomiques), pas de gestion des versions/retour arrière, pas de contrôle d'évolution de schéma entre fichiers, pas de catalogue ni de droits. Il apporte seulement un format colonnaire typé et compressé.

**6. Quels risques si la gouvernance est insuffisante ?**
Data swamp (données introuvables ou incompréhensibles), fuite de données personnelles, chiffres contradictoires entre équipes, coûts qui augmentent, traitements impossibles à reproduire.

**7. Quels composants sont indispensables au socle et lesquels sont de l'approfondissement ?**
Socle : Linux/Ubuntu, Python, Hadoop/HDFS (avec repli documenté), NiFi (avec repli documenté), Spark/PySpark, Parquet comme référence, ADLS Gen2 comme objectif cloud. Facultatifs : HBase, Delta Lake. À étudier/présenter : Azure Data Factory et Synapse.
