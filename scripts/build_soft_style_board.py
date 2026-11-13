from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "reference_dataset" / "clannad_scenes"
OUT = ROOT / "data" / "reference_dataset" / "clannad_soft_style_board.jpg"


def fit(path: Path, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(Image.open(path).convert("RGB"), size, Image.LANCZOS)


def soft_mask(size: tuple[int, int]) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    w, h = size
    for step in range(30):
        inset = step * 3
        alpha = int(255 * (1 - step / 30) ** 1.8)
        draw.ellipse((inset, inset, w - inset, h - inset), fill=alpha)
    return mask.filter(ImageFilter.GaussianBlur(24))


def main() -> None:
    base = fit(SRC / "Clannad_girls.jpg", (1536, 1024)).filter(ImageFilter.GaussianBlur(1.2))
    canvas = base.convert("RGBA")

    scene = fit(SRC / "Clannad.PNG", (760, 760)).filter(ImageFilter.GaussianBlur(0.6))
    scene.putalpha(soft_mask(scene.size).point(lambda v: int(v * 0.55)))
    canvas.alpha_composite(scene, (720, 120))

    festival = fit(SRC / "Festival.jpg", (620, 420)).filter(ImageFilter.GaussianBlur(0.8))
    festival.putalpha(soft_mask(festival.size).point(lambda v: int(v * 0.42)))
    canvas.alpha_composite(festival, (40, 560))

    sprite = Image.open(SRC / "Furukawa_nagisa.png").convert("RGBA")
    sprite = ImageOps.contain(sprite, (330, 760), Image.LANCZOS)
    sprite.putalpha(sprite.getchannel("A").point(lambda v: int(v * 0.8)))
    canvas.alpha_composite(sprite, (1110, 220))

    draw = ImageDraw.Draw(canvas)
    for index, color in enumerate(["#f4dfbf", "#e9b7b0", "#b9c9e8", "#5b4b5f", "#2c3447"]):
        x = 1120 + index * 62
        draw.ellipse((x, 900, x + 42, 942), fill=color, outline="#ffffff", width=2)

    canvas.convert("RGB").save(OUT, quality=92)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

