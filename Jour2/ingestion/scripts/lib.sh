export MSYS_NO_PATHCONV=1
# execute une commande dans un conteneur et l'ecrit dans un journal avec date et code retour
# usage : run <journal> <conteneur> <commande...>
run() {
  local log="$1" ctr="$2"; shift 2
  { echo "[$(date '+%F %T')] $ctr \$ $*"; docker exec "$ctr" bash -c "$*" 2>&1; echo "-> code retour $?"; echo; } | tee -a "$log"
}
