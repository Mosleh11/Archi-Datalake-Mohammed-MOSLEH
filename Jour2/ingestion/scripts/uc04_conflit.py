"""Relance du flux avec un fichier deja present dans HDFS : PutHDFS (strategie fail) doit refuser, le FlowFile va en failure"""
import json, ssl, time, urllib.request, urllib.parse
BASE = "https://localhost:8443/nifi-api"
ctx = ssl._create_unverified_context()
mdp = open("../docker/nifi.env").read().split("PASSWORD=")[1].split()[0]
t = urllib.request.urlopen(urllib.request.Request(BASE + "/access/token", data=urllib.parse.urlencode(
    {"username": "etudiant", "password": mdp}).encode()), context=ctx).read().decode()
ids = json.load(open("../../UC04_preuves/execution/ids.json"))


def api(m, c, b=None):
    r = urllib.request.Request(BASE + c, data=json.dumps(b).encode() if b is not None else None, method=m)
    r.add_header("Content-Type", "application/json"); r.add_header("Authorization", "Bearer " + t)
    return json.loads(urllib.request.urlopen(r, context=ctx).read() or b"{}")


def etat(k, s):
    e = api("GET", f"/processors/{ids[k]}")
    api("PUT", f"/processors/{ids[k]}/run-status", {"revision": e["revision"], "state": s})


for k in ("log", "put", "upd", "get"):
    etat(k, "RUNNING")
time.sleep(25)
for k in ("get", "upd", "put", "log"):
    etat(k, "STOPPED")
d = api("GET", f"/flow/process-groups/{ids['groupe']}/status")["processGroupStatus"]["aggregateSnapshot"]
for p in d["processorStatusSnapshots"]:
    s = p["processorStatusSnapshot"]
    print(s["name"], "entrees", s["flowFilesIn"], "sorties", s["flowFilesOut"])
for c in d["connectionStatusSnapshots"]:
    s = c["connectionStatusSnapshot"]
    print(s["sourceName"], "->", s["destinationName"], "en file d'attente :", s["flowFilesQueued"])
