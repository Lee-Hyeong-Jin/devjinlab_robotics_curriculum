"""Pack `favicon.ico` (16, 32 and 48 px) from the PNGs `make-icons.mjs` rendered.

    python3 scripts/make-favicon.py

A browser tab uses the 16 or 32 px image; Google's search results need 48 px or a multiple of
it. Each size is the mark rendered at that size, not a 48 px image scaled down. The PNG inputs
are removed afterwards: only the .ico is served.
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SIZES = (16, 32, 48)

images = [Image.open(ROOT / "public" / f"favicon-{size}.png").convert("RGBA") for size in SIZES]
target = ROOT / "src" / "app" / "favicon.ico"
images[-1].save(target, format="ICO", sizes=[(s, s) for s in SIZES], append_images=images[:-1])
for size in SIZES:
    (ROOT / "public" / f"favicon-{size}.png").unlink()
print(f"{target.relative_to(ROOT)}: {', '.join(f'{s}x{s}' for s in SIZES)}")
