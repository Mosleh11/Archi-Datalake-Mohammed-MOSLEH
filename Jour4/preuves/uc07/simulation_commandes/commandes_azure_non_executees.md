# Commandes Azure prévues – NON EXÉCUTÉES

Aucune de ces commandes n'a été lancée : pas d'abonnement autorisé pour ce TP, et aucune ressource payante ne doit être créée sans validation du formateur. Les noms entre `<>` sont des valeurs à choisir. La syntaxe est à vérifier dans la documentation Azure CLI avant exécution. Aucun secret : l'authentification se fait par `az login` (identité Entra ID), pas par clé de compte.

```
# 1. groupe de ressources (région à confirmer selon les consignes)
az group create --name rg-retail-intelligence --location <region>

# 2. compte de stockage avec espace de noms hiérarchique (HNS) = ADLS Gen2
az storage account create --name <compte> --resource-group rg-retail-intelligence --location <region> \
  --sku Standard_LRS --kind StorageV2 --enable-hierarchical-namespace true \
  --min-tls-version TLS1_2 --allow-blob-public-access false

# 3. conteneur (système de fichiers) et répertoires
az storage fs create --name retail-intelligence --account-name <compte> --auth-mode login
az storage fs directory create --name bronze/tpcxbb/customer/ingest_date=2026-11-19 -f retail-intelligence --account-name <compte> --auth-mode login

# 4. dépôt du fichier de démonstration (échantillon de 200 lignes, données synthétiques)
az storage fs file upload --source customer_echantillon_200.dat \
  --path bronze/tpcxbb/customer/ingest_date=2026-11-19/customer_echantillon_200.dat -f retail-intelligence --account-name <compte> --auth-mode login

# 5. vérification : le fichier est listé, taille identique à celle du manifeste local
az storage fs file list -f retail-intelligence --path bronze --account-name <compte> --auth-mode login

# 6. droits : rôle RBAC sur le conteneur, puis ACL sur le répertoire gold
az role assignment create --assignee <id_groupe_analystes> --role "Storage Blob Data Reader" --scope <id_du_conteneur_ou_du_compte>
az storage fs access set --acl "user::rwx,group::r-x,other::---" -p gold -f retail-intelligence --account-name <compte> --auth-mode login

# 7. nettoyage en fin de test : supprime toutes les ressources du groupe
az group delete --name rg-retail-intelligence
```

Contrôles prévus après exécution : le compte affiche HNS activé ; les répertoires bronze, silver, gold existent ; le fichier déposé est listé avec la même taille que `customer_echantillon_200.dat` (26 305 octets) ; un compte de test sans rôle reçoit un refus (403) sur `gold/` ; aucune clé ni jeton dans le dépôt ; groupe de ressources supprimé.
