# CO-01 – Blocs et réplication HDFS

**Blocs** : HDFS découpe un fichier en blocs de taille fixe (128 Mo ici : `Block Size 128 MB` dans l'explorateur, `%o` = 134 217 728 octets avec `hdfs dfs -stat`). Chaque bloc est stocké sur un DataNode ; le NameNode garde la liste des blocs de chaque fichier et leur emplacement.

**Observé** : `date_dim.dat` (15 395 800 octets) = 1 bloc `blk_1073741826`, `household_demographics.dat` (155 100 octets) = 1 bloc `blk_1073741825`. Les deux sont sur le DataNode `172.20.0.3` (`fsck -files -blocks -locations`). Un fichier plus petit que 128 Mo n'occupe que sa taille réelle sur le disque.

**Réplication** : le facteur est 1 (`dfs.replication` = 1, `replication=1` dans `fsck`). Avec 3 DataNodes et un facteur 3, chaque bloc aurait 3 copies et un nœud en panne n'empêcherait pas la lecture.

**Limites du mono-nœud** : un seul DataNode donc pas de copie de secours (`Average block replication: 1.0`) ; si le DataNode disparaît, les données sont perdues ; le NameNode est aussi un point unique de défaillance ; pas de répartition de charge. Je n'ai pas changé les paramètres de réplication ni provoqué de panne de nœud.
