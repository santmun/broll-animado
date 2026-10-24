"""Hoja de contacto para revisar con Read: imágenes sueltas o cuadros de un video.

uso:
  python3 hoja.py --images "escenas/stills/*.png" -o hoja.jpg
  python3 hoja.py --video renders/v1.mp4 --at 1.6,6.6,11.8 -o hoja.jpg
  python3 hoja.py --video clip.mp4 --at inicio,mitad,final -o hoja.jpg   (cuadros relativos a la duración)
"""
import argparse, glob, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("--images")
ap.add_argument("--video")
ap.add_argument("--at", default="inicio,mitad,final")
ap.add_argument("--cols", type=int, default=4)
ap.add_argument("--width", type=int, default=480)
ap.add_argument("-o", "--out", required=True)
args = ap.parse_args()

items = []  # (etiqueta, ruta)
if args.images:
    items = [(os.path.basename(p), p) for p in sorted(glob.glob(os.path.expanduser(args.images)))]
elif args.video:
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", args.video],
                               capture_output=True, text=True).stdout)
    rel = {"inicio": 0.05, "mitad": 0.5, "final": 0.95}
    tmp = tempfile.mkdtemp()
    for i, t in enumerate(args.at.split(",")):
        sec = dur * rel[t] if t in rel else float(t)
        p = os.path.join(tmp, f"{i:03d}.jpg")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sec:.3f}", "-i", args.video, "-frames:v", "1", p], check=True)
        items.append((f"{sec:.2f}s", p))
if not items:
    raise SystemExit("nada que poner en la hoja")

try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
except OSError:
    font = ImageFont.load_default()
thumbs = []
for label, p in items:
    im = Image.open(p).convert("RGB")
    thumbs.append((label, im.resize((args.width, int(im.height * args.width / im.width)))))
cell_h = max(t.height for _, t in thumbs) + 30
rows = (len(thumbs) + args.cols - 1) // args.cols
sheet = Image.new("RGB", (min(len(thumbs), args.cols) * args.width, rows * cell_h), "#111")
d = ImageDraw.Draw(sheet)
for k, (label, t) in enumerate(thumbs):
    x, y = (k % args.cols) * args.width, (k // args.cols) * cell_h
    sheet.paste(t, (x, y + 30))
    d.text((x + 6, y + 4), label, font=font, fill=(245, 166, 35))
sheet.save(args.out, quality=85)
print(args.out, len(thumbs), "cuadros")
