"""Plan de SFX: calcula el volumen de cada cue para que quede por debajo de la voz.

Corre desde la raíz del proyecto HyperFrames. Lee transcript/sfx-cues.json y escribe transcript/sfx-plan.json,
que luego usa build.py.

Formato de transcript/sfx-cues.json (una entrada por cue):
  [{"at": 1.38, "soundId": "sfx-fdea8c16b3393c", "mediaStart": 0.0, "duration": 0.48, "below": 11, "purpose": "corte de tijeras"}, …]
  soundId   nombre del archivo en assets/sfx/ sin .wav (de EditorBrain o tuyo)
  at        segundo en el timeline
  mediaStart desde qué segundo del archivo arranca (default 0)
  duration  cuánto suena
  below     dB por debajo del pico momentáneo de la voz: acentos 11, barridos/papel 14, trazos 13

Ganancia = el tope más estricto de tres:
  M      pico de loudness momentáneo (400 ms) del cue = voz − below
  pico   pico de muestra del cue ≤ pico de la voz − 12 dB
  rms50  RMS de 50 ms del cue ≤ RMS de 50 ms de la voz − 15 dB
El M solo subestima golpes cortos (clics, impactos): por eso los otros dos.
Los archivos mono se miden en estéreo y llevan −3 dB extra (HyperFrames los reproduce más fuerte).

uso: python3 sfx_plan.py [--voice assets/video/santi.mp4]
"""
import argparse, json, re, subprocess
from pathlib import Path
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--voice", default="assets/video/santi.mp4")
args = ap.parse_args()

# manifest.json lo escribe eb_get.py; con tus propios .wav no hace falta (el nombre es el archivo)
mpath = Path("assets/sfx/manifest.json")
man = json.loads(mpath.read_text()) if mpath.exists() else {}
cues = json.loads(Path("transcript/sfx-cues.json").read_text())
PEAK_BELOW, RMS50_BELOW = 12, 15


def channels(path):
    return subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=channels", "-of", "csv=p=0", path],
                          capture_output=True, text=True).stdout.strip()


def voice_m():
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", args.voice, "-vn", "-ac", "2", "-ar", "48000",
                        "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return [(float(t), float(m)) for t, m in re.findall(r"t:\s*([\d.]+)\s+TARGET.*?M:\s*(-?[\d.]+)", r)]


def m_max(path, ss, dur):
    up = "pan=stereo|c0=c0|c1=c0," if channels(path) == "1" else ""
    af = f"{up}atrim={ss}:{ss + dur},asetpts=N/SR/TB,apad=pad_dur=0.6,ebur128"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", af, "-f", "null", "-"], capture_output=True, text=True).stderr
    vals = [float(x) for x in re.findall(r" M:\s*(-?[\d.]+)", r)]
    return max(vals) if vals else -99.0


def pcm(path, ss=0.0, dur=None):
    """Mono float a 48 kHz (promedio L/R, como suena en la mezcla)."""
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss)] + (["-t", str(dur)] if dur else []) + \
          ["-i", path, "-f", "f32le", "-ac", "2", "-ar", "48000", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).mean(axis=1)


def peak_db(x):
    return 20 * np.log10(np.abs(x).max() + 1e-12)


def rms50_db(x, w=2400):
    k = len(x) // w
    if k == 0:
        return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)
    return 20 * np.log10(np.sqrt((x[:k * w].reshape(k, w) ** 2).mean(axis=1)).max() + 1e-12)


VM = voice_m()
VOICE = pcm(args.voice)


def voice_at(t, dur):
    vals = [m for tt, m in VM if t <= tt <= t + dur + 0.4]
    return max(vals) if vals else -20.0


plan = []
for c in cues:
    start, sid, dur, off = c["at"], c["soundId"], c["duration"], c["below"]
    ms = c.get("mediaStart", 0.0)
    path = f"assets/sfx/{sid}.wav"
    v = voice_at(start, dur)
    m = m_max(path, ms, dur)
    seg = pcm(path, ms, dur)
    win = VOICE[max(0, int((start - 0.5) * 48000)):int((start + dur + 0.5) * 48000)]
    gains = {
        "M": (v - off) - m,
        "pico": (peak_db(win) - PEAK_BELOW) - peak_db(seg),
        "rms50": (rms50_db(win) - RMS50_BELOW) - rms50_db(seg),
    }
    limit = min(gains, key=gains.get)
    gain_db = float(gains[limit]) - (3.0 if channels(path) == "1" else 0.0)
    vol = round(min(10 ** (gain_db / 20), 3.98), 3)
    plan.append({"at": start, "soundId": sid, "name": man.get(sid, {}).get("name", sid), "mediaStart": ms, "durationSeconds": dur,
                 "volume": vol, "voiceM": round(v, 1), "sfxM": round(m, 1), "belowVoiceDb": off,
                 "limitedBy": limit, "purpose": c.get("purpose", "")})
    print(f"{start:6.2f} {man.get(sid, {}).get('name', sid):22s} -> vol {vol:5.3f} ({gain_db:+.1f} dB, manda {limit})  {c.get('purpose', '')}")

Path("transcript/sfx-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
