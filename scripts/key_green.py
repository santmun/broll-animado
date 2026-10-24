"""Quita el fondo verde de un clip de Kling y exporta WebM VP9 con alpha.

Key por dominancia de verde (g - max(r, b)), así las sombras verdes oscuras
también se van. Despill para que los bordes no queden verdosos.

uso: python3 key_green.py in.mp4 out.webm [--size 1920x1080] [--t0 18] [--t1 60]
  --t0  dominancia de verde por debajo de la cual el pixel es opaco (súbelo si se come bordes negros finos)
  --t1  dominancia a partir de la cual es transparente (bájalo si queda halo verde)
"""
import subprocess, sys
import numpy as np

src, dst = sys.argv[1], sys.argv[2]


def opt(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


size = opt("--size", None)

probe = subprocess.run(
    ["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
     "stream=width,height,r_frame_rate", "-of", "csv=p=0", src],
    capture_output=True, text=True, check=True).stdout.strip().split(",")
w, h = int(probe[0]), int(probe[1])
fps = probe[2]
if size:
    w, h = map(int, size.split("x"))

dec = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-i", src, "-vf", f"scale={w}:{h}:flags=lanczos",
     "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
     "-s", f"{w}x{h}", "-r", fps, "-i", "-", "-c:v", "libvpx-vp9",
     "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "24", "-row-mt", "1",
     "-auto-alt-ref", "0", dst], stdin=subprocess.PIPE)

T0, T1 = float(opt("--t0", 18)), float(opt("--t1", 60))  # dominancia de verde: <T0 opaco, >T1 transparente
n = 0
while True:
    buf = dec.stdout.read(w * h * 3)
    if len(buf) < w * h * 3:
        break
    f = np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(np.float32)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    dom = g - np.maximum(r, b)
    a = 1.0 - np.clip((dom - T0) / (T1 - T0), 0, 1)
    # despill: limita el verde al máximo de r/b donde hay contaminación
    g2 = np.where(dom > 0, np.maximum(r, b) + np.minimum(dom, T0) * 0.2, g)
    out = np.dstack([r, g2, b, a * 255]).clip(0, 255).astype(np.uint8)
    enc.stdin.write(out.tobytes())
    n += 1

enc.stdin.close()
enc.wait()
dec.wait()
print(f"{dst}: {n} frames {w}x{h}")
