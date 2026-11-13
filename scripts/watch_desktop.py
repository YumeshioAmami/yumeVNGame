from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PID_PATH = Path(os.getenv("APPDATA") or str(Path.home() / ".config")) / "yumeVNGame" / "desktop.pid"
WATCH_ROOTS = [
    ROOT / "desktop.py",
    ROOT / "server",
    ROOT / "web" / "src",
    ROOT / "web" / "index.html",
    ROOT / "web" / "vite.config.ts",
    ROOT / "package.json",
    ROOT / "requirements.txt",
]
SUFFIXES = {".py", ".ts", ".tsx", ".css", ".html", ".json", ".md", ".sql"}


def snapshot() -> tuple:
    items = []
    for root in WATCH_ROOTS:
        if not root.exists():
            continue
        if root.is_file():
            stat = root.stat()
            items.append((str(root), stat.st_mtime_ns, stat.st_size))
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUFFIXES:
                stat = path.stat()
                items.append((str(path), stat.st_mtime_ns, stat.st_size))
    return tuple(sorted(items))


def desktop_pid() -> int | None:
    if not PID_PATH.exists():
        return None
    try:
        value = int(PID_PATH.read_text(encoding="ascii").strip())
        return value
    except (OSError, ValueError):
        return None


def stop_desktop() -> None:
    pid = desktop_pid()
    if not pid:
        return
    print(f"[watch] stopping desktop pid {pid}", flush=True)
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
    else:
        try:
            os.kill(pid, 15)
        except OSError:
            pass
    try:
        PID_PATH.unlink(missing_ok=True)
    except OSError:
        pass


def launch_desktop() -> None:
    python = Path(sys.executable)
    pythonw = python.with_name("pythonw.exe")
    executable = str(pythonw if os.name == "nt" and pythonw.exists() else python)
    print("[watch] launching desktop", flush=True)
    subprocess.Popen([executable, str(ROOT / "desktop.py")], cwd=ROOT)


def main() -> None:
    print("[watch] desktop source watcher started", flush=True)
    stop_desktop()
    launch_desktop()
    last = snapshot()
    while True:
        time.sleep(1.0)
        current = snapshot()
        if current == last:
            continue
        time.sleep(1.2)
        settled = snapshot()
        if settled != current:
            last = settled
            continue
        print("[watch] change detected; restarting desktop", flush=True)
        stop_desktop()
        time.sleep(0.5)
        launch_desktop()
        last = settled


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[watch] stopped", flush=True)

