"""Baja sonidos del banco de EditorBrain, verifica SHA-256 y actualiza assets/sfx/manifest.json (sin URLs).

Corre desde la raíz del proyecto HyperFrames.

uso: python3 eb_get.py --project <eb-project> --catalog <sha256> [--bank editorbrain-essentials-v1] sfx-xxxx sfx-yyyy …
  --catalog  el catalogSha256 que devuelve `editorbrain sfx search`
"""
import argparse, hashlib, json, subprocess, urllib.request
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--project", required=True)
ap.add_argument("--catalog", required=True)
ap.add_argument("--bank", default="editorbrain-essentials-v1")
ap.add_argument("ids", nargs="+")
args = ap.parse_args()

out = Path("assets/sfx")
out.mkdir(parents=True, exist_ok=True)
mpath = out / "manifest.json"
manifest = json.loads(mpath.read_text()) if mpath.exists() else {}

for sid in args.ids:
    r = subprocess.run(["editorbrain", "sfx", "get", sid, "--project", args.project, "--bank", args.bank,
                        "--catalog-sha256", args.catalog, "--scene-role", "body"],
                       capture_output=True, text=True, cwd="/tmp")
    d = json.loads(r.stdout)
    a, e = d["asset"], d["entry"]
    data = urllib.request.urlopen(urllib.request.Request(a["url"], headers={"User-Agent": "Mozilla/5.0"})).read()
    sha = hashlib.sha256(data).hexdigest()
    assert sha == a["sha256"], f"{sid}: el hash no coincide"
    (out / f"{sid}.wav").write_bytes(data)
    manifest[sid] = {"name": e["name"], "sha256": sha, "duration": e["durationSeconds"],
                     "bank": args.bank, "catalogSha256": args.catalog}
    print("ok", sid, e["name"], e["durationSeconds"])

mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
