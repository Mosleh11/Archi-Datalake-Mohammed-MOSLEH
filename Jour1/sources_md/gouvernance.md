# UC-02 – Règles minimales de gouvernance

Proposition de règles. Rien n'est encore mis en œuvre. Pour chaque règle, je relie le besoin à ce qu'on a observé en UC-01.

| Domaine | Règle proposée | Lien avec UC-01 |
|---|---|---|
| **Traçabilité de la provenance** | À chaque dépôt en Bronze, un manifeste enregistre : nom du fichier, source (ici : `retail_project.zip` fourni par le formateur), date de dépôt, taille, nombre de lignes, somme de contrôle (SHA-256), version du kit si connue (sinon « non communiqué »). Silver et Gold gardent une colonne ou une table de lineage : fichier d'origine, version du traitement, date. | Version, date et outil de génération du kit sont inconnus. Le zip était corrompu : on veut pouvoir prouver quel fichier a été utilisé. |
| **Documentation des fichiers et tables** | Un dictionnaire de données par table (nom, description, colonnes, types, clés, grain, source). Point de départ : `inventaire_sources.xlsx`. Catalogue accessible aux utilisateurs. | Les `.dat` n'ont pas d'en-tête : sans dictionnaire, personne ne sait ce que veut dire la colonne 3. |
| **Contrôles de qualité** | À chaque entrée en Silver : nombre de champs par ligne, ligne incomplète rejetée, clé unique, vides comptés, valeurs hors plage, clés étrangères sans orphelin, nombre de lignes attendu. Les lignes rejetées vont dans `_rejets/`. Seuil d'alerte sur le taux de rejet (à fixer). | Tronqué (inventory), vides (0,02 %), -1 (3,9 % de `hd_vehicle_count`), 22 clients sans adresse. |
| **Gestion des accès** | Principe du moindre privilège, par rôle et par zone : Bronze en écriture par NiFi seulement et en lecture seule pour l'équipe Data ; Silver pour l'équipe Data ; Gold en lecture pour les utilisateurs métier (direction, contrôle de gestion, magasins, stocks). Responsable de magasin limité à son magasin (à valider avec les données `store`). | Plusieurs profils d'utilisateurs avec des besoins différents. |
| **Protection des données** | `customer` contient nom, prénom, email, login. Même synthétiques, on les traite comme personnelles : en Gold, on supprime ou on hache ces champs (on garde l'identifiant client). Chiffrement du stockage et des échanges. Pas de données personnelles dans les journaux. | A7 de la qualification. |
| **Suivi des traitements** | Chaque traitement écrit un journal : début, fin, lignes lues / écrites / rejetées, version du code, erreur. Un traitement doit pouvoir être **rejoué** depuis Bronze. Alerte en cas d'échec ou de rejet anormal. | Reproductibilité demandée par le cours. |
| **Maîtrise des coûts et des volumes** | Parquet compressé et partitionné ; suppression des copies intermédiaires ; durée de conservation par zone (Bronze conservé longtemps car c'est la preuve, Silver et Gold reconstructibles) ; suivi du volume par zone. Dimensionnement impossible tant que le volume du kit complet est inconnu. | `inventory` représente 78 % du volume reçu (398 Mo sur 510 Mo). |
| **Séparation des données** | Les données complémentaires (JSON, logs) sont dans un dossier séparé, marquées « synthétiques » avec leur provenance. | Exigence du TP. |

## Responsabilités (proposition)

| Rôle | Responsabilité |
|---|---|
| Équipe Data | pipelines, qualité, catalogue, droits techniques |
| Propriétaire de chaque domaine (ex. responsable des stocks) | valider la définition des données et des KPI de son domaine |
| Direction / contrôle de gestion | valider les KPI officiels |

## Risques si on ne le fait pas

Data swamp (fichier sans description), fuite de données personnelles, KPI différents selon les équipes, impossibilité de reproduire un chiffre, coûts de stockage qui augmentent sans contrôle.
