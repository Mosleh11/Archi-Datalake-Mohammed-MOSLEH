"""Lance le flux cree par uc04_nifi.py, releve compteurs, provenance et export du flux"""
import json, ssl, sys, time, urllib.request, urllib.parse
BASE = "https://localhost:8443/nifi-api"
ctx = ssl._create_unverified_context()
sortie = sys.argv[1]
mdp = open("../docker/nifi.env").read().split("PASSWORD=")[1].split()[0]
token = urllib.request.urlopen(urllib.request.Request(BASE + "/access/token", data=urllib.parse.urlencode(
    {"username": "etudiant", "password": mdp}).encode()), context=ctx).read().decode()
ids = json.load(open(sortie + "/ids.json"))


def api(m, c, corps=None):
    r = urllib.request.Request(BASE + c, data=json.dumps(corps).encode() if corps is not None else None, method=m)
    r.add_header("Content-Type", "application/json"); r.add_header("Authorization", "Bearer " + token)
    return json.loads(urllib.request.urlopen(r, context=ctx).read() or b"{}")


def etat(cle, state):
    e = api("GET", f"/processors/{ids[cle]}")
    api("PUT", f"/processors/{ids[cle]}/run-status", {"revision": e["revision"], "state": state})


for cle in ("put", "upd", "get"):          # PutFile d'abord, GetFile en dernier
    etat(cle, "RUNNING")
time.sleep(12)
stat = api("GET", f"/flow/process-groups/{ids['groupe']}/status")["processGroupStatus"]["aggregateSnapshot"]
for p in api("GET", f"/flow/process-groups/{ids['groupe']}/status")["processGroupStatus"]["aggregateSnapshot"]["processorStatusSnapshots"]:
    s = p["processorStatusSnapshot"]
    print(s["name"], s["runStatus"], "in", s["flowFilesIn"], "out", s["flowFilesOut"], "octets lus", s["bytesRead"], "ecrits", s["bytesWritten"])
json.dump(api("GET", f"/flow/process-groups/{ids['groupe']}/status"), open(sortie + "/statut_flux.json", "w"), indent=1)
for cle in ("get", "upd", "put"):
    etat(cle, "STOPPED")
q = api("POST", "/provenance", {"provenance": {"request": {"maxResults": 50}}})["provenance"]
for _ in range(20):
    q = api("GET", "/provenance/" + q["id"])["provenance"]
    if q["finished"]:
        break
    time.sleep(1)
ev = q["results"]["provenanceEvents"]
json.dump(ev, open(sortie + "/../provenance/provenance_evenements.json", "w"), indent=1)
for e in sorted(ev, key=lambda x: x["eventId"]):
    print(e["eventId"], e["eventTime"], e["eventType"], e["componentName"], e["flowFileUuid"], e["fileSize"])
api("DELETE", "/provenance/" + q["id"])
