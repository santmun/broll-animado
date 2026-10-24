"""Genera index.html desde scripts/index.template.html: inyecta subtítulos y la pista de SFX.

Corre desde la raíz del proyecto HyperFrames.
  __CAPTIONS__  ← transcript/captions.json (captions.py)
  <!--SFX-->    ← transcript/sfx-plan.json (sfx_plan.py); si no existe, sin SFX
"""
import json
from pathlib import Path

caps = json.loads(Path("transcript/captions.json").read_text())
plan_path = Path("transcript/sfx-plan.json")
plan = json.loads(plan_path.read_text()) if plan_path.exists() else []

sfx_html = "\n".join(
    f'    <audio id="sfx-{i:02d}" src="assets/sfx/{c["soundId"]}.wav" data-start="{c["at"]}" '
    f'data-media-start="{c["mediaStart"]}" data-duration="{c["durationSeconds"]}" '
    f'data-track-index="{20 + i % 3}" data-volume="{c["volume"]}"></audio>'
    for i, c in enumerate(plan)
)

tpl = Path("scripts/index.template.html").read_text()
out = tpl.replace("__CAPTIONS__", json.dumps(caps, ensure_ascii=False)).replace("<!--SFX-->", sfx_html)
Path("index.html").write_text(out)
print("index.html escrito:", len(caps), "grupos de subtítulo,", len(plan), "sfx")
