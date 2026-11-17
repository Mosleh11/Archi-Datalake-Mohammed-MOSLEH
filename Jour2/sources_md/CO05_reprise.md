# Procédure de reprise après échec d'ingestion (CO-05)

Procédure proposée à partir de ce qui a été observé. Les étapes 1 à 4 ont été testées (doublon refusé par PutHDFS, erreur de validation GetFile). Le reste est de la conception.

1. **Identifier l'échec** : processeur invalide ou FlowFile bloqué dans une file (canvas NiFi, relation `failure` vers `LogAttribute_echec`), ou code retour différent de 0 dans le journal du script.
2. **Retrouver le fichier source** : le nom et l'uuid sont dans les événements de provenance ; la source d'origine reste dans le kit.
3. **Éviter les doublons** : `PutHDFS` en `fail` et `hdfs dfs -put` sans `-f` refusent d'écraser (testé : « file with same name already exists »). Avant de relancer, lister la destination : `hdfs dfs -ls /retail-lake/raw/nifi`.
4. **Relancer** : corriger la cause (chemin, droits, service), remettre le fichier dans `/data/nifi/input`, démarrer PutHDFS puis GetFile. Ne pas relancer en boucle avant d'avoir compris le premier résultat.
5. **Vérifier** : taille avec `hdfs dfs -du -h`, empreinte avec `hdfs dfs -cat <fichier> | sha256sum` comparée à la source.

Limite : sans contrôle de doublon par nom ou empreinte, un deuxième fichier de même contenu mais de nom différent serait accepté.
