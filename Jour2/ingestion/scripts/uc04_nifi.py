"""UC-04 : construit dans NiFi GetFile -> UpdateAttribute -> PutHDFS, avec LogAttribute sur les echecs.
Prerequis : les NAR nifi-hadoop-nar et nifi-hadoop-libraries-nar 2.12.0 doivent etre dans nar_extensions (voir README)."""
import json, ssl, sys, time, urllib.request, urllib.parse

BASE = "https://localhost:8443/nifi-api"
ctx = ssl._create_unverified_context()
sortie = sys.argv[1]
mdp = open("../docker/nifi.env").read().split("PASSWORD=")[1].split()[0]


def api(methode, chemin, corps=None, form=None):
    data = urllib.parse.urlencode(form).encode() if form else (json.dumps(corps).encode() if corps is not None else None)
    req = urllib.request.Request(BASE + chemin, data=data, method=methode)
    if not form:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        return json.loads(urllib.request.urlopen(req, context=ctx).read() or b"{}")
    except urllib.error.HTTPError as e:
        print("ERREUR", e.code, e.read().decode()[:500]); raise


token = None
token = urllib.request.urlopen(urllib.request.Request(BASE + "/access/token", data=urllib.parse.urlencode(
    {"username": "etudiant", "password": mdp}).encode()), context=ctx).read().decode()
racine = api("GET", "/flow/process-groups/root")["processGroupFlow"]["id"]


def processeur(type_, artefact, nom, x, y, props, termine):
    b = {"revision": {"version": 0}, "component": {
        "type": type_, "name": nom, "position": {"x": x, "y": y},
        "bundle": {"group": "org.apache.nifi", "artifact": artefact, "version": "2.12.0"},
        "config": {"properties": props, "autoTerminatedRelationships": termine}}}
    return api("POST", f"/process-groups/{racine}/processors", b)


def lien(src, dst, rels):
    b = {"revision": {"version": 0}, "component": {
        "source": {"id": src["id"], "groupId": racine, "type": "PROCESSOR"},
        "destination": {"id": dst["id"], "groupId": racine, "type": "PROCESSOR"}, "selectedRelationships": rels}}
    return api("POST", f"/process-groups/{racine}/connections", b)


S = "org.apache.nifi.processors.standard."
get = processeur(S + "GetFile", "nifi-standard-nar", "GetFile_entree", 50, 100,
                 {"Input Directory": "/data/nifi/input", "Keep Source File": "false", "Recurse Subdirectories": "false"}, [])
upd = processeur("org.apache.nifi.processors.attributes.UpdateAttribute", "nifi-update-attribute-nar", "UpdateAttribute_suivi", 700, 100,
                 {"source": "tpcxbb", "zone": "raw", "ingere_par": "nifi_j2"}, [])
put = processeur("org.apache.nifi.processors.hadoop.PutHDFS", "nifi-hadoop-nar", "PutHDFS_raw_nifi", 1350, 100,
                 {"Hadoop Configuration Resources": "/opt/hadoop-conf/core-site.xml,/opt/hadoop-conf/hdfs-site.xml",
                  "Directory": "/retail-lake/raw/nifi", "Conflict Resolution Strategy": "fail"}, ["success"])
log = processeur(S + "LogAttribute", "nifi-standard-nar", "LogAttribute_echec", 1350, 450, {}, ["success"])
lien(get, upd, ["success"]); lien(upd, put, ["success"]); lien(put, log, ["failure"])
for p in (get, upd, put, log):
    e = api("GET", f"/processors/{p['id']}")
    print(e["component"]["name"], e["component"]["state"], e["component"].get("validationStatus"),
          [m for m in e["component"].get("validationErrors", [])])
json.dump({"get": get["id"], "upd": upd["id"], "put": put["id"], "log": log["id"], "groupe": racine}, open(sortie + "/ids.json", "w"))
