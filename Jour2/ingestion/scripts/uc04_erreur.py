"""Erreur controlee : dossier source inexistant dans GetFile, observation, puis retour a la configuration d'origine"""
import json, ssl, sys, urllib.request, urllib.parse
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


def regler(dossier):
    e = api("GET", f"/processors/{ids['get']}")
    e = api("PUT", f"/processors/{ids['get']}", {"revision": e["revision"], "component": {
        "id": ids["get"], "config": {"properties": {"Input Directory": dossier}}}})
    c = e["component"]
    print("Input Directory =", c["config"]["properties"]["Input Directory"], "| validation :", c["validationStatus"], c.get("validationErrors", []))


regler("/data/nifi/inexistant")
regler("/data/nifi/input")
