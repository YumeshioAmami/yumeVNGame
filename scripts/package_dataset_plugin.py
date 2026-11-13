from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "datasets" / "local" / "text_vn"
OUT = ROOT / "dist_plugins"


def main() -> None:
    if not SOURCE.exists() or not (SOURCE / "plugin.json").exists():
        raise SystemExit("Run `python scripts/build_text_dataset.py` first.")
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "text-vn-official-0.1.0.zip"
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in SOURCE.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(SOURCE))
    print(f"packaged {target} ({target.stat().st_size} bytes)")
    print("Install it from Settings -> External dataset / plugins.")


if __name__ == "__main__":
    main()

