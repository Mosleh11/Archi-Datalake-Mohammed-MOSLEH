# UC-06 – Règles de nettoyage

Appliquées par `scripts/nettoyage.py` (log : `preuves/transformations/nettoyage_log.txt`, chiffres : `nettoyage_stats.json`). Principe : on ne supprime et on ne remplace rien sans règle explicite ; ce qui est écarté va dans `data/silver/_rejets/` avec son motif.

| Anomalie | Règle | Action appliquée | Justification |
|---|---|---|---|
| Espaces et champs vides | Tout champ est nettoyé avec `trim` ; un champ vide devient `null` | Toutes les colonnes de toutes les tables | Évite des valeurs « vides » qui ne seraient ni nulles ni exploitables |
| Type incorrect | Tout est lu en texte, converti vers le type de la spec (bigint, int, decimal, date) ; échecs comptés | `cast` ; une valeur non convertible devient `null` et est comptée | L'inférence automatique ne valide pas le schéma ; le DDL fait foi. Résultat : 0 échec sur les 6 tables |
| Valeur manquante sur une clé | Une ligne sans clé primaire (ou sans clé d'inventaire) n'est pas exploitable | Mise à l'écart dans `_rejets` avec le motif | Une ligne sans identifiant ne peut être ni jointe ni dédupliquée. Résultat : 1 ligne (inventory) |
| Valeur manquante optionnelle | Pas de règle métier pour la deviner | Conservée à `null`, jamais remplacée par 0 ou une moyenne | Inventer une valeur fausserait les agrégats ; les moyennes Spark ignorent les `null` |
| Doublon | Défini par la clé primaire (ou le triplet date, article, entrepôt) | `dropDuplicates` sur la clé ; compté | Définition claire, justifiée par la spec. Résultat : 0 doublon |
| Identifiant invalide | Clé non nulle et de type entier | Voir « Type incorrect » et « Valeur manquante sur une clé » | |
| Date incohérente | `d_date` converti en date (`yyyy-MM-dd`), `d_year` doit égaler l'année de `d_date` | Conversion, contrôle | Résultat : 0 incohérence |
| Valeur atypique : `hd_vehicle_count` = -1 | Un nombre de véhicules ne peut pas être négatif | Mis à `null` **et** marqué dans la colonne `vehicle_count_invalide` ; la ligne est conservée | Je ne supprime pas le foyer (ses autres colonnes servent) et je ne le remplace pas par 0 (valeur inventée). -1 ressemble à un code « inconnu ». 282 lignes |
| Valeur de domaine invalide | `ca_state` = 2 lettres majuscules, `ca_zip` = 5 chiffres, `c_preferred_cust_flag` ∈ {Y, N}, `c_birth_year` entre 1900 et 2025 | Hors domaine → `null` | Résultat : 0 valeur hors domaine |
| Fin de fichier tronquée (`inventory`) | La dernière ligne `38584\|1180` n'a que 2 champs sur 4 | Ligne rejetée avec le motif « ligne incomplète » | La valeur et l'entrepôt sont inconnus |
| Date d'inventaire incomplète | Une date est complète si elle a le même nombre de lignes que la plus grande (90 000) | Colonne `date_complete` ajoutée ; ligne conservée en Silver, **exclue** du Gold | Une moyenne sur 11 808 lignes au lieu de 90 000 serait biaisée vers certains articles |
| Quantité d'inventaire nulle (5 616) | Voir valeur manquante optionnelle | Conservée à `null` | Ne pas confondre « inconnu » et « stock nul » |
| Données personnelles | Minimiser : on ne garde que ce qui sert aux KPI | Supprimées en Silver : `c_first_name`, `c_last_name`, `c_login`, `c_email_address` (remplacée par `email_domaine`), `c_birth_day`, `c_birth_month`, rue / numéro / suite des adresses | Le jeu est synthétique, mais les champs ressemblent à des données personnelles (point soulevé au Jour 1) |
| Valeur négative | Aucune trouvée (`inv_quantity_on_hand` entre 0 et 1000) | Aucune | Une valeur négative n'est pas forcément une erreur (retour, correction) : on ne l'aurait pas supprimée sans en comprendre le sens |

## Résultats du nettoyage

{{TABLE_NETTOYAGE}}

Traçabilité : chaque jeu Silver contient `_source` (fichier d'origine) et `_traite_le` (horodatage du traitement). Les jeux sont écrits en Parquet dans `data/silver/<table>/`.
