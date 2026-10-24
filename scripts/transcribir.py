"""Transcribe con AssemblyAI (español, disfluencias, tiempos por palabra) y guarda el JSON crudo.

uso: python3 transcribir.py audio.wav transcript/raw.json
La key se lee de la variable ASSEMBLYAI_API_KEY o de ~/.config/broll-animado/keys.env (línea ASSEMBLYAI_API_KEY=...).
"""
import json, os, sys, time, urllib.request


def api_key():
    if os.environ.get("ASSEMBLYAI_API_KEY"):
        return os.environ["ASSEMBLYAI_API_KEY"]
    path = os.path.expanduser("~/.config/broll-animado/keys.env")
    if os.path.exists(path):
        for line in open(path):
            if line.startswith("ASSEMBLYAI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"')
    sys.exit("Falta la key de AssemblyAI: export ASSEMBLYAI_API_KEY=... o guárdala en ~/.config/broll-animado/keys.env")


key = api_key()
H = {"authorization": key, "User-Agent": "Mozilla/5.0"}
API = "https://api.assemblyai.com/v2"

src, dst = sys.argv[1], sys.argv[2]
req = urllib.request.Request(f"{API}/upload", data=open(src, "rb").read(), headers=H, method="POST")
url = json.load(urllib.request.urlopen(req))["upload_url"]

body = json.dumps({"audio_url": url, "language_code": "es", "disfluencies": True,
                   "punctuate": True, "format_text": True}).encode()
req = urllib.request.Request(f"{API}/transcript", data=body, headers={**H, "content-type": "application/json"}, method="POST")
tid = json.load(urllib.request.urlopen(req))["id"]

while True:
    r = json.load(urllib.request.urlopen(urllib.request.Request(f"{API}/transcript/{tid}", headers=H)))
    if r["status"] in ("completed", "error"):
        break
    time.sleep(2)

os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
json.dump(r, open(dst, "w"), ensure_ascii=False, indent=1)
print(r["status"], r.get("error") or "")
print(r.get("text"))
