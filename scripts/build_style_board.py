from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import requests
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "reference_dataset" / "clannad_scenes"
BOARD = ROOT / "data" / "reference_dataset" / "clannad_style_board.jpg"
API = "https://clannad.fandom.com/api.php"
HEADERS = {"User-Agent": "yumeVNGame-reference-research/0.1"}
FILES = [
    "File:Clannad girls.jpg",
    "File:Festival.jpg",
    "File:Field of flowers.jpg",
    "File:Clannad.PNG",
    "File:Furukawa nagisa.png",
    "File:Fujibayashi kyo.png",
]


def safe_name(value: str) -> str:
    value = value.replace("File:", "")
    value = re.sub(r"[^\w.\-]+", "_", value, flags=re.UNICODE)
    return value.strip("._")[:120] or "image"


def fetch(title: str) -> Path | None:
    response = requests.get(
        API,
        params={
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "iiprop": "url|mime|size",
            "iiurlwidth": 1200,
            "titles": title,
        },
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    infos = page.get("imageinfo") or []
    if not infos:
        return None
    info = infos[0]
    url = info.get("thumburl") or info.get("url")
    if not url:
        return None
    extension = ".png" if "png" in info.get("mime", "") else ".jpg"
    target = OUT / f"{safe_name(title).rsplit('.', 1)[0]}{extension}"
    data = requests.get(url, headers=HEADERS, timeout=60)
    data.raise_for_status()
    target.write_bytes(data.content)
    return target


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = []
    for title in FILES:
        print(f"[board] {title}", flush=True)
        try:
            path = fetch(title)
        except Exception as exc:
            print(f"[board] failed: {exc}", flush=True)
            continue
        if path:
            paths.append(path)
    if not paths:
        raise SystemExit("no style board images")
    cell = 512
    cols = 3
    rows = 2
    warm = Image.new("RGB", (cell, cell), "#f3e7d7")
    board = Image.new("RGB", (cell * cols, cell * rows), "#f3e7d7")
    for index, path in enumerate(paths[: cols * rows]):
        image = Image.open(path).convert("RGBA")
        base = warm.copy()
        base.paste(image, (0, 0), image)
        fitted = ImageOps.fit(base.convert("RGB"), (cell, cell), Image.LANCZOS)
        board.paste(fitted, ((index % cols) * cell, (index // cols) * cell))
    board.save(BOARD, quality=92)
    (OUT / "manifest.json").write_text(
        json.dumps(
            {
                "source": "CLANNAD Fandom public character/scene pages",
                "usage_note": "Local research/style-reference only; not redistributed or committed.",
                "files": [str(path.relative_to(ROOT)) for path in paths],
                "board": str(BOARD.relative_to(ROOT)),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[board] wrote {BOARD}")


if __name__ == "__main__":
    main()

