"""Agrupa las palabras de AssemblyAI en frases cortas para subtítulos palabra por palabra.

Corre desde la raíz del proyecto HyperFrames: lee transcript/raw.json, escribe transcript/captions.json.

uso: python3 captions.py [--hide 16.95-17.8,23.5-24.6] [--max 4] [--fix "aún=>¿aún|sabes,=>sabes?"]
  --hide  ventanas (segundos) donde manda el texto cinético: ahí no hay subtítulo
  --max   palabras máximas por frase (default 4)
  --fix   reemplazos exactos de palabra (AssemblyAI suele perder los signos de pregunta)
"""
import argparse, json, re

ap = argparse.ArgumentParser()
ap.add_argument("--hide", default="")
ap.add_argument("--max", type=int, default=4)
ap.add_argument("--fix", default="")
args = ap.parse_args()
HIDE = [tuple(map(float, w.split("-"))) for w in args.hide.split(",") if w]
FIX = dict(p.split("=>", 1) for p in args.fix.split("|") if "=>" in p)

words = json.load(open("transcript/raw.json"))["words"]
W = [{"t": w["text"], "s": w["start"] / 1000, "e": w["end"] / 1000} for w in words]

# AssemblyAI parte "B-roll" en "B" + "roll"
out, i = [], 0
while i < len(W):
    w = W[i]
    if w["t"] == "B" and i + 1 < len(W) and W[i + 1]["t"].lower().startswith("roll"):
        out.append({"t": "B-roll" + W[i + 1]["t"][4:], "s": w["s"], "e": W[i + 1]["e"]})
        i += 2
        continue
    out.append(dict(w))
    i += 1
W = out
for w in W:
    w["t"] = FIX.get(w["t"], w["t"])

# nombres propios que no abren frase aunque vayan con mayúscula
PROPER = {"B-roll", "YouTube", "Instagram", "TikTok", "Claude", "Higgsfield", "Kling"}

def hidden(w):
    return any(a <= w["s"] < b for a, b in HIDE)

groups, cur = [], []
for w in W:
    if hidden(w):
        if cur:
            groups.append(cur); cur = []
        continue
    new_sentence = w["t"][:1].isupper() and re.sub(r"[.,?!]$", "", w["t"]) not in PROPER
    if cur and (len(cur) >= args.max or w["s"] - cur[-1]["e"] > 0.22 or new_sentence):
        groups.append(cur); cur = []
    cur.append(w)
    if re.search(r"[.,?!]$", w["t"]):
        groups.append(cur); cur = []
if cur:
    groups.append(cur)

# una palabra corta suelta se pega al grupo anterior
merged = []
for g in groups:
    if merged and len(g) == 1 and len(g[0]["t"]) <= 3 and g[0]["s"] - merged[-1][-1]["e"] < 0.6 and len(merged[-1]) < args.max:
        merged[-1].append(g[0])
    else:
        merged.append(g)
groups = merged

res = []
for gi, g in enumerate(groups):
    nxt = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else 1e9
    end = min(nxt, g[-1]["e"] + 0.45)
    for a, b in HIDE:
        if a > g[0]["s"]:
            end = min(end, a + 0.05)
    res.append({"s": round(g[0]["s"], 3), "e": round(end, 3),
                "w": [[re.sub(r"[.,]$", "", w["t"]), round(w["s"], 3)] for w in g]})
json.dump(res, open("transcript/captions.json", "w"), ensure_ascii=False)
for r in res:
    print(f'{r["s"]:6.2f}-{r["e"]:6.2f} ' + " ".join(w[0] for w in r["w"]))
