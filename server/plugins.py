from __future__ import annotations

import base64
import io
import json
import os
import re
import shutil
import uuid
import zipfile
from pathlib import Path
from typing import Any

from . import db


ROOT = Path(__file__).resolve().parent.parent
BUNDLED_DIR = ROOT / "plugins"
USER_DIR = Path(os.getenv("APPDATA") or str(Path.home() / ".config")) / "yumeVNGame" / "plugins"
FALLBACK_STYLE = Path(__file__).with_name("style_guide.md")
ALLOWED_TYPES = {
    "dataset",
    "world",
    "story",
    "music",
    "image",
    "voice",
    "asset_pack",
    "theme",
}


def _safe_id(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-.")
    return clean[:80] or f"plugin-{uuid.uuid4().hex[:8]}"


def _manifest(directory: Path) -> dict[str, Any] | None:
    path = directory / "plugin.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    if not data.get("id") or not data.get("name") or not data.get("type"):
        return None
    data["type"] = str(data["type"])
    if data["type"] not in ALLOWED_TYPES:
        data["type"] = "asset_pack"
    return data


def _work_count(directory: Path, manifest: dict[str, Any]) -> int:
    data_file = manifest.get("data_file")
    if not data_file:
        return 0
    path = directory / str(data_file)
    if not path.exists():
        return 0
    if path.suffix == ".jsonl":
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    if path.suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return 0
        return len(data) if isinstance(data, list) else 1
    return 0


def _is_enabled(plugin_id: str, manifest: dict[str, Any]) -> bool:
    default = "1" if manifest.get("enabled_by_default") else "0"
    return db.get_setting(f"plugin.{plugin_id}.enabled", default) in {"1", "true", "yes", "on"}


def _plugin_info(directory: Path, manifest: dict[str, Any], source: str) -> dict[str, Any]:
    plugin_id = _safe_id(str(manifest["id"]))
    return {
        "id": plugin_id,
        "name": str(manifest.get("name", plugin_id)),
        "version": str(manifest.get("version", "0.0.0")),
        "type": str(manifest.get("type", "asset_pack")),
        "description": str(manifest.get("description", "")),
        "author": str(manifest.get("author", "")),
        "license": str(manifest.get("license", "")),
        "tags": manifest.get("tags", []),
        "source": source,
        "works": _work_count(directory, manifest),
        "enabled": _is_enabled(plugin_id, manifest),
        "path": str(directory),
    }


def _iter_dirs() -> list[tuple[Path, str]]:
    dirs: list[tuple[Path, str]] = []
    if BUNDLED_DIR.exists():
        dirs.extend((path, "bundled") for path in BUNDLED_DIR.iterdir() if path.is_dir())
    if USER_DIR.exists():
        dirs.extend((path, "user") for path in USER_DIR.iterdir() if path.is_dir() and not path.name.startswith("."))
    return dirs


def list_plugins() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for directory, source in _iter_dirs():
        manifest = _manifest(directory)
        if manifest:
            items.append(_plugin_info(directory, manifest, source))
    items.sort(key=lambda item: (item["source"] != "bundled", item["type"], item["name"]))
    return items


def get_plugin(plugin_id: str) -> dict[str, Any] | None:
    return next((item for item in list_plugins() if item["id"] == plugin_id), None)


def _plugin_dir(plugin_id: str) -> Path | None:
    for directory, _source in _iter_dirs():
        manifest = _manifest(directory)
        if manifest and _safe_id(str(manifest["id"])) == plugin_id:
            return directory
    return None


def set_enabled(plugin_id: str, enabled: bool) -> dict[str, Any]:
    if not get_plugin(plugin_id):
        raise ValueError("plugin not found")
    db.set_setting(f"plugin.{plugin_id}.enabled", "1" if enabled else "0")
    return get_plugin(plugin_id) or {}


def _enabled_dataset_plugins() -> list[tuple[Path, dict[str, Any]]]:
    result = []
    for directory, _source in _iter_dirs():
        manifest = _manifest(directory)
        if not manifest or manifest.get("type") != "dataset":
            continue
        if _is_enabled(_safe_id(str(manifest["id"])), manifest):
            result.append((directory, manifest))
    return result


def dataset_summary() -> dict[str, Any]:
    plugins = [item for item in list_plugins() if item["type"] == "dataset"]
    active = [item for item in plugins if item["enabled"]]
    return {
        "works": sum(item["works"] for item in active),
        "plugins": len(plugins),
        "active_plugins": len(active),
        "status": "ready" if active else "external_optional",
        "mode": "external_plugin",
    }


def dataset_preview(limit: int = 8) -> list[dict[str, Any]]:
    preview: list[dict[str, Any]] = []
    for directory, manifest in _enabled_dataset_plugins():
        data_file = manifest.get("data_file")
        if not data_file:
            continue
        path = directory / str(data_file)
        if path.suffix != ".jsonl" or not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            item.setdefault("plugin_id", _safe_id(str(manifest["id"])))
            preview.append(item)
            if len(preview) >= limit:
                return preview
    return preview


def dataset_context(max_chars: int = 6000) -> str:
    parts: list[str] = []
    for directory, manifest in _enabled_dataset_plugins():
        context_file = manifest.get("context_file")
        if context_file:
            path = directory / str(context_file)
            if path.exists():
                parts.append(path.read_text(encoding="utf-8")[:2800])
        data_file = manifest.get("data_file")
        if data_file:
            path = directory / str(data_file)
            if path.suffix == ".jsonl" and path.exists():
                compact = []
                for line in path.read_text(encoding="utf-8").splitlines()[:10]:
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    compact.append(
                        " | ".join(
                            str(value)
                            for value in [
                                item.get("title_zh", item.get("title", "")),
                                ", ".join(item.get("genres", [])),
                                ", ".join(item.get("themes", [])),
                                ", ".join(item.get("narrative_devices", [])),
                                item.get("pacing_notes", ""),
                                str(item.get("summary_zh", ""))[:260],
                            ]
                            if value
                        )
                    )
                if compact:
                    parts.append("\n".join(compact))
    if not parts and FALLBACK_STYLE.exists():
        parts.append(FALLBACK_STYLE.read_text(encoding="utf-8"))
    return "\n\n".join(parts)[:max_chars]


def install_plugin_zip(filename: str, data_base64: str) -> dict[str, Any]:
    try:
        raw = base64.b64decode(data_base64)
    except Exception as exc:
        raise ValueError(f"invalid base64: {exc}") from exc
    if len(raw) > 30 * 1024 * 1024:
        raise ValueError("plugin archive is too large (max 30 MB)")
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        raise ValueError("plugin must be a .zip archive")
    USER_DIR.mkdir(parents=True, exist_ok=True)
    temp = USER_DIR / f".install-{uuid.uuid4().hex}"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            for member in archive.infolist():
                target = (temp / member.filename).resolve()
                if not str(target).startswith(str(temp.resolve())):
                    raise ValueError("unsafe path in plugin archive")
            archive.extractall(temp)
        manifests = list(temp.rglob("plugin.json"))
        if not manifests:
            raise ValueError("plugin.json not found")
        plugin_root = manifests[0].parent
        manifest = _manifest(plugin_root)
        if not manifest:
            raise ValueError("invalid plugin.json")
        plugin_id = _safe_id(str(manifest["id"]))
        destination = USER_DIR / plugin_id
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(plugin_root, destination)
    finally:
        shutil.rmtree(temp, ignore_errors=True)
    info = get_plugin(plugin_id)
    if not info:
        raise ValueError("plugin installed but not discoverable")
    return info


def delete_plugin(plugin_id: str) -> None:
    directory = _plugin_dir(plugin_id)
    if not directory:
        raise ValueError("plugin not found")
    if str(directory).startswith(str(BUNDLED_DIR.resolve())):
        raise ValueError("bundled plugins cannot be deleted")
    if not str(directory.resolve()).startswith(str(USER_DIR.resolve())):
        raise ValueError("refusing to delete outside the user plugin directory")
    shutil.rmtree(directory)

