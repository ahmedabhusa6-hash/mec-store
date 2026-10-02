# MEC-21: generate brand icons (icon.png 512, apple-icon.png 180, favicon.ico 48)
# Lightning bolt mark on dark rounded square — matches store branding (emerald/zinc).
from PIL import Image, ImageDraw

EMERALD = (16, 185, 129, 255)      # emerald-500
EMERALD_LIGHT = (52, 211, 153, 255) # emerald-400
ZINC950 = (9, 9, 11, 255)          # zinc-950

def draw_mark(size: int, radius_ratio: float = 0.22) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(size * radius_ratio)
    # dark rounded square background
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=ZINC950)
    # emerald border
    bw = max(2, size // 42)
    d.rounded_rectangle([bw, bw, size - 1 - bw, size - 1 - bw], radius=max(1, r - bw), outline=(6, 78, 59, 255), width=bw)
    # lightning bolt polygon (classic 7-point bolt), centered
    s = size
    bolt = [
        (0.58 * s, 0.16 * s),  # top right of upper arm
        (0.30 * s, 0.55 * s),  # left mid
        (0.47 * s, 0.55 * s),  # inner notch
        (0.40 * s, 0.84 * s),  # bottom tip left
        (0.70 * s, 0.44 * s),  # right mid
        (0.53 * s, 0.44 * s),  # inner notch 2
        (0.68 * s, 0.16 * s),  # hmm — fix: keep 7 points coherent
    ]
    # Simpler coherent bolt (x,y) in unit space:
    bolt = [
        (0.55, 0.14),
        (0.28, 0.56),
        (0.45, 0.56),
        (0.38, 0.86),
        (0.72, 0.42),
        (0.53, 0.42),
        (0.68, 0.14),
    ]
    pts = [(int(x * s), int(y * s)) for x, y in bolt]
    d.polygon(pts, fill=EMERALD)
    # subtle top highlight: thinner lighter bolt overlay upper half
    bolt_hi = [
        (0.55, 0.14),
        (0.40, 0.38),
        (0.53, 0.42),
        (0.68, 0.14),
    ]
    pts_hi = [(int(x * s), int(y * s)) for x, y in bolt_hi]
    d.polygon(pts_hi, fill=EMERALD_LIGHT)
    return img

img512 = draw_mark(512)
img512.save("/home/z/my-project/public/icon.png")
img512.resize((180, 180), Image.LANCZOS).save("/home/z/my-project/public/apple-icon.png")
img512.resize((48, 48), Image.LANCZOS).save("/home/z/my-project/public/favicon.ico", sizes=[(48, 48)])
img512.resize((32, 32), Image.LANCZOS).save("/home/z/my-project/public/favicon-32.png")
print("icons written: public/icon.png (512), apple-icon.png (180), favicon.ico (48), favicon-32.png")
