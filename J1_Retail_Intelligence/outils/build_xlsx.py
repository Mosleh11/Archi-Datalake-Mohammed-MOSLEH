"""Génère dictionnaire_KPI.xlsx et inventaire_sources.xlsx à partir des résultats de analyse_kit.py"""
import json, os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
uc1 = os.path.join(racine, "01_UC01_besoin_exploration")
res = json.load(open(os.path.join(uc1, "preuves", "resultats_analyse.json"), encoding="utf-8"))
schema = json.load(open(os.path.join(uc1, "preuves", "schema_spec_tpcxbb.json"), encoding="utf-8"))


def feuille(wb, titre, entetes, lignes, largeurs):
    ws = wb.create_sheet(titre)
    ws.append(entetes)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="305496")
    for l in lignes:
        ws.append(l)
    for i, w in enumerate(largeurs):
        ws.column_dimensions[chr(65 + i)].width = w
    for row in ws.iter_rows():
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"


def nouveau():
    wb = Workbook()
    wb.remove(wb.active)
    return wb


# ================= KPI =================
E = ["ID", "Nom", "Définition métier", "Formule", "Unité", "Périmètre / granularité", "Fréquence",
     "Sources nécessaires", "Colonnes (DDL spec)", "Données manquantes", "Limites d'interprétation",
     "Calculable avec le zip reçu ?"]
kpi = [
    ["KPI-01", "Chiffre d'affaires", "Montant des ventes de la période, retours traités à part",
     "SUM(ss_ext_sales_price) en magasin ; SUM(ws_ext_sales_price) sur le web",
     "Devise (non précisée dans la spec)", "Par jour/mois, produit, magasin, canal. Retours exclus", "Mensuelle",
     "store_sales, web_sales, date_dim, item, store", "ss_ext_sales_price, ws_ext_sales_price, ss_sold_date_sk, ws_sold_date_sk",
     "Tables de ventes absentes du zip. HT/TTC et remise incluse ou non : à confirmer sur les vraies données",
     "Ne pas additionner magasin et web sans vérifier que le montant a le même sens", "Non (store_sales et web_sales absents)"],
    ["KPI-02", "Nombre de transactions", "Nombre de tickets (magasin) et de commandes (web) distincts",
     "COUNT(DISTINCT ss_ticket_number) ; COUNT(DISTINCT ws_order_number)", "Nombre",
     "Par période, magasin, canal (jamais mélangés)", "Mensuelle", "store_sales, web_sales",
     "ss_ticket_number, ws_order_number", "Tables absentes ; unicité des numéros non vérifiée",
     "Un ticket, une commande, une ligne de vente ne sont pas la même chose", "Non"],
    ["KPI-03", "Panier moyen", "Montant moyen dépensé par transaction",
     "KPI-01 / KPI-02 sur le même périmètre", "Devise / transaction", "Par canal et période", "Mensuelle",
     "store_sales, web_sales", "voir KPI-01 et KPI-02", "Tables absentes",
     "Faux si CA et transactions n'ont pas le même périmètre", "Non"],
    ["KPI-04", "Quantités vendues", "Nombre d'unités vendues",
     "SUM(ss_quantity) ; SUM(ws_quantity)", "Unités", "Par produit, période, magasin, canal", "Mensuelle",
     "store_sales, web_sales, item", "ss_quantity, ws_quantity, ss_item_sk, ws_item_sk", "Tables absentes",
     "Une quantité n'est pas un nombre de lignes", "Non"],
    ["KPI-05", "Évolution des ventes", "Variation du CA entre deux périodes",
     "(CA N - CA N-1) / CA N-1", "%", "Mois sur mois ou année sur année", "Mensuelle",
     "store_sales, web_sales, date_dim", "ss_sold_date_sk, ws_sold_date_sk, d_year, d_moy",
     "Tables de ventes absentes. date_dim existe (1900 à 2199)",
     "Données synthétiques : une tendance observée n'a pas de sens métier réel. Corrélation différente de causalité", "Non (date_dim seule ne suffit pas)"],
    ["KPI-06", "Taux de remise", "Part de remise par rapport au prix de liste",
     "SUM(ss_ext_discount_amt) / SUM(ss_ext_list_price)", "%", "Par produit, magasin, période", "Mensuelle",
     "store_sales, web_sales", "ss_ext_discount_amt, ss_ext_list_price, ws_ext_discount_amt, ws_ext_list_price",
     "Tables absentes ; définition exacte de la remise à confirmer", "Base de calcul (prix de liste) à confirmer", "Non"],
    ["KPI-07", "Taux de retour", "Part des quantités vendues qui sont retournées",
     "SUM(sr_return_quantity) / SUM(ss_quantity) ; idem web avec wr_ et ws_", "%", "Par produit, canal, période", "Mensuelle",
     "store_returns, store_sales, web_returns, web_sales", "sr_return_quantity, sr_ticket_number, wr_return_quantity, wr_order_number",
     "Tables absentes ; lien retour -> vente (ticket + article) non vérifié",
     "La date du retour peut être différente de celle de la vente", "Non"],
    ["KPI-08", "Stock moyen", "Quantité moyenne en stock sur une période",
     "AVG(inv_quantity_on_hand) par entrepôt (ou par article)", "Unités", "Par entrepôt et date (hebdomadaire). Pas de stock par magasin",
     "Hebdomadaire", "inventory, date_dim (+ item, warehouse pour les libellés)", "inv_date_sk, inv_item_sk, inv_warehouse_sk, inv_quantity_on_hand",
     "item et warehouse absents : pas de libellé produit/entrepôt. Dernière semaine incomplète (11 808 lignes sur 90 000)",
     "Valeurs aléatoires entre 0 et 1000 selon la spec (moyenne ~500 par entrepôt) : pas d'interprétation métier", "Oui, partiellement (constaté : ~500 par entrepôt)"],
    ["KPI-09", "Nombre de clients", "Nombre de clients référencés",
     "COUNT(DISTINCT c_customer_sk)", "Nombre", "Global, par état via customer_address", "Mensuelle", "customer, customer_address",
     "c_customer_sk, c_current_addr_sk, ca_state", "22 clients sans adresse", "Ne dit rien sur les clients actifs (aucune vente disponible)",
     "Oui (constaté : 99 000)"],
    ["KPI-10", "Répartition des clients par tranche de revenu", "Nombre de clients par tranche de revenu du foyer",
     "COUNT(c_customer_sk) groupé par ib_lower_bound / ib_upper_bound via household_demographics", "Nombre", "20 tranches", "Ponctuelle",
     "customer, household_demographics, income_band", "c_current_hdemo_sk, hd_income_band_sk, ib_*", "29 clients sans foyer, 2 foyers sans tranche",
     "Répartition quasi uniforme (~5 000 par tranche) : signe de données générées au hasard", "Oui (constaté, voir preuves/controles_simples.txt)"],
]
wb = nouveau()
feuille(wb, "KPI", E, kpi, [8, 22, 30, 38, 14, 28, 12, 28, 34, 36, 38, 22])
wb.save(os.path.join(uc1, "dictionnaire_KPI.xlsx"))

# ================= Inventaire =================
domaine = {"customer": "Clients", "customer_address": "Clients (adresses)", "customer_demographics": "Clients (démographie)",
           "date_dim": "Dates", "household_demographics": "Foyers", "income_band": "Tranches de revenu", "inventory": "Stocks"}
cle = {"customer": "c_customer_sk", "customer_address": "ca_address_sk", "customer_demographics": "cd_demo_sk",
       "date_dim": "d_date_sk", "household_demographics": "hd_demo_sk", "income_band": "ib_income_band_sk",
       "inventory": "(inv_date_sk, inv_item_sk, inv_warehouse_sk)"}
fichiers, colonnes = [], []
for t, v in res.items():
    if t == "jointures":
        continue
    etat = "Tronqué (dernière ligne incomplète)" if v["dernier_ligne_incomplete"] else "Complet"
    fichiers.append([f"{t}.dat", f"retail_project/data/{t}/{t}.dat", "Texte délimité, séparateur |, sans en-tête, fin de ligne CRLF",
                     v["taille_octets"], v["lignes"], len(v["colonnes"]), domaine[t], cle[t], etat])
    for i, c in enumerate(v["colonnes"]):
        n = v["nulls"][i]
        colonnes.append([t, i + 1, c, v["types_spec"][i], n, round(100 * n / v["lignes"], 3),
                         v["min"][i], v["max"][i], "oui" if c == cle[t] else ""])
wb = nouveau()
feuille(wb, "Fichiers", ["Fichier", "Chemin dans le zip", "Format", "Taille (octets)", "Lignes complètes", "Colonnes",
                         "Domaine", "Clé", "État"], fichiers, [28, 42, 40, 16, 16, 10, 22, 36, 30])
feuille(wb, "Colonnes", ["Table", "Position", "Colonne (DDL spec)", "Type (spec)", "Valeurs vides", "% vides", "Min", "Max", "Clé"],
        colonnes, [24, 9, 26, 12, 12, 10, 12, 12, 6])
rel = []
for j in res["jointures"]:
    rel.append([j["source"], j["cible"], j["lignes"], j.get("nulls", ""), j["sans_correspondance"], "Vérifié (0 orphelin)" if j["sans_correspondance"] == 0 else "Anomalie"])
rel += [["inventory.inv_item_sk", "item", "", "", "non testable", "À valider (item absent du zip)"],
        ["inventory.inv_warehouse_sk", "warehouse", "", "", "non testable", "À valider (warehouse absent du zip)"]]
feuille(wb, "Relations", ["Colonne source", "Table cible", "Lignes", "Valeurs vides", "Sans correspondance", "Statut"], rel, [34, 26, 12, 12, 20, 34])

absents = {
    "item": ("Produits", "Quels produits vendent le plus ?"), "store": ("Magasins", "Quels magasins performent ?"),
    "store_sales": ("Ventes magasin", "CA, panier, quantités, remises"), "web_sales": ("Ventes web", "CA et volumes par canal"),
    "store_returns": ("Retours magasin", "Taux de retour"), "web_returns": ("Retours web", "Taux de retour"),
    "warehouse": ("Entrepôts", "Libellé des entrepôts du stock"), "promotion": ("Promotions", "Effet des promotions"),
    "time_dim": ("Heures", "Ventes par tranche horaire"), "web_clickstreams": ("Navigation web", "Comportement des visiteurs"),
    "web_page": ("Pages web", "Navigation par type de page"), "web_site": ("Sites web", "Ventes par site"),
    "ship_mode": ("Modes de livraison", "Analyse logistique"), "reason": ("Motifs de retour", "Motifs de retour"),
    "item_marketprices": ("Prix concurrents", "Veille prix"), "product_reviews": ("Avis produits", "Avis clients (texte)"),
}
ab = []
for t, (dom, q) in absents.items():
    nb = len(schema[t]) if t in schema else ""
    ab.append([t, dom, q, nb, "Cité dans la spec TPCx-BB et dans le projet fil rouge ; absent du zip reçu",
               "Non disponible (zip reçu)"])
feuille(wb, "Absents du zip", ["Table", "Domaine", "Question métier concernée", "Nb colonnes attendues (DDL spec)", "Source de l'information", "Statut"],
        ab, [20, 20, 36, 18, 52, 26])
wb.save(os.path.join(uc1, "inventaire_sources.xlsx"))
print("xlsx ok")
