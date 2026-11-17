# Questions de recul

1. **Rôle du NameNode** : il tient les métadonnées de HDFS (arborescence, droits, blocs et leur emplacement) et indique aux clients où lire. Vu dans `fsck` : il connaît le bloc `blk_1073741826` de `date_dim.dat` et son DataNode.
2. **NameNode / DataNode** : le NameNode sait où sont les données, les DataNodes les stockent (blocs) et lui envoient leur état.
3. **Blocs** : un gros fichier est découpé (128 Mo ici) pour être réparti sur plusieurs machines et traité en parallèle. Mes fichiers (15 Mo et 151 Ko) tiennent dans 1 bloc chacun.
4. **Réplication** : plusieurs copies de chaque bloc sur des DataNodes différents. Si un nœud tombe, les données restent lisibles. Ici le facteur est 1 donc aucune protection.
5. **Zones** : séparer les rôles (source, nettoyé, prêt à l'analyse), régler les droits par zone et savoir à quel niveau de qualité on est.
6. **Conserver Raw** : pouvoir rejouer les traitements, prouver ce qui a été reçu, corriger une erreur de traitement sans redemander la donnée.
7. **FlowFile** : l'unité qui circule dans NiFi : le contenu du fichier plus ses attributs (nom, taille, uuid, attributs ajoutés).
8. **Processor / Connection** : le processeur fait une opération ; la connexion transporte les FlowFiles entre deux processeurs selon une relation, avec une file d'attente.
9. **Provenance** : elle permet de reconstituer le parcours d'un fichier, de retrouver la cause d'un incident et de prouver le traitement.
10. **Échec technique / rejet métier** : échec technique = le traitement n'a pas pu s'exécuter (dossier absent, service arrêté, droits). Rejet métier = le traitement a fonctionné mais la donnée ne respecte pas une règle (colonne manquante, valeur interdite). Je n'ai testé que le premier cas.
11. **Relance sans contrôle** : doublons dans la destination ou écrasement. Constaté : `hdfs dfs -put` sans `-f` refuse (« File exists ») et PutHDFS en stratégie `fail` renvoie le FlowFile en `failure` (« file with same name already exists »).
12. **Limites du mono-nœud** : pas de tolérance aux pannes (réplication 1), pas de vraie répartition, un seul point de défaillance pour le NameNode, pas représentatif des performances d'un cluster.
13. **Copie locale ≠ dépôt HDFS** : copier un fichier sur le disque ne le met pas dans HDFS (pas de blocs, pas de métadonnées NameNode, pas de réplication). La preuve est un `hdfs dfs -ls` ou `fsck` sur le chemin HDFS.
14. **Pour reproduire une ingestion** : versions des composants, chemins source et destination, configuration des processeurs, empreintes des fichiers, date et utilisateur, commandes lancées, journaux.
