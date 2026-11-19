"""Genere notebooks/analyses_kpi.ipynb (non execute) ; l'execution se fait avec scripts/lancer_notebook.sh"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md("# TP4 – Analyse des données Retail Intelligence (UC-08)\n\nObjectif : calculer des KPI du dictionnaire du Jour 1, produire des statistiques descriptives, deux analyses métier et des graphiques, "
       "à partir des jeux **Silver et Gold produits au Jour 3**. Les calculs sont faits avec PySpark ; seuls de petits tableaux agrégés passent dans pandas pour Matplotlib.\n\n"
       "Les tables de ventes ne sont pas dans le kit reçu : seuls KPI-08, KPI-09 et KPI-10 sont calculables. Les données sont synthétiques."),
    md("## 1. Environnement et session Spark"),
    code("import os, platform, subprocess\nimport pyspark, pandas as pd, matplotlib\nimport matplotlib.pyplot as plt\nfrom pathlib import Path\nfrom pyspark.sql import SparkSession, functions as F\n\n"
         "DATA = os.environ.get('DATA_DIR', '/j3/data')\nOUT, VIS = Path('../preuves/uc08/resultats'), Path('../visualisations')\nOUT.mkdir(parents=True, exist_ok=True); VIS.mkdir(exist_ok=True)\n\n"
         "print('Python :', platform.python_version())\nprint('PySpark :', pyspark.__version__)\nprint('pandas :', pd.__version__)\nprint('Matplotlib :', matplotlib.__version__)\n"
         "print(subprocess.run(['java', '-version'], capture_output=True, text=True).stderr.splitlines()[0])\n"
         "spark = (SparkSession.builder.appName('TP4-Retail-Intelligence').master('local[4]')\n"
         "         .config('spark.driver.memory', '4g').config('spark.sql.shuffle.partitions', '8')\n"
         "         .config('spark.ui.showConsoleProgress', 'false').getOrCreate())\nspark.sparkContext.setLogLevel('ERROR')\n"
         "print('Spark :', spark.version, '| mode :', spark.sparkContext.master)\nprint('Données lues dans :', DATA)"),
    md("## 2. Chargement et inventaire des jeux utilisés\n\nSchéma, volume et granularité de chaque jeu avant tout calcul."),
    code("jeux = {\n"
         "    ('silver', 'clients_enrichis'): 'un client',\n"
         "    ('silver', 'inventory'): 'une date, un article, un entrepôt',\n"
         "    ('silver', 'date_dim'): 'un jour',\n"
         "    ('gold', 'clients_par_etat'): 'un état',\n"
         "    ('gold', 'clients_par_tranche_revenu'): 'une tranche de revenu',\n"
         "    ('gold', 'stock_moyen_entrepot_mois'): 'un entrepôt et un mois',\n"
         "}\ndf = {}\ninventaire = []\nfor (zone, nom), grain in jeux.items():\n"
         "    d = spark.read.parquet(f'{DATA}/{zone}/{nom}')\n    df[nom] = d\n"
         "    inventaire.append({'jeu': nom, 'zone': zone, 'format': 'Parquet', 'granularite': grain, 'lignes': d.count(), 'colonnes': len(d.columns)})\n"
         "    print('=====', zone, '/', nom, '=====')\n    d.printSchema()\n"
         "pd.DataFrame(inventaire).to_csv(OUT / 'inventaire_jeux.csv', index=False)\npd.DataFrame(inventaire)"),
    md("## 3. Vérification de la granularité et de la cohérence\n\nUne ligne par client, un état par ligne, un entrepôt et un mois par ligne ; les totaux du Gold doivent retrouver ceux du Silver."),
    code("clients, inv, dates = df['clients_enrichis'], df['inventory'], df['date_dim']\n"
         "g_etat, g_tranche, g_stock = df['clients_par_etat'], df['clients_par_tranche_revenu'], df['stock_moyen_entrepot_mois']\n\n"
         "n_clients = clients.count()\n"
         "controles = [\n"
         "    ('clients_enrichis : c_customer_sk unique', n_clients == clients.select('c_customer_sk').distinct().count()),\n"
         "    ('clients_par_etat : un état par ligne', g_etat.count() == g_etat.select('etat').distinct().count()),\n"
         "    ('clients_par_etat : somme = nb de clients', g_etat.agg(F.sum('nb_clients')).first()[0] == n_clients),\n"
         "    ('clients_par_tranche_revenu : somme = nb de clients', g_tranche.agg(F.sum('nb_clients')).first()[0] == n_clients),\n"
         "    ('stock_moyen_entrepot_mois : un entrepôt et un mois par ligne', g_stock.count() == g_stock.select('inv_warehouse_sk', 'd_year', 'd_moy').distinct().count()),\n"
         "]\nfor texte, ok in controles:\n    print('OK ' if ok else 'ECHEC', texte)\nassert all(ok for _, ok in controles)"),
    md("## 4. KPI calculés\n\nDéfinitions : dictionnaire des KPI du Jour 1 (voir `docs`/rapport). **KPI-09** nombre de clients, **KPI-10** répartition par tranche de revenu du foyer, **KPI-08** stock moyen par entrepôt."),
    code("# KPI-09 : nombre de clients (distincts) et clients sans adresse\n"
         "kpi09 = clients.select(F.countDistinct('c_customer_sk')).first()[0]\n"
         "sans_adresse = clients.filter(F.col('ca_state').isNull()).count()\n"
         "print('KPI-09 clients :', kpi09, '| sans adresse :', sans_adresse)\n\n"
         "# KPI-10 : tranche la plus et la moins peuplée (hors non renseigné)\n"
         "t = g_tranche.filter(F.col('hd_income_band_sk').isNotNull()).toPandas()\n"
         "haut, bas = t.loc[t['nb_clients'].idxmax()], t.loc[t['nb_clients'].idxmin()]\n"
         "print('KPI-10 tranche la plus peuplée :', haut['tranche'], haut['nb_clients'], '| la moins peuplée :', bas['tranche'], bas['nb_clients'])\n\n"
         "# KPI-08 : stock moyen = moyenne de inv_quantity_on_hand (lignes non nulles, dates complètes), recalculé depuis le Silver\n"
         "inv_ok = inv.filter(F.col('date_complete'))\n"
         "stock_global = inv_ok.agg(F.avg('inv_quantity_on_hand')).first()[0]\n"
         "stock_ent = inv_ok.groupBy('inv_warehouse_sk').agg(F.avg('inv_quantity_on_hand').alias('stock_moyen')).orderBy('inv_warehouse_sk').toPandas()\n"
         "print('KPI-08 stock moyen global :', round(stock_global, 2))\nprint(stock_ent)\n\n"
         "# contrôle croisé : moyenne pondérée du Gold = valeur recalculée depuis le Silver\n"
         "g = g_stock.agg((F.sum(F.col('stock_moyen') * (F.col('nb_lignes') - F.col('nb_quantites_nulles'))) / F.sum(F.col('nb_lignes') - F.col('nb_quantites_nulles'))).alias('m')).first()['m']\n"
         "print('Moyenne pondérée du Gold :', round(g, 2), '| écart avec le Silver :', round(abs(g - stock_global), 4))\n\n"
         "kpi = pd.DataFrame([\n"
         "    ['KPI-09', 'Nombre de clients', kpi09, 'clients', 'global, clients_enrichis (Silver)'],\n"
         "    ['KPI-09', 'Clients sans adresse', sans_adresse, 'clients', 'ca_state vide'],\n"
         "    ['KPI-10', 'Tranche de revenu la plus peuplée : ' + haut['tranche'], int(haut['nb_clients']), 'clients', '20 tranches, hors non renseigné'],\n"
         "    ['KPI-10', 'Tranche de revenu la moins peuplée : ' + bas['tranche'], int(bas['nb_clients']), 'clients', '20 tranches, hors non renseigné'],\n"
         "    ['KPI-08', 'Stock moyen (tous entrepôts)', round(stock_global, 2), 'unités', 'inventory Silver, dates complètes'],\n"
         "] + [['KPI-08', f'Stock moyen entrepôt {int(r.inv_warehouse_sk)}', round(r.stock_moyen, 2), 'unités', 'inventory Silver, dates complètes'] for r in stock_ent.itertuples()],\n"
         "    columns=['kpi', 'nom', 'valeur', 'unite', 'perimetre'], dtype=object)\nkpi.to_csv(OUT / 'kpi.csv', index=False)\nkpi"),
    md("## 5. Statistiques descriptives\n\nMesures numériques : année de naissance, nombre de personnes à charge et de véhicules du foyer (clients), quantité en stock (inventory). "
       "Compteurs et sommes via Spark ; médiane approchée (`percentile_approx`)."),
    code("def stats(d, colonnes, jeu):\n"
         "    lignes = []\n    for c in colonnes:\n"
         "        r = d.agg(F.count(c).alias('n'), F.sum(F.col(c).isNull().cast('int')).alias('nuls'), F.min(c).alias('min'), F.max(c).alias('max'),\n"
         "                  F.avg(c).alias('moyenne'), F.percentile_approx(c, 0.5).alias('mediane'), F.stddev(c).alias('ecart_type')).first()\n"
         "        lignes.append({'jeu': jeu, 'colonne': c, 'valeurs': r['n'], 'manquantes': r['nuls'], 'min': r['min'], 'max': r['max'],\n"
         "                       'moyenne': round(r['moyenne'], 2), 'mediane': r['mediane'], 'ecart_type': round(r['ecart_type'], 2)})\n"
         "    return lignes\n\n"
         "st = stats(clients, ['c_birth_year', 'hd_dep_count', 'hd_vehicle_count'], 'clients_enrichis') + stats(inv_ok, ['inv_quantity_on_hand'], 'inventory (dates complètes)')\n"
         "pdf_stats = pd.DataFrame(st)\npdf_stats.to_csv(OUT / 'statistiques.csv', index=False)\npdf_stats"),
    code("# répartitions par catégorie (variables qualitatives des clients)\n"
         "rep = []\nfor c in ['c_preferred_cust_flag', 'hd_buy_potential', 'c_salutation']:\n"
         "    p = clients.groupBy(F.coalesce(F.col(c).cast('string'), F.lit('Non renseigné')).alias('valeur')).count().orderBy(F.desc('count')).toPandas()\n"
         "    p.insert(0, 'colonne', c)\n    p['part_pct'] = (100 * p['count'] / n_clients).round(2)\n    rep.append(p)\n"
         "repartitions = pd.concat(rep)\nrepartitions.rename(columns={'count': 'nb_clients'}).to_csv(OUT / 'repartitions.csv', index=False)\nrepartitions"),
    md("## 6. Analyse 1 – Comment évolue le stock moyen dans le temps ? (KPI-08)\n\nSource : `gold/stock_moyen_entrepot_mois` (5 entrepôts × 56 mois). Un point par entrepôt et par mois."),
    code("ts = g_stock.orderBy('d_year', 'd_moy').toPandas()\n"
         "ts['mois'] = ts['d_year'].astype(str) + '-' + ts['d_moy'].astype(str).str.zfill(2)\n"
         "print(ts['mois'].min(), '->', ts['mois'].max(), '|', ts['mois'].nunique(), 'mois |', ts['inv_warehouse_sk'].nunique(), 'entrepôts')\n"
         "print(ts.groupby('inv_warehouse_sk')['stock_moyen'].agg(['min', 'max', 'mean']).round(1))\n"
         "ts[['inv_warehouse_sk', 'mois', 'stock_moyen', 'nb_dates', 'nb_lignes']].to_csv(OUT / 'stock_moyen_mensuel.csv', index=False)\n\n"
         "plt.figure(figsize=(11, 5))\n"
         "for e, g in ts.groupby('inv_warehouse_sk'):\n    plt.plot(g['mois'], g['stock_moyen'], label=f'Entrepôt {e}', linewidth=1.3)\n"
         "plt.title('Stock moyen mensuel par entrepôt (jan. 2001 - août 2005)')\nplt.xlabel('Mois')\nplt.ylabel('Quantité moyenne en stock (unités)')\n"
         "plt.xticks(range(0, ts['mois'].nunique(), 6), sorted(ts['mois'].unique())[::6], rotation=45)\nplt.grid(True, alpha=0.3)\nplt.ylim(0, 600)\nplt.legend()\n"
         "plt.figtext(0.01, -0.02, 'Source : gold/stock_moyen_entrepot_mois (TPCx-BB, données synthétiques)', fontsize=8)\nplt.tight_layout()\n"
         "plt.savefig(VIS / 'stock_moyen_mensuel.png', dpi=150, bbox_inches='tight')\nplt.show()"),
    md("## 7. Analyse 2 – Où sont les clients ? (KPI-09)\n\nSource : `gold/clients_par_etat` (52 lignes dont « Non renseigné »). Graphique limité aux 10 premiers états (filtre documenté)."),
    code("etat = g_etat.orderBy(F.desc('nb_clients')).toPandas()\n"
         "top = etat.head(10)\n"
         "print(top)\nprint('Part des 10 premiers états :', round(top['part_pct'].sum(), 2), '% | nombre d états au total :', len(etat))\n"
         "print('Etat le plus petit :', etat.iloc[-1].to_dict())\n"
         "etat.to_csv(OUT / 'clients_par_etat.csv', index=False)\n\n"
         "plt.figure(figsize=(10, 5))\nplt.bar(top['etat'], top['nb_clients'], color='#305496')\n"
         "for i, v in enumerate(top['nb_clients']):\n    plt.text(i, v + 80, f'{v:,}'.replace(',', ' '), ha='center', fontsize=8)\n"
         "plt.title('Nombre de clients par état (10 premiers états)')\nplt.xlabel('État')\nplt.ylabel('Nombre de clients')\n"
         "plt.figtext(0.01, -0.02, 'Source : gold/clients_par_etat (TPCx-BB, données synthétiques) – 99 000 clients, adresse courante', fontsize=8)\nplt.tight_layout()\n"
         "plt.savefig(VIS / 'clients_par_etat.png', dpi=150, bbox_inches='tight')\nplt.show()"),
    md("## 8. Analyse 3 – Comment les clients se répartissent-ils par tranche de revenu ? (KPI-10)\n\nSource : `gold/clients_par_tranche_revenu` (20 tranches de 10 000 + « Non renseigné »)."),
    code("tr = g_tranche.filter(F.col('hd_income_band_sk').isNotNull()).orderBy('hd_income_band_sk').toPandas()\n"
         "moy = tr['nb_clients'].mean()\nprint(tr[['tranche', 'nb_clients', 'part_pct']])\n"
         "print('Moyenne par tranche :', round(moy, 1), '| écart min-max :', tr['nb_clients'].min(), '-', tr['nb_clients'].max(),\n"
         "      '| rapport max/min :', round(tr['nb_clients'].max() / tr['nb_clients'].min(), 2))\n"
         "tr.to_csv(OUT / 'clients_par_tranche_revenu.csv', index=False)\n\n"
         "plt.figure(figsize=(11, 5))\nplt.bar(tr['tranche'], tr['nb_clients'], color='#548235')\n"
         "plt.axhline(moy, color='#C00000', linestyle='--', label=f'Moyenne : {moy:,.0f}'.replace(',', ' '))\n"
         "plt.title('Nombre de clients par tranche de revenu du foyer')\nplt.xlabel('Tranche de revenu (unité monétaire non précisée par la spec)')\nplt.ylabel('Nombre de clients')\n"
         "plt.xticks(rotation=60, ha='right')\nplt.legend()\n"
         "plt.figtext(0.01, -0.06, 'Source : gold/clients_par_tranche_revenu (TPCx-BB, données synthétiques) – 60 clients sans tranche non affichés', fontsize=8)\nplt.tight_layout()\n"
         "plt.savefig(VIS / 'clients_par_tranche_revenu.png', dpi=150, bbox_inches='tight')\nplt.show()"),
    md("## 9. Distribution de l'année de naissance des clients\n\nHistogramme construit à partir d'un comptage par année calculé par Spark (une ligne par année)."),
    code("naiss = clients.filter(F.col('c_birth_year').isNotNull()).groupBy('c_birth_year').count().orderBy('c_birth_year').toPandas()\n"
         "print(len(naiss), 'années distinctes,', naiss['c_birth_year'].min(), '->', naiss['c_birth_year'].max())\n"
         "print('Nombre de clients par année : min', naiss['count'].min(), '| max', naiss['count'].max(), '| moyenne', round(naiss['count'].mean(), 1))\n"
         "naiss.rename(columns={'count': 'nb_clients'}).to_csv(OUT / 'distribution_annee_naissance.csv', index=False)\n\n"
         "plt.figure(figsize=(10, 5))\nplt.bar(naiss['c_birth_year'], naiss['count'], width=0.9, color='#7F6000')\n"
         "plt.title('Distribution des clients par année de naissance')\nplt.xlabel('Année de naissance')\nplt.ylabel('Nombre de clients')\nplt.grid(True, axis='y', alpha=0.3)\n"
         "plt.figtext(0.01, -0.02, 'Source : silver/clients_enrichis (TPCx-BB, données synthétiques) – 30 clients sans année de naissance non affichés', fontsize=8)\nplt.tight_layout()\n"
         "plt.savefig(VIS / 'distribution_annee_naissance.png', dpi=150, bbox_inches='tight')\nplt.show()"),
    md("## 10. Ce qui n'a pas pu être calculé\n\n"
       "Les tables `store_sales`, `web_sales`, `store_returns`, `web_returns`, `item` et `store` ne sont pas dans le zip reçu : KPI-01 à KPI-07 ne sont pas calculables. "
       "Aucun graphique `ventes_par_magasin` ni `evolution_ventes_mensuelles` n'est produit. Les interprétations et les recommandations sont dans le rapport `UC08_analyses_visualisations.pdf`."),
]
nbf.write(nb, "../notebooks/analyses_kpi.ipynb")

# meme analyse sous forme de script : cellules de code mises bout a bout, sans affichage interactif
import re
corps = ['"""Analyses KPI du TP4 (meme code que notebooks/analyses_kpi.ipynb) ; a lancer depuis scripts/ : python analyses.py"""', "import matplotlib" + chr(10) + "matplotlib.use('Agg')"]
for c in nb.cells:
    if c.cell_type != "code":
        continue
    lignes = c.source.split(chr(10))
    if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*|pd\.DataFrame\(inventaire\)", lignes[-1]):
        lignes[-1] = f"print({lignes[-1]})"
    corps.append(chr(10).join(lignes).replace("plt.show()", "plt.close()"))
open("../scripts/analyses.py", "w", encoding="utf-8").write((chr(10) * 2).join(corps) + chr(10))
print("notebook cree :", len(nb.cells), "cellules")
