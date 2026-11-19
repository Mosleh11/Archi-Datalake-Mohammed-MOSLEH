"""Analyses KPI du TP4 (meme code que notebooks/analyses_kpi.ipynb) ; a lancer depuis scripts/ : python analyses.py"""

import matplotlib
matplotlib.use('Agg')

import os, platform, subprocess
import pyspark, pandas as pd, matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
from pyspark.sql import SparkSession, functions as F

DATA = os.environ.get('DATA_DIR', '/j3/data')
OUT, VIS = Path('../preuves/uc08/resultats'), Path('../visualisations')
OUT.mkdir(parents=True, exist_ok=True); VIS.mkdir(exist_ok=True)

print('Python :', platform.python_version())
print('PySpark :', pyspark.__version__)
print('pandas :', pd.__version__)
print('Matplotlib :', matplotlib.__version__)
print(subprocess.run(['java', '-version'], capture_output=True, text=True).stderr.splitlines()[0])
spark = (SparkSession.builder.appName('TP4-Retail-Intelligence').master('local[4]')
         .config('spark.driver.memory', '4g').config('spark.sql.shuffle.partitions', '8')
         .config('spark.ui.showConsoleProgress', 'false').getOrCreate())
spark.sparkContext.setLogLevel('ERROR')
print('Spark :', spark.version, '| mode :', spark.sparkContext.master)
print('Données lues dans :', DATA)

jeux = {
    ('silver', 'clients_enrichis'): 'un client',
    ('silver', 'inventory'): 'une date, un article, un entrepôt',
    ('silver', 'date_dim'): 'un jour',
    ('gold', 'clients_par_etat'): 'un état',
    ('gold', 'clients_par_tranche_revenu'): 'une tranche de revenu',
    ('gold', 'stock_moyen_entrepot_mois'): 'un entrepôt et un mois',
}
df = {}
inventaire = []
for (zone, nom), grain in jeux.items():
    d = spark.read.parquet(f'{DATA}/{zone}/{nom}')
    df[nom] = d
    inventaire.append({'jeu': nom, 'zone': zone, 'format': 'Parquet', 'granularite': grain, 'lignes': d.count(), 'colonnes': len(d.columns)})
    print('=====', zone, '/', nom, '=====')
    d.printSchema()
pd.DataFrame(inventaire).to_csv(OUT / 'inventaire_jeux.csv', index=False)
print(pd.DataFrame(inventaire))

clients, inv, dates = df['clients_enrichis'], df['inventory'], df['date_dim']
g_etat, g_tranche, g_stock = df['clients_par_etat'], df['clients_par_tranche_revenu'], df['stock_moyen_entrepot_mois']

n_clients = clients.count()
controles = [
    ('clients_enrichis : c_customer_sk unique', n_clients == clients.select('c_customer_sk').distinct().count()),
    ('clients_par_etat : un état par ligne', g_etat.count() == g_etat.select('etat').distinct().count()),
    ('clients_par_etat : somme = nb de clients', g_etat.agg(F.sum('nb_clients')).first()[0] == n_clients),
    ('clients_par_tranche_revenu : somme = nb de clients', g_tranche.agg(F.sum('nb_clients')).first()[0] == n_clients),
    ('stock_moyen_entrepot_mois : un entrepôt et un mois par ligne', g_stock.count() == g_stock.select('inv_warehouse_sk', 'd_year', 'd_moy').distinct().count()),
]
for texte, ok in controles:
    print('OK ' if ok else 'ECHEC', texte)
assert all(ok for _, ok in controles)

# KPI-09 : nombre de clients (distincts) et clients sans adresse
kpi09 = clients.select(F.countDistinct('c_customer_sk')).first()[0]
sans_adresse = clients.filter(F.col('ca_state').isNull()).count()
print('KPI-09 clients :', kpi09, '| sans adresse :', sans_adresse)

# KPI-10 : tranche la plus et la moins peuplée (hors non renseigné)
t = g_tranche.filter(F.col('hd_income_band_sk').isNotNull()).toPandas()
haut, bas = t.loc[t['nb_clients'].idxmax()], t.loc[t['nb_clients'].idxmin()]
print('KPI-10 tranche la plus peuplée :', haut['tranche'], haut['nb_clients'], '| la moins peuplée :', bas['tranche'], bas['nb_clients'])

# KPI-08 : stock moyen = moyenne de inv_quantity_on_hand (lignes non nulles, dates complètes), recalculé depuis le Silver
inv_ok = inv.filter(F.col('date_complete'))
stock_global = inv_ok.agg(F.avg('inv_quantity_on_hand')).first()[0]
stock_ent = inv_ok.groupBy('inv_warehouse_sk').agg(F.avg('inv_quantity_on_hand').alias('stock_moyen')).orderBy('inv_warehouse_sk').toPandas()
print('KPI-08 stock moyen global :', round(stock_global, 2))
print(stock_ent)

# contrôle croisé : moyenne pondérée du Gold = valeur recalculée depuis le Silver
g = g_stock.agg((F.sum(F.col('stock_moyen') * (F.col('nb_lignes') - F.col('nb_quantites_nulles'))) / F.sum(F.col('nb_lignes') - F.col('nb_quantites_nulles'))).alias('m')).first()['m']
print('Moyenne pondérée du Gold :', round(g, 2), '| écart avec le Silver :', round(abs(g - stock_global), 4))

kpi = pd.DataFrame([
    ['KPI-09', 'Nombre de clients', kpi09, 'clients', 'global, clients_enrichis (Silver)'],
    ['KPI-09', 'Clients sans adresse', sans_adresse, 'clients', 'ca_state vide'],
    ['KPI-10', 'Tranche de revenu la plus peuplée : ' + haut['tranche'], int(haut['nb_clients']), 'clients', '20 tranches, hors non renseigné'],
    ['KPI-10', 'Tranche de revenu la moins peuplée : ' + bas['tranche'], int(bas['nb_clients']), 'clients', '20 tranches, hors non renseigné'],
    ['KPI-08', 'Stock moyen (tous entrepôts)', round(stock_global, 2), 'unités', 'inventory Silver, dates complètes'],
] + [['KPI-08', f'Stock moyen entrepôt {int(r.inv_warehouse_sk)}', round(r.stock_moyen, 2), 'unités', 'inventory Silver, dates complètes'] for r in stock_ent.itertuples()],
    columns=['kpi', 'nom', 'valeur', 'unite', 'perimetre'], dtype=object)
kpi.to_csv(OUT / 'kpi.csv', index=False)
print(kpi)

def stats(d, colonnes, jeu):
    lignes = []
    for c in colonnes:
        r = d.agg(F.count(c).alias('n'), F.sum(F.col(c).isNull().cast('int')).alias('nuls'), F.min(c).alias('min'), F.max(c).alias('max'),
                  F.avg(c).alias('moyenne'), F.percentile_approx(c, 0.5).alias('mediane'), F.stddev(c).alias('ecart_type')).first()
        lignes.append({'jeu': jeu, 'colonne': c, 'valeurs': r['n'], 'manquantes': r['nuls'], 'min': r['min'], 'max': r['max'],
                       'moyenne': round(r['moyenne'], 2), 'mediane': r['mediane'], 'ecart_type': round(r['ecart_type'], 2)})
    return lignes

st = stats(clients, ['c_birth_year', 'hd_dep_count', 'hd_vehicle_count'], 'clients_enrichis') + stats(inv_ok, ['inv_quantity_on_hand'], 'inventory (dates complètes)')
pdf_stats = pd.DataFrame(st)
pdf_stats.to_csv(OUT / 'statistiques.csv', index=False)
print(pdf_stats)

# répartitions par catégorie (variables qualitatives des clients)
rep = []
for c in ['c_preferred_cust_flag', 'hd_buy_potential', 'c_salutation']:
    p = clients.groupBy(F.coalesce(F.col(c).cast('string'), F.lit('Non renseigné')).alias('valeur')).count().orderBy(F.desc('count')).toPandas()
    p.insert(0, 'colonne', c)
    p['part_pct'] = (100 * p['count'] / n_clients).round(2)
    rep.append(p)
repartitions = pd.concat(rep)
repartitions.rename(columns={'count': 'nb_clients'}).to_csv(OUT / 'repartitions.csv', index=False)
print(repartitions)

ts = g_stock.orderBy('d_year', 'd_moy').toPandas()
ts['mois'] = ts['d_year'].astype(str) + '-' + ts['d_moy'].astype(str).str.zfill(2)
print(ts['mois'].min(), '->', ts['mois'].max(), '|', ts['mois'].nunique(), 'mois |', ts['inv_warehouse_sk'].nunique(), 'entrepôts')
print(ts.groupby('inv_warehouse_sk')['stock_moyen'].agg(['min', 'max', 'mean']).round(1))
ts[['inv_warehouse_sk', 'mois', 'stock_moyen', 'nb_dates', 'nb_lignes']].to_csv(OUT / 'stock_moyen_mensuel.csv', index=False)

plt.figure(figsize=(11, 5))
for e, g in ts.groupby('inv_warehouse_sk'):
    plt.plot(g['mois'], g['stock_moyen'], label=f'Entrepôt {e}', linewidth=1.3)
plt.title('Stock moyen mensuel par entrepôt (jan. 2001 - août 2005)')
plt.xlabel('Mois')
plt.ylabel('Quantité moyenne en stock (unités)')
plt.xticks(range(0, ts['mois'].nunique(), 6), sorted(ts['mois'].unique())[::6], rotation=45)
plt.grid(True, alpha=0.3)
plt.ylim(0, 600)
plt.legend()
plt.figtext(0.01, -0.02, 'Source : gold/stock_moyen_entrepot_mois (TPCx-BB, données synthétiques)', fontsize=8)
plt.tight_layout()
plt.savefig(VIS / 'stock_moyen_mensuel.png', dpi=150, bbox_inches='tight')
plt.close()

etat = g_etat.orderBy(F.desc('nb_clients')).toPandas()
top = etat.head(10)
print(top)
print('Part des 10 premiers états :', round(top['part_pct'].sum(), 2), '% | nombre d états au total :', len(etat))
print('Etat le plus petit :', etat.iloc[-1].to_dict())
etat.to_csv(OUT / 'clients_par_etat.csv', index=False)

plt.figure(figsize=(10, 5))
plt.bar(top['etat'], top['nb_clients'], color='#305496')
for i, v in enumerate(top['nb_clients']):
    plt.text(i, v + 80, f'{v:,}'.replace(',', ' '), ha='center', fontsize=8)
plt.title('Nombre de clients par état (10 premiers états)')
plt.xlabel('État')
plt.ylabel('Nombre de clients')
plt.figtext(0.01, -0.02, 'Source : gold/clients_par_etat (TPCx-BB, données synthétiques) – 99 000 clients, adresse courante', fontsize=8)
plt.tight_layout()
plt.savefig(VIS / 'clients_par_etat.png', dpi=150, bbox_inches='tight')
plt.close()

tr = g_tranche.filter(F.col('hd_income_band_sk').isNotNull()).orderBy('hd_income_band_sk').toPandas()
moy = tr['nb_clients'].mean()
print(tr[['tranche', 'nb_clients', 'part_pct']])
print('Moyenne par tranche :', round(moy, 1), '| écart min-max :', tr['nb_clients'].min(), '-', tr['nb_clients'].max(),
      '| rapport max/min :', round(tr['nb_clients'].max() / tr['nb_clients'].min(), 2))
tr.to_csv(OUT / 'clients_par_tranche_revenu.csv', index=False)

plt.figure(figsize=(11, 5))
plt.bar(tr['tranche'], tr['nb_clients'], color='#548235')
plt.axhline(moy, color='#C00000', linestyle='--', label=f'Moyenne : {moy:,.0f}'.replace(',', ' '))
plt.title('Nombre de clients par tranche de revenu du foyer')
plt.xlabel('Tranche de revenu (unité monétaire non précisée par la spec)')
plt.ylabel('Nombre de clients')
plt.xticks(rotation=60, ha='right')
plt.legend()
plt.figtext(0.01, -0.06, 'Source : gold/clients_par_tranche_revenu (TPCx-BB, données synthétiques) – 60 clients sans tranche non affichés', fontsize=8)
plt.tight_layout()
plt.savefig(VIS / 'clients_par_tranche_revenu.png', dpi=150, bbox_inches='tight')
plt.close()

naiss = clients.filter(F.col('c_birth_year').isNotNull()).groupBy('c_birth_year').count().orderBy('c_birth_year').toPandas()
print(len(naiss), 'années distinctes,', naiss['c_birth_year'].min(), '->', naiss['c_birth_year'].max())
print('Nombre de clients par année : min', naiss['count'].min(), '| max', naiss['count'].max(), '| moyenne', round(naiss['count'].mean(), 1))
naiss.rename(columns={'count': 'nb_clients'}).to_csv(OUT / 'distribution_annee_naissance.csv', index=False)

plt.figure(figsize=(10, 5))
plt.bar(naiss['c_birth_year'], naiss['count'], width=0.9, color='#7F6000')
plt.title('Distribution des clients par année de naissance')
plt.xlabel('Année de naissance')
plt.ylabel('Nombre de clients')
plt.grid(True, axis='y', alpha=0.3)
plt.figtext(0.01, -0.02, 'Source : silver/clients_enrichis (TPCx-BB, données synthétiques) – 30 clients sans année de naissance non affichés', fontsize=8)
plt.tight_layout()
plt.savefig(VIS / 'distribution_annee_naissance.png', dpi=150, bbox_inches='tight')
plt.close()
