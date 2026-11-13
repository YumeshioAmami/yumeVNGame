from __future__ import annotations

import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "web" / "dist" / "index.html"
WINDOW_TITLE = "yumeVNGame 0.1.0"
APP_DIR = Path(os.getenv("APPDATA") or str(Path.home() / ".config")) / "yumeVNGame"
LOCK_PATH = APP_DIR / "desktop.lock"
PID_PATH = APP_DIR / "desktop.pid"


class SingleInstanceLock:
    """OS-level lock so only one desktop process can run at a time."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.handle = None

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = open(self.path, "a+b")
        self.handle.seek(0, 2)
        if self.handle.tell() == 0:
            self.handle.write(b"0")
            self.handle.flush()
        self.handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            self.handle.close()
            self.handle = None
            return False

    def release(self) -> None:
        if not self.handle:
            return
        try:
            if os.name == "nt":
                import msvcrt

                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        finally:
            self.handle.close()
            self.handle = None


def focus_existing() -> None:
    if os.name != "nt":
        print("[desktop] another instance is already running")
        return
    import ctypes

    user32 = ctypes.windll.user32
    hwnd = user32.FindWindowW(None, WINDOW_TITLE)
    if hwnd:
        user32.ShowWindow(hwnd, 9)
        user32.SetForegroundWindow(hwnd)
    else:
        user32.MessageBoxW(None, "yumeVNGame 已经在运行。", WINDOW_TITLE, 0x40)


def ensure_frontend() -> None:
    assets = ROOT / "web" / "public" / "assets" / "backgrounds"
    if not assets.exists() or len(list(assets.glob("*.svg"))) < 6:
        print("[desktop] generating local placeholder art...")
        subprocess.run([sys.executable, "scripts/build_assets.py"], cwd=ROOT, check=True)
    sources = [ROOT / "web" / "index.html", ROOT / "package.json"]
    if (ROOT / "web" / "src").exists():
        sources.extend((ROOT / "web" / "src").rglob("*.tsx"))
        sources.extend((ROOT / "web" / "src").rglob("*.ts"))
        sources.extend((ROOT / "web" / "src").rglob("*.css"))
    latest = max((path.stat().st_mtime for path in sources if path.exists()), default=0)
    if not DIST.exists() or DIST.stat().st_mtime < latest:
        print("[desktop] building frontend bundle...")
        subprocess.run("npm run build", cwd=ROOT, shell=True, check=True)


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_server(url: str, timeout: float = 20.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1):
                return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("local API did not start")


def main() -> None:
    lock = SingleInstanceLock(LOCK_PATH)
    if not lock.acquire():
        focus_existing()
        return
    try:
        PID_PATH.write_text(str(os.getpid()), encoding="ascii")
        ensure_frontend()
        # Import after the bundle exists: server.main mounts web/dist at import time.
        from server.main import app
        import uvicorn
        import webview

        port = free_port()
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=port,
            log_level="warning",
            access_log=False,
        )
        server = uvicorn.Server(config)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{port}"
        wait_for_server(f"{base_url}/api/health")
        print(f"[desktop] yumeVNGame 0.1.0 -> {base_url}")

        window = webview.create_window(
            WINDOW_TITLE,
            base_url,
            width=1440,
            height=920,
            min_size=(1100, 700),
            background_color="#05070d",
            confirm_close=False,
        )
        auto_close_ms = os.getenv("YUME_AUTO_CLOSE_MS", "").strip()
        if auto_close_ms.isdigit():
            threading.Timer(int(auto_close_ms) / 1000, window.destroy).start()
        try:
            webview.start(debug=os.getenv("YUME_DEBUG") == "1")
        finally:
            server.should_exit = True
            thread.join(timeout=3)
    finally:
        try:
            PID_PATH.unlink(missing_ok=True)
        except OSError:
            pass
        lock.release()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[desktop] failed to start: {exc}", file=sys.stderr)
        raise

