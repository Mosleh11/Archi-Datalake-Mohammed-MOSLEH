"""Controles qualite sur Silver et Gold : completude, unicite, validite, coherence, volumes, integrite referentielle"""
import json
from pyspark.sql import functions as F
from commun import *

spark = session("controles_qualite")
S = lambda nom: lire_parquet(spark, "silver", nom)
G = lambda nom: lire_parquet(spark, "gold", nom)
stats = json.load(open(f"{PREUVES}/transformations/nettoyage_stats.json"))
res = []


def controle(famille, cible, regle, mesure, attendu, ok=None, remarque=""):
    ok = (mesure == attendu) if ok is None else ok
    res.append({"famille": famille, "cible": cible, "regle": regle, "mesure": mesure, "attendu": attendu,
                "statut": "OK" if ok else "ANOMALIE", "remarque": remarque})
    print(f"[{'OK' if ok else 'ANOMALIE'}] {famille} | {cible} | {regle} -> {mesure} (attendu {attendu}) {remarque}")


cle = {"customer": "c_customer_sk", "customer_address": "ca_address_sk", "household_demographics": "hd_demo_sk",
       "income_band": "ib_income_band_sk", "date_dim": "d_date_sk"}
tables = {t: S(t) for t in cle}
inv = S("inventory")

# Completude : cles non nulles
for t, c in cle.items():
    controle("Completude", t, f"{c} non nul", tables[t].filter(F.col(c).isNull()).count(), 0)
controle("Completude", "inventory", "inv_date_sk, inv_item_sk, inv_warehouse_sk non nuls",
         inv.filter(F.col("inv_date_sk").isNull() | F.col("inv_item_sk").isNull() | F.col("inv_warehouse_sk").isNull()).count(), 0)
n_inv = inv.count()
nulles = inv.filter(F.col("inv_quantity_on_hand").isNull()).count()
controle("Completude", "inventory", "inv_quantity_on_hand renseigne (seuil 1 % de nulls)", nulles, 0, ok=nulles / n_inv < 0.01,
         remarque=f"{nulles} nulls = {100 * nulles / n_inv:.3f} % ; lignes conservees, valeur non remplacee")
cust = tables["customer"]; n_cust = cust.count()
for c in ["c_current_addr_sk", "c_current_hdemo_sk", "c_birth_year"]:
    k = cust.filter(F.col(c).isNull()).count()
    controle("Completude", "customer", f"{c} renseigne (seuil 1 % de nulls)", k, 0, ok=k / n_cust < 0.01, remarque=f"{k} nulls = {100 * k / n_cust:.3f} %")

# Unicite
for t, c in cle.items():
    controle("Unicite", t, f"{c} unique", tables[t].count() - tables[t].select(c).distinct().count(), 0)
dup = inv.groupBy("inv_date_sk", "inv_item_sk", "inv_warehouse_sk").count().filter("count > 1").count()
controle("Unicite", "inventory", "(date, item, entrepot) unique", dup, 0)

# Validite : types
for t, v in stats.items():
    controle("Validite", t, "valeurs non convertibles vers le type de la spec", sum(v["echecs_conversion"].values()), 0)
ca = tables["customer_address"]
controle("Validite", "customer_address", "ca_state = 2 lettres majuscules (ou null)", ca.filter(F.col("ca_state").isNotNull() & ~F.col("ca_state").rlike("^[A-Z]{2}$")).count(), 0)
controle("Validite", "customer_address", "ca_zip = 5 chiffres (ou null)", ca.filter(F.col("ca_zip").isNotNull() & ~F.col("ca_zip").rlike("^[0-9]{5}$")).count(), 0)

# Coherence : valeurs dans un domaine valide
hd = tables["household_demographics"]
controle("Coherence", "household_demographics", "hd_vehicle_count >= 0", hd.filter(F.col("hd_vehicle_count") < 0).count(), 0,
         remarque=f"{stats['household_demographics']['vehicle_count_negatif_mis_a_null']} valeurs -1 corrigees en null au nettoyage")
controle("Coherence", "customer", "c_birth_year entre 1900 et 2025", cust.filter(~F.col("c_birth_year").between(1900, 2025)).count(), 0)
dd = tables["date_dim"]
controle("Coherence", "date_dim", "d_year = annee de d_date", dd.filter(F.year("d_date") != F.col("d_year")).count(), 0)
ib = tables["income_band"]
controle("Coherence", "income_band", "borne basse <= borne haute", ib.filter(F.col("ib_lower_bound") > F.col("ib_upper_bound")).count(), 0)
controle("Coherence", "inventory", "quantite entre 0 et 1000", inv.filter(~F.col("inv_quantity_on_hand").between(0, 1000)).count(), 0)
incompletes = inv.filter(~F.col("date_complete")).select("inv_date_sk").distinct().count()
lignes_inc = inv.filter(~F.col("date_complete")).count()
controle("Coherence", "inventory", "toutes les dates d'inventaire sont completes", incompletes, 0,
         remarque=f"{lignes_inc} lignes sur 90 000 pour la derniere date (fichier tronque) ; exclue du Gold")

# Volumes : brut = silver + rejets
for t, v in stats.items():
    controle("Volume", t, "lignes brutes = lignes Silver + lignes rejetees", v["lignes_silver"] + v["lignes_rejetees"], v["lignes_brutes"],
             remarque=f"{v['lignes_brutes']} brutes, {v['lignes_silver']} Silver, {v['lignes_rejetees']} rejetee(s)")

# Integrite referentielle : cles etrangeres vers une table presente
def orphelins(fils, col, parent, cle_parent):
    f = fils.filter(F.col(col).isNotNull()).select(col).distinct()
    return f.join(parent.select(F.col(cle_parent).alias("k")), f[col] == F.col("k"), "left_anti").count()

controle("Integrite", "customer -> customer_address", "c_current_addr_sk existe", orphelins(cust, "c_current_addr_sk", ca, "ca_address_sk"), 0)
controle("Integrite", "customer -> household_demographics", "c_current_hdemo_sk existe", orphelins(cust, "c_current_hdemo_sk", hd, "hd_demo_sk"), 0)
controle("Integrite", "household_demographics -> income_band", "hd_income_band_sk existe", orphelins(hd, "hd_income_band_sk", ib, "ib_income_band_sk"), 0)
controle("Integrite", "customer -> date_dim", "c_first_sales_date_sk existe", orphelins(cust, "c_first_sales_date_sk", dd, "d_date_sk"), 0)
controle("Integrite", "customer -> date_dim", "c_first_shipto_date_sk existe", orphelins(cust, "c_first_shipto_date_sk", dd, "d_date_sk"), 0)
controle("Integrite", "inventory -> date_dim", "inv_date_sk existe", orphelins(inv, "inv_date_sk", dd, "d_date_sk"), 0)
res.append({"famille": "Integrite", "cible": "inventory -> item / warehouse", "regle": "inv_item_sk et inv_warehouse_sk existent",
            "mesure": None, "attendu": 0, "statut": "NON VERIFIABLE", "remarque": "tables item et warehouse absentes du zip"})
res.append({"famille": "Integrite", "cible": "customer -> customer_demographics", "regle": "c_current_cdemo_sk existe",
            "mesure": None, "attendu": 0, "statut": "NON VERIFIABLE", "remarque": "table non traitee au Jour 3 (verifie au Jour 1 : 0 orphelin)"})

# Gold : coherence avec Silver
clients = S("clients_enrichis")
controle("Gold", "clients_enrichis", "une ligne par client (pas de duplication par les jointures)", clients.count(), n_cust)
controle("Gold", "clients_par_etat", "somme des clients = total Silver", G("clients_par_etat").agg(F.sum("nb_clients")).first()[0], n_cust)
controle("Gold", "clients_par_tranche_revenu", "somme des clients = total Silver", G("clients_par_tranche_revenu").agg(F.sum("nb_clients")).first()[0], n_cust)
stock = G("stock_moyen_entrepot_mois")
controle("Gold", "stock_moyen_entrepot_mois", "stock moyen dans [0, 1000]", stock.filter(~F.col("stock_moyen").between(0, 1000)).count(), 0)
controle("Gold", "stock_moyen_entrepot_mois", "lignes d'inventaire du Gold = lignes des dates completes",
         stock.agg(F.sum("nb_lignes")).first()[0], inv.filter(F.col("date_complete")).count())

ko = [r for r in res if r["statut"] == "ANOMALIE"]
print(f"\n{len(res)} controles : {sum(r['statut'] == 'OK' for r in res)} OK, {len(ko)} anomalie(s), "
      f"{sum(r['statut'] == 'NON VERIFIABLE' for r in res)} non verifiable(s)")
sauver_json(res, f"{PREUVES}/qualite/controles_qualite.json")
spark.stop()
