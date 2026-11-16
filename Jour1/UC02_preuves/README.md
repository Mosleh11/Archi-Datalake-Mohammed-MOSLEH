# Preuves UC-02

Au Jour 1, **rien n'a été installé ni déployé** (ni Hadoop, ni NiFi, ni Spark, ni Azure). Seul Python a servi (scripts UC-01). Il n'y a donc pas de captures de manipulations : les preuves sont des schémas de conception.

| # | Preuve | Ce qu'elle démontre |
|---|---|---|
| P1 | `architecture_cible.svg` | Architecture annotée : sources, zones Bronze / Silver / Gold, composants. Conception. |
| P2 | `schema_flux.svg` | Flux de données de la source au Gold, avec l'outil à chaque étape. Conception. |
| P3 | `schema_besoins.svg` | Schéma fonctionnel UC-01 (besoin vers données), repris pour lier UC-01 et UC-02. |

Les tableaux de comparaison, de composants, de gouvernance et de correspondance local / Azure sont dans `UC02_architecture.pdf`.
