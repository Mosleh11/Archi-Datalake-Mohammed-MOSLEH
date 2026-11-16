"""
Analyse des fichiers .dat du kit TPCx-BB.
Usage : python analyse_kit.py <dossier data> [dossier sortie]

Les .dat n'ont pas d'en-tête : les noms de colonnes viennent du DDL de la
spec TPCx-BB 1.7.0 (schema_spec_tpcxbb.json), dans l'ordre.
"""
import os, sys, json
from array import array

data_dir = sys.argv[1]
out_dir = sys.argv[2] if len(sys.argv) > 2 else "."
here = os.path.dirname(os.path.abspath(__file__))
schema = json.load(open(os.path.join(here, "schema_spec_tpcxbb.json")))
SEP = "|"
res = {}


def lire(table):
    """génère les lignes complètes d'une table (séparées par |)"""
    dossier = os.path.join(data_dir, table)
    for nom in sorted(os.listdir(dossier)):
        with open(os.path.join(dossier, nom), encoding="utf-8", errors="replace", newline="") as f:
            for ligne in f:
                yield ligne


def analyser(table):
    cols = schema[table]
    n = len(cols)
    r = {"colonnes_spec": n, "lignes": 0, "lignes_mauvais_nb_colonnes": 0,
         "nb_colonnes_observes": {}, "nulls": [0] * n, "non_numeriques": [0] * n,
         "min": [None] * n, "max": [None] * n, "dernier_ligne_incomplete": False}
    numeriques = [c[1] in ("bigint", "int") for c in cols]
    distinct = {}  # petites colonnes seulement
    cle_pk = array("q")
    last_complete = True
    for ligne in lire(table):
        complete = ligne.endswith("\n")
        champs = ligne.rstrip("\r\n").split(SEP)
        k = len(champs)
        r["nb_colonnes_observes"][k] = r["nb_colonnes_observes"].get(k, 0) + 1
        if k != n or not complete:
            r["lignes_mauvais_nb_colonnes"] += 1
            if not complete:
                r["dernier_ligne_incomplete"] = True
            continue
        r["lignes"] += 1
        for i, v in enumerate(champs):
            if v == "":
                r["nulls"][i] += 1
            elif numeriques[i]:
                try:
                    x = int(v)
                    if r["min"][i] is None or x < r["min"][i]: r["min"][i] = x
                    if r["max"][i] is None or x > r["max"][i]: r["max"][i] = x
                except ValueError:
                    r["non_numeriques"][i] += 1
        if table == "inventory":
            cle_pk.append((int(champs[0]) << 40) | (int(champs[1]) << 20) | int(champs[2]))
    r["colonnes"] = [c[0] for c in cols]
    r["types_spec"] = [c[1] for c in cols]
    if table == "inventory":
        cle_pk = sorted(cle_pk)
        r["doublons_cle_date_item_entrepot"] = sum(1 for a, b in zip(cle_pk, cle_pk[1:]) if a == b)
    return r


def charger_col(table, idx):
    return [l.rstrip("\r\n").split(SEP)[idx] for l in lire(table)]


tables = [t for t in os.listdir(data_dir) if t in schema]
for t in sorted(tables):
    print("analyse", t, flush=True)
    res[t] = analyser(t)

# ---- unicité des clés primaires (tables de référence) ----
pk = {"customer": 0, "customer_address": 0, "customer_demographics": 0,
      "date_dim": 0, "household_demographics": 0, "income_band": 0}
cles = {}
for t, i in pk.items():
    if t in res:
        vals = charger_col(t, i)
        s = set(vals)
        cles[t] = s
        res[t]["pk"] = {"colonne": schema[t][i][0], "valeurs": len(vals), "distinctes": len(s),
                        "nulls": vals.count("")}
for t in ("customer", "customer_address"):
    if t in res:  # unicité de l'identifiant texte
        vals = charger_col(t, 1)
        res[t]["id_texte_distincts"] = len(set(vals))

# ---- jointures ----
def jointure(src, col, dest):
    i = [c[0] for c in schema[src]].index(col)
    vals = charger_col(src, i)
    nul = vals.count("")
    non_nuls = [v for v in vals if v != ""]
    orph = sum(1 for v in non_nuls if v not in cles[dest])
    return {"source": f"{src}.{col}", "cible": dest, "lignes": len(vals), "nulls": nul,
            "sans_correspondance": orph}

res["jointures"] = []
for src, col, dest in [
    ("customer", "c_current_cdemo_sk", "customer_demographics"),
    ("customer", "c_current_hdemo_sk", "household_demographics"),
    ("customer", "c_current_addr_sk", "customer_address"),
    ("customer", "c_first_shipto_date_sk", "date_dim"),
    ("customer", "c_first_sales_date_sk", "date_dim"),
    ("household_demographics", "hd_income_band_sk", "income_band"),
]:
    if src in res and dest in cles:
        res["jointures"].append(jointure(src, col, dest))

# inventory : date -> date_dim ; item et warehouse n'ont pas de table de référence dans le zip
if "inventory" in res and "date_dim" in cles:
    dates, items, whs = set(), set(), set()
    for l in lire("inventory"):
        c = l.rstrip("\r\n").split(SEP)
        if len(c) == 4 and l.endswith("\n"):
            dates.add(c[0]); items.add(c[1]); whs.add(c[2])
    res["jointures"].append({"source": "inventory.inv_date_sk", "cible": "date_dim", "lignes": res["inventory"]["lignes"],
                             "valeurs_distinctes": len(dates), "sans_correspondance": sum(1 for d in dates if d not in cles["date_dim"])})
    res["inventory"]["distinct"] = {"dates": len(dates), "items": len(items), "entrepots": len(whs)}
    # plage de dates réelle
    dd = {}
    for l in lire("date_dim"):
        c = l.split(SEP)
        if c[0] in dates:
            dd[c[0]] = c[2]
    ds = sorted(dd.values())
    res["inventory"]["dates_min_max"] = [ds[0], ds[-1]] if ds else None

# ---- tailles ----
for t in res:
    if t in schema:
        d = os.path.join(data_dir, t)
        res[t]["taille_octets"] = sum(os.path.getsize(os.path.join(d, f)) for f in os.listdir(d))
        res[t]["fichiers"] = os.listdir(d)

# ---- date_dim : plage de dates ----
if "date_dim" in res:
    ds = [l.split(SEP)[2] for l in lire("date_dim")]
    res["date_dim"]["d_date_min_max"] = [min(ds), max(ds)]

os.makedirs(out_dir, exist_ok=True)
json.dump(res, open(os.path.join(out_dir, "resultats_analyse.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("ok ->", os.path.join(out_dir, "resultats_analyse.json"))
