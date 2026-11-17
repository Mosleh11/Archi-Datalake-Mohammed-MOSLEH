# CO-04 – Supervision NiFi

Tableau de suivi du flux (valeurs relevées par l'API `/flow/process-groups/.../status`, fichiers `UC04_preuves/execution/statut_flux.json` et `run2_income_band_statut.json`, capture `canvas_flux_compteurs.png`) :

| Processeur | État après exécution | Entrées (5 min) | Sorties (5 min) | Octets lus / écrits | Remarque |
|---|---|---|---|---|---|
| GetFile_entree | Arrêté | 0 | 1 | 327 / 327 | 2e run, `income_band.dat` |
| UpdateAttribute_suivi | Arrêté | 1 | 1 | 0 / 0 | ajoute `source`, `zone`, `ingere_par` |
| PutHDFS_raw_nifi | Arrêté | 1 | 0 | 327 / 0 | écrit dans HDFS, relation success auto-terminée |
| LogAttribute_echec | Arrêté | 0 | 0 | 0 / 0 | reçoit les échecs |

| Connexion | File d'attente |
|---|---|
| GetFile → UpdateAttribute (success) | 0 |
| UpdateAttribute → PutHDFS (success) | 0 |
| PutHDFS → LogAttribute (failure) | **1 FlowFile (151,46 Ko)** : le doublon refusé du test |

Les compteurs sont des fenêtres de 5 minutes (affichage NiFi) : ils redescendent à 0 ensuite. Événements de provenance : voir `UC04_preuves/provenance/`. Les journaux techniques sont ceux de `docker logs j2-nifi` (`nifi-app.log`).
