from __future__ import annotations

import re
import subprocess
import sys


MEDIA_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
    ".tiff",
    ".wav",
    ".mp3",
    ".flac",
    ".ogg",
    ".mp4",
    ".webm",
    ".mov",
}
KEY_PATTERN = re.compile(r"sk-[A-Za-z0-9]{20,}")
ALLOW = {".env.example"}


def main() -> None:
    files = [
        name
        for name in subprocess.check_output(["git", "ls-files"], text=True).splitlines()
        if name
    ]
    errors: list[str] = []
    for name in files:
        lower = name.lower()
        if any(lower.endswith(ext) for ext in MEDIA_EXTENSIONS):
            errors.append(f"binary/media file tracked: {name}")
        if lower in ALLOW or "node_modules/" in lower:
            continue
        try:
            text = open(name, "r", encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if KEY_PATTERN.search(text):
            errors.append(f"possible API key in: {name}")
        if ".nsfw." in lower:
            errors.append(f"NSFW asset tracked: {name}")
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"OK: {len(files)} tracked files, no media or API keys")


if __name__ == "__main__":
    main()

