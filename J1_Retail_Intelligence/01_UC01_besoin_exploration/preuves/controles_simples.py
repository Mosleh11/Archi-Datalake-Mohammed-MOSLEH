"""Quelques contrôles simples sur les données (python controles_simples.py <dossier data>)"""
import os, sys
from collections import Counter

d = sys.argv[1]
SEP = "|"


def lignes(t):
    for nom in os.listdir(os.path.join(d, t)):
        with open(os.path.join(d, t, nom), encoding="utf-8", errors="replace", newline="") as f:
            for l in f:
                if l.endswith("\n"):
                    yield l.rstrip("\r\n").split(SEP)


print("--- fins de ligne")
with open(os.path.join(d, "customer", "customer.dat"), "rb") as f:
    print("customer.dat : CRLF" if b"\r\n" in f.read(2000) else "customer.dat : LF")

print("--- clients par état (customer -> customer_address)")
addr = {c[0]: c[8] for c in lignes("customer_address")}
etat = Counter()
sans = 0
for c in lignes("customer"):
    a = c[4]
    if a == "":
        sans += 1
    else:
        etat[addr[a]] += 1
print("clients sans adresse :", sans)
print("top 5 états :", etat.most_common(5))

print("--- genre dans customer_demographics")
print(Counter(c[1] for c in lignes("customer_demographics")))

print("--- hd_vehicle_count (valeurs distinctes)")
print(Counter(c[4] for c in lignes("household_demographics")))

print("--- clients par tranche de revenu (customer -> household_demographics -> income_band)")
hd = {c[0]: c[1] for c in lignes("household_demographics")}
ib = {c[0]: (c[1], c[2]) for c in lignes("income_band")}
tr = Counter()
for c in lignes("customer"):
    h = c[3]
    if h and hd.get(h):
        tr[ib[hd[h]]] += 1
for k in sorted(tr, key=lambda x: int(x[0]))[:20]:
    print(k, tr[k])

print("--- inventory : lignes et stock moyen par entrepôt")
dates = Counter()
somme = Counter()
nb = Counter()
for c in lignes("inventory"):
    dates[c[0]] += 1
    if c[3] != "":
        somme[c[2]] += int(c[3]); nb[c[2]] += 1
print("lignes par date (min / max) :", min(dates.values()), max(dates.values()))
incompletes = [k for k, v in dates.items() if v != 90000]
print("dates avec moins de 90000 lignes (18000 articles x 5 entrepôts) :", incompletes, [dates[k] for k in incompletes])
for w in sorted(somme):
    print("entrepôt", w, "stock moyen", round(somme[w] / nb[w], 1))
