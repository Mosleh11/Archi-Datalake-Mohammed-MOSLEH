"""
Récupère les fichiers lisibles du zip du prof.
Le zip est tronqué (pas de répertoire central), donc unzip / zipfile échouent.
On lit les en-têtes locaux un par un et on décompresse en flux.

Usage : python recuperation_zip.py retail_project.zip dossier_sortie
"""
import struct, os, sys, zlib

src, out = sys.argv[1], os.path.abspath(sys.argv[2])
f = open(src, "rb")
total = os.path.getsize(src)
pos = 0
while True:
    f.seek(pos)
    h = f.read(30)
    if len(h) < 30 or h[:4] != b"PK\x03\x04":
        print("fin à", pos, "sur", total)
        break
    _, flag, meth, _, _, crc, csz, usz, nl, el = struct.unpack("<HHHHHIIIHH", h[4:])
    name = f.read(nl).decode("utf-8", "replace")
    f.read(el)
    start = f.tell()
    dest = os.path.normpath(os.path.join(out, name))
    if not dest.startswith(out):  # on refuse les chemins qui sortent du dossier
        print("chemin suspect", name)
        break
    if name.endswith("/"):
        os.makedirs(dest, exist_ok=True)
        pos = start
        continue
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if not (flag & 8):  # tailles connues dans l'en-tête
        data = f.read(csz)
        open(dest, "wb").write(data)
        print("OK" if start + csz <= total else "TRONQUE", name, len(data))
        pos = start + csz
        continue
    # sinon : flux deflate, la taille est dans le descripteur après les données
    d = zlib.decompressobj(-15)
    n = 0
    fini = False
    with open(dest, "wb") as o:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            r = d.decompress(b)
            o.write(r)
            n += len(r)
            if d.eof:
                f.seek(f.tell() - len(d.unused_data))
                fini = True
                break
    print("COMPLET" if fini else "TRONQUE (flux incomplet)", name, n, "octets")
    if not fini:
        break
    p = f.tell()
    pos = p + 16 if f.read(4) == b"PK\x07\x08" else p + 12
