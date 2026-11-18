"""Bronze (fichiers .dat) -> Silver (Parquet) : typage, nettoyage, mise a l'ecart des lignes invalides"""
from pyspark.sql import functions as F
from commun import *

spark = session("nettoyage")
stats = {}


def typer(brut, table):
    """Trim, vide -> null, conversion de type. Retourne le DataFrame et le nombre d'echecs de conversion par colonne"""
    cols = [c for c, _ in SCHEMA[table]]
    propre = brut.select([F.when(F.trim(F.col(c)) == "", None).otherwise(F.trim(F.col(c))).alias(c) for c, _ in SCHEMA[table]])
    df_type = propre.select([F.col(c).cast(TYPES[t]).alias(c) for c, t in SCHEMA[table]])
    echecs = propre.agg(*[F.sum(F.when(F.col(c).isNotNull() & F.col(c).cast(TYPES[t]).isNull(), 1).otherwise(0)).alias(c)
                          for c, t in SCHEMA[table]]).first().asDict()
    return df_type, {c: int(v or 0) for c, v in echecs.items() if v}


def finir(df, table, brut_n, rejets, regles):
    """Ajoute la provenance, ecrit Silver et les rejets, garde les chiffres pour le rapport"""
    df = df.withColumn("_source", F.lit(f"{table}.dat")).withColumn("_traite_le", F.current_timestamp())
    ecrire_parquet(df, "silver", table)
    nb_rejets = rejets.count()
    if nb_rejets:
        ecrire_parquet(rejets.withColumn("_source", F.lit(f"{table}.dat")), "silver/_rejets", table)
    nb = spark.read.parquet(f"{DATA}/silver/{table}").count()
    stats[table] = {"lignes_brutes": brut_n, "lignes_silver": nb, "lignes_rejetees": nb_rejets, **regles}
    print(f"{table}: brut={brut_n} silver={nb} rejets={nb_rejets} {regles}")


def sans_cle(df, cles):
    cond = F.lit(False)
    for c in cles:
        cond = cond | F.col(c).isNull()
    return cond


# ---------- customer ----------
brut = lire_raw(spark, "customer"); n = brut.count()
df, echecs = typer(brut, "customer")
rejets = df.filter(sans_cle(df, ["c_customer_sk"])).withColumn("motif", F.lit("cle c_customer_sk absente"))
df = df.filter(~sans_cle(df, ["c_customer_sk"]))
avant = df.count(); df = df.dropDuplicates(["c_customer_sk"]); doublons = avant - df.count()
flag_invalide = (~F.col("c_preferred_cust_flag").isin("Y", "N")) & F.col("c_preferred_cust_flag").isNotNull()
nb_flag = df.filter(flag_invalide).count()
nb_annee = df.filter(~F.col("c_birth_year").between(1900, 2025)).count()
df = (df.withColumn("c_preferred_cust_flag", F.when(flag_invalide, None).otherwise(F.col("c_preferred_cust_flag")))
        .withColumn("c_birth_year", F.when(F.col("c_birth_year").between(1900, 2025), F.col("c_birth_year")))
        .withColumn("email_domaine", F.when(F.col("c_email_address").contains("@"), F.regexp_extract("c_email_address", "@(.+)$", 1)))
        .drop("c_first_name", "c_last_name", "c_login", "c_email_address", "c_birth_day", "c_birth_month"))
finir(df, "customer", n, rejets, {"echecs_conversion": echecs, "doublons_supprimes": doublons,
                                   "flag_preferred_invalide": nb_flag, "annee_naissance_hors_plage": nb_annee})

# ---------- customer_address ----------
brut = lire_raw(spark, "customer_address"); n = brut.count()
df, echecs = typer(brut, "customer_address")
rejets = df.filter(sans_cle(df, ["ca_address_sk"])).withColumn("motif", F.lit("cle ca_address_sk absente"))
df = df.filter(~sans_cle(df, ["ca_address_sk"]))
avant = df.count(); df = df.dropDuplicates(["ca_address_sk"]); doublons = avant - df.count()
etat_ko = df.filter(F.col("ca_state").isNotNull() & ~F.col("ca_state").rlike("^[A-Z]{2}$")).count()
zip_ko = df.filter(F.col("ca_zip").isNotNull() & ~F.col("ca_zip").rlike("^[0-9]{5}$")).count()
df = (df.withColumn("ca_state", F.when(F.col("ca_state").rlike("^[A-Z]{2}$"), F.col("ca_state")))
        .withColumn("ca_zip", F.when(F.col("ca_zip").rlike("^[0-9]{5}$"), F.col("ca_zip")))
        .drop("ca_street_number", "ca_street_name", "ca_street_type", "ca_suite_number"))
finir(df, "customer_address", n, rejets, {"echecs_conversion": echecs, "doublons_supprimes": doublons,
                                           "etat_invalide": etat_ko, "zip_invalide": zip_ko})

# ---------- household_demographics ----------
brut = lire_raw(spark, "household_demographics"); n = brut.count()
df, echecs = typer(brut, "household_demographics")
rejets = df.filter(sans_cle(df, ["hd_demo_sk"])).withColumn("motif", F.lit("cle hd_demo_sk absente"))
df = df.filter(~sans_cle(df, ["hd_demo_sk"])).dropDuplicates(["hd_demo_sk"])
neg = df.filter(F.col("hd_vehicle_count") < 0).count()
df = (df.withColumn("vehicle_count_invalide", F.col("hd_vehicle_count") < 0)
        .withColumn("hd_vehicle_count", F.when(F.col("hd_vehicle_count") >= 0, F.col("hd_vehicle_count"))))
finir(df, "household_demographics", n, rejets, {"echecs_conversion": echecs, "vehicle_count_negatif_mis_a_null": neg})

# ---------- income_band ----------
brut = lire_raw(spark, "income_band"); n = brut.count()
df, echecs = typer(brut, "income_band")
rejets = df.filter(sans_cle(df, ["ib_income_band_sk"])).withColumn("motif", F.lit("cle absente"))
df = df.filter(~sans_cle(df, ["ib_income_band_sk"]))
bornes_ko = df.filter(F.col("ib_lower_bound") > F.col("ib_upper_bound")).count()
df = df.withColumn("tranche", F.concat_ws("-", "ib_lower_bound", "ib_upper_bound"))
finir(df, "income_band", n, rejets, {"echecs_conversion": echecs, "bornes_inversees": bornes_ko})

# ---------- date_dim ----------
brut = lire_raw(spark, "date_dim"); n = brut.count()
df, echecs = typer(brut, "date_dim")
rejets = df.filter(sans_cle(df, ["d_date_sk"])).withColumn("motif", F.lit("cle d_date_sk absente"))
df = df.filter(~sans_cle(df, ["d_date_sk"])).dropDuplicates(["d_date_sk"])
df = df.withColumn("d_date", F.to_date("d_date", "yyyy-MM-dd"))
date_ko = df.filter(F.col("d_date").isNull()).count()
annee_incoherente = df.filter(F.col("d_date").isNotNull() & (F.year("d_date") != F.col("d_year"))).count()
finir(df, "date_dim", n, rejets, {"echecs_conversion": echecs, "date_non_convertible": date_ko, "annee_incoherente": annee_incoherente})

# ---------- inventory ----------
brut = lire_raw(spark, "inventory"); n = brut.count()
df, echecs = typer(brut, "inventory")
cles = ["inv_date_sk", "inv_item_sk", "inv_warehouse_sk"]
rejets = df.filter(sans_cle(df, cles)).withColumn("motif", F.lit("ligne incomplete (cle absente) : fin de fichier tronquee"))
df = df.filter(~sans_cle(df, cles))
quantite_nulle = df.filter(F.col("inv_quantity_on_hand").isNull()).count()
negatif = df.filter(F.col("inv_quantity_on_hand") < 0).count()
par_date = df.groupBy("inv_date_sk").agg(F.count("*").alias("lignes_du_jour"))
attendu = par_date.agg(F.max("lignes_du_jour")).first()[0]
par_date = par_date.withColumn("date_complete", F.col("lignes_du_jour") == attendu).select("inv_date_sk", "date_complete")
df = df.join(F.broadcast(par_date), "inv_date_sk", "left")
dates_incompletes = par_date.filter(~F.col("date_complete")).count()
finir(df, "inventory", n, rejets, {"echecs_conversion": echecs, "quantite_nulle_conservee": quantite_nulle, "quantite_negative": negatif,
                                    "lignes_attendues_par_date": attendu, "dates_incompletes": dates_incompletes})

sauver_json(stats, f"{PREUVES}/transformations/nettoyage_stats.json")
spark.stop()
