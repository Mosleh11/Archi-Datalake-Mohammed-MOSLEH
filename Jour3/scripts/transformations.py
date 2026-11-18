"""Silver -> jeux enrichis (jointures verifiees) -> Gold (agregations repondant aux KPI du Jour 1)"""
from pyspark.sql import functions as F
from commun import *

spark = session("transformations")
jointures = []


def cle_unique(df, cle, nom):
    nb, distincts = df.count(), df.select(cle).distinct().count()
    print(f"cle {nom}.{cle} : {nb} lignes, {distincts} valeurs distinctes ->", "unique" if nb == distincts else "NON unique")
    assert nb == distincts, f"{nom}.{cle} n'est pas unique : la jointure dupliquerait des lignes"


def joindre(gauche, droite, cle_g, cle_d, nom_droite, indicateur):
    """Jointure gauche apres verification que la cle de droite est unique ; compte lignes avant/apres et non rapprochees"""
    cle_unique(droite, cle_d, nom_droite)
    avant = gauche.count()
    res = gauche.join(droite, gauche[cle_g] == droite[cle_d], "left")
    apres = res.count()
    sans_cle_g = gauche.filter(F.col(cle_g).isNull()).count()
    non_rapprochees = res.filter(F.col(cle_g).isNotNull() & F.col(indicateur).isNull()).count()
    jointures.append({"gauche": cle_g, "droite": f"{nom_droite}.{cle_d}", "lignes_avant": avant, "lignes_apres": apres,
                      "cle_gauche_nulle": sans_cle_g, "orphelins": non_rapprochees})
    print(jointures[-1])
    return res


customer = lire_parquet(spark, "silver", "customer")
adresse = lire_parquet(spark, "silver", "customer_address").select("ca_address_sk", "ca_city", "ca_county", "ca_state", "ca_zip", "ca_country")
foyer = lire_parquet(spark, "silver", "household_demographics").select("hd_demo_sk", "hd_income_band_sk", "hd_buy_potential", "hd_dep_count", "hd_vehicle_count")
tranche = lire_parquet(spark, "silver", "income_band").select("ib_income_band_sk", "tranche")

# Silver enrichi : un client par ligne
clients = joindre(customer, adresse, "c_current_addr_sk", "ca_address_sk", "customer_address", "ca_address_sk")
clients = joindre(clients, foyer, "c_current_hdemo_sk", "hd_demo_sk", "household_demographics", "hd_demo_sk")
clients = joindre(clients, tranche, "hd_income_band_sk", "ib_income_band_sk", "income_band", "ib_income_band_sk")
clients = clients.drop("ca_address_sk", "hd_demo_sk", "ib_income_band_sk")
ecrire_parquet(clients, "silver", "clients_enrichis")
print("silver/clients_enrichis :", clients.count(), "lignes")

# Gold 1 (KPI-09) : clients par etat
total = clients.count()
par_etat = (clients.groupBy(F.coalesce("ca_state", F.lit("Non renseigne")).alias("etat"))
            .agg(F.count("*").alias("nb_clients"))
            .withColumn("part_pct", F.round(F.col("nb_clients") * 100 / total, 2))
            .orderBy(F.desc("nb_clients")))
ecrire_parquet(par_etat, "gold", "clients_par_etat")
par_etat.show(10, truncate=False)

# Gold 2 (KPI-10) : clients par tranche de revenu du foyer
par_tranche = (clients.groupBy("hd_income_band_sk", F.coalesce("tranche", F.lit("Non renseigne")).alias("tranche"))
               .agg(F.count("*").alias("nb_clients"))
               .withColumn("part_pct", F.round(F.col("nb_clients") * 100 / total, 2))
               .orderBy("hd_income_band_sk"))
ecrire_parquet(par_tranche, "gold", "clients_par_tranche_revenu")
par_tranche.show(25, truncate=False)

# Gold 3 (KPI-08) : stock moyen par entrepot et par mois (semaines completes seulement)
inventaire = lire_parquet(spark, "silver", "inventory")
dates = lire_parquet(spark, "silver", "date_dim").select("d_date_sk", "d_year", "d_moy")
cle_unique(dates, "d_date_sk", "date_dim")
avant = inventaire.count()
inv_dates = inventaire.join(F.broadcast(dates), inventaire["inv_date_sk"] == dates["d_date_sk"], "left")
orphelins = inv_dates.filter(F.col("d_date_sk").isNull()).count()
jointures.append({"gauche": "inventory.inv_date_sk", "droite": "date_dim.d_date_sk", "lignes_avant": avant,
                  "lignes_apres": inv_dates.count(), "cle_gauche_nulle": 0, "orphelins": orphelins})
print(jointures[-1])
stock = (inv_dates.filter(F.col("date_complete"))
         .groupBy("inv_warehouse_sk", "d_year", "d_moy")
         .agg(F.round(F.avg("inv_quantity_on_hand"), 2).alias("stock_moyen"),
              F.countDistinct("inv_date_sk").alias("nb_dates"),
              F.count("*").alias("nb_lignes"),
              F.sum(F.when(F.col("inv_quantity_on_hand").isNull(), 1).otherwise(0)).alias("nb_quantites_nulles"))
         .orderBy("inv_warehouse_sk", "d_year", "d_moy"))
ecrire_parquet(stock, "gold", "stock_moyen_entrepot_mois")
stock.show(12, truncate=False)
print("gold/stock_moyen_entrepot_mois :", stock.count(), "lignes")

sauver_json(jointures, f"{PREUVES}/transformations/jointures.json")
spark.stop()
