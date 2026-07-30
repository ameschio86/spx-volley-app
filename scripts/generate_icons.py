"""One-off script: generate PWA icon set from logo_nuovo_Giallo.png."""
from PIL import Image
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "logo_nuovo_Giallo.png")
OUT = os.path.join(ROOT, "assets", "icons")
BG = (10, 10, 10, 255)  # #0a0a0a

logo = Image.open(SRC).convert("RGBA")


def make_icon(size, logo_ratio, filename, background=BG):
    canvas = Image.new("RGBA", (size, size), background)
    target_h = int(size * logo_ratio)
    ratio = target_h / logo.height
    target_w = int(logo.width * ratio)
    resized = logo.resize((target_w, target_h), Image.LANCZOS)
    x = (size - target_w) // 2
    y = (size - target_h) // 2
    canvas.alpha_composite(resized, (x, y))
    canvas.convert("RGB").save(os.path.join(OUT, filename), "PNG")


os.makedirs(OUT, exist_ok=True)

make_icon(192, 0.72, "icon-192.png")
make_icon(512, 0.72, "icon-512.png")
make_icon(512, 0.55, "icon-maskable-512.png")  # smaller, safe-zone padding for Android adaptive mask
make_icon(180, 0.72, "apple-touch-icon.png")
make_icon(32, 0.8, "favicon-32.png")
make_icon(16, 0.8, "favicon-16.png")

print("done")
