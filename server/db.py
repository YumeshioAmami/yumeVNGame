from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .demo_story import DEMO_STORY
from .gallery import build_gallery_entries


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("YUME_DATA_DIR", ROOT / "data"))
DB_PATH = DATA_DIR / "yumevn.db"
PLAYER_ID = "local-player"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def _json(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def init_db() -> None:
    schema = (Path(__file__).with_name("schema.sql")).read_text(encoding="utf-8")
    with _connect() as conn:
        conn.executescript(schema)
        conn.execute(
            "INSERT OR IGNORE INTO player_profiles(id, name, created_at) VALUES (?, ?, ?)",
            (PLAYER_ID, "本地玩家", now()),
        )
        conn.execute(
            "INSERT OR IGNORE INTO schema_meta(version, applied_at) VALUES (1, ?)",
            (now(),),
        )
        count = conn.execute("SELECT COUNT(*) AS n FROM stories").fetchone()["n"]
        if count == 0:
            _save_story(conn, DEMO_STORY, source="demo", story_id="demo-mistharbor")


def _normalise_package(package: dict[str, Any]) -> dict[str, Any]:
    package = dict(package)
    package.setdefault("title", "未命名故事")
    package.setdefault("logline", "")
    package.setdefault("synopsis", "")
    package.setdefault("genre", [])
    package.setdefault("tone", "克制")
    package.setdefault("theme", "选择与后果")
    package.setdefault("cover", "rain_classroom")
    package.setdefault("characters", [])
    nodes = package.get("nodes") or []
    if not nodes:
        raise ValueError("story package needs at least one node")
    node_ids = {node.get("id") for node in nodes if node.get("id")}
    if not package.get("start_node") or package["start_node"] not in node_ids:
        package["start_node"] = nodes[0]["id"]
    for index, node in enumerate(nodes):
        node.setdefault("id", f"n_{index + 1}")
        node.setdefault("title", f"场景 {index + 1}")
        node.setdefault("type", "scene")
        node.setdefault("speaker", "旁白")
        node.setdefault("narration", "")
        node.setdefault("text", "……")
        scene = node.get("scene") or {}
        scene.setdefault("visual_mode", "background_only")
        scene.setdefault("background", "rain_classroom")
        scene.setdefault("cg", None)
        scene.setdefault("filter", "cool")
        scene.setdefault("cast", [])
        if scene["visual_mode"] == "cg" and not scene.get("cg"):
            scene["cg"] = "cg_letter"
        if scene["visual_mode"] != "cg" and not scene.get("background"):
            scene["background"] = "rain_classroom"
        node["scene"] = scene
        choices = []
        for choice in node.get("choices") or []:
            if choice.get("to") in node_ids:
                choices.append(choice)
        if choices:
            node["choices"] = choices
        if node.get("next") not in node_ids:
            node.pop("next", None)
    has_ending = any(node.get("ending") for node in nodes)
    if not has_ending:
        last = nodes[-1]
        last["type"] = "ending"
        last["ending"] = {
            "id": f"end_{last['id']}",
            "title": last.get("title", "结局"),
            "type": "neutral",
            "description": "故事在这里结束。",
        }
    return package


def _save_story(
    conn: sqlite3.Connection,
    package: dict[str, Any],
    source: str,
    story_id: str | None = None,
) -> dict[str, Any]:
    package = _normalise_package(package)
    story_id = story_id or uuid.uuid4().hex[:12]
    stamp = now()
    conn.execute(
        """
        INSERT OR REPLACE INTO stories
        (id, title, logline, synopsis, genre_json, tone, theme, cover,
         package_json, source, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ready', ?, ?)
        """,
        (
            story_id,
            package.get("title", "未命名故事"),
            package.get("logline", ""),
            package.get("synopsis", ""),
            json.dumps(package.get("genre", []), ensure_ascii=False),
            package.get("tone", ""),
            package.get("theme", ""),
            package.get("cover", "rain_classroom"),
            json.dumps(package, ensure_ascii=False),
            source,
            stamp,
            stamp,
        ),
    )
    conn.execute("DELETE FROM gallery_entries WHERE story_id = ?", (story_id,))
    for entry in build_gallery_entries(package):
        conn.execute(
            """
            INSERT INTO gallery_entries
            (id, story_id, entry_key, entry_type, title, image, node_id, payload_json, sort_order, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry["id"],
                story_id,
                entry["entry_key"],
                entry["entry_type"],
                entry["title"],
                entry["image"],
                entry["node_id"],
                json.dumps(entry["payload_json"], ensure_ascii=False),
                entry["sort_order"],
                stamp,
            ),
        )
    return {"id": story_id, "title": package.get("title", ""), "package": package}


def save_story_package(package: dict[str, Any], source: str = "ai") -> dict[str, Any]:
    with _connect() as conn:
        result = _save_story(conn, package, source=source)
    return get_story(result["id"]) or result


def list_stories() -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM stories ORDER BY updated_at DESC"
        ).fetchall()
    stories = []
    for row in rows:
        item = dict(row)
        package = _json(item.pop("package_json", ""), {})
        item["genre"] = _json(item.pop("genre_json", "[]"), [])
        item["node_count"] = len(package.get("nodes", []))
        item["ending_count"] = sum(1 for node in package.get("nodes", []) if node.get("ending"))
        item["character_count"] = len(package.get("characters", []))
        stories.append(item)
    return stories


def get_story(story_id: str) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM stories WHERE id = ?", (story_id,)).fetchone()
    if not row:
        return None
    item = dict(row)
    package = _json(item.pop("package_json", ""), {})
    item["genre"] = _json(item.pop("genre_json", "[]"), [])
    item["package"] = package
    return item


def get_story_package(story_id: str) -> dict[str, Any] | None:
    story = get_story(story_id)
    return story["package"] if story else None


def _get_node(package: dict[str, Any], node_id: str) -> dict[str, Any] | None:
    return next((node for node in package.get("nodes", []) if node.get("id") == node_id), None)


def create_session(story_id: str, player_id: str = PLAYER_ID) -> dict[str, Any]:
    package = get_story_package(story_id)
    if not package:
        raise ValueError("story not found")
    start = package.get("start_node")
    session_id = uuid.uuid4().hex
    stamp = now()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO sessions
            (id, story_id, player_id, current_node_id, visited_json, choices_json,
             history_json, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, '[]', '[]', 'active', ?, ?)
            """,
            (session_id, story_id, player_id, start, json.dumps([start], ensure_ascii=False), stamp, stamp),
        )
        _unlock_node_gallery(conn, package, story_id, player_id, start)
    return get_session(session_id) or {}


def get_session(session_id: str) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if not row:
        return None
    session = dict(row)
    session["visited"] = _json(session.pop("visited_json", "[]"), [])
    session["choices"] = _json(session.pop("choices_json", "[]"), [])
    session["history"] = _json(session.pop("history_json", "[]"), [])
    return session


def session_payload(session_id: str) -> dict[str, Any]:
    session = get_session(session_id)
    if not session:
        raise ValueError("session not found")
    story = get_story(session["story_id"])
    if not story:
        raise ValueError("story not found")
    node = _get_node(story["package"], session["current_node_id"])
    return {"session": session, "story": story, "node": node}


def _unlock_node_gallery(
    conn: sqlite3.Connection,
    package: dict[str, Any],
    story_id: str,
    player_id: str,
    node_id: str,
) -> list[str]:
    node = _get_node(package, node_id)
    if not node:
        return []
    keys = {f"scene:{node_id}"}
    scene = node.get("scene") or {}
    if scene.get("cg"):
        keys.add(f"cg:{node_id}")
    ending = node.get("ending")
    if ending:
        keys.add(f"ending:{ending.get('id', node_id)}")
    for cast in scene.get("cast") or []:
        keys.add(f"sprite:{cast.get('character')}")
    unlocked: list[str] = []
    for key in keys:
        row = conn.execute(
            "SELECT id FROM gallery_entries WHERE story_id = ? AND entry_key = ?",
            (story_id, key),
        ).fetchone()
        if not row:
            continue
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO gallery_unlocks(id, player_id, entry_id, unlocked_at)
            VALUES (?, ?, ?, ?)
            """,
            (uuid.uuid4().hex, player_id, row["id"], now()),
        )
        if cursor.rowcount:
            unlocked.append(key)
    return unlocked


def advance(session_id: str, choice_index: int | None = None) -> dict[str, Any]:
    session = get_session(session_id)
    if not session:
        raise ValueError("session not found")
    story = get_story(session["story_id"])
    if not story:
        raise ValueError("story not found")
    package = story["package"]
    current = _get_node(package, session["current_node_id"])
    if not current:
        raise ValueError("current node not found")
    if current.get("type") == "ending" or current.get("ending"):
        raise ValueError("story has ended")

    target: str | None = None
    choice_text = "继续"
    if current.get("choices"):
        if choice_index is None or not (0 <= choice_index < len(current["choices"])):
            raise ValueError("choice_index out of range")
        choice = current["choices"][choice_index]
        target = choice.get("to")
        choice_text = choice.get("text", "选择")
    else:
        target = current.get("next")
        choice_text = "继续"
    if not target or not _get_node(package, target):
        raise ValueError("invalid next node")

    visited = session["visited"]
    if not visited or visited[-1] != target:
        visited.append(target)
    choices = session["choices"]
    choices.append({"node": current["id"], "choice": choice_text, "to": target})
    history = session["history"]
    history.append(
        {
            "node": current["id"],
            "speaker": current.get("speaker", ""),
            "narration": current.get("narration", ""),
            "text": current.get("text", ""),
        }
    )
    target_node = _get_node(package, target)
    status = "completed" if target_node and (target_node.get("type") == "ending" or target_node.get("ending")) else "active"
    with _connect() as conn:
        conn.execute(
            """
            UPDATE sessions
            SET current_node_id = ?, visited_json = ?, choices_json = ?,
                history_json = ?, status = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                target,
                json.dumps(visited, ensure_ascii=False),
                json.dumps(choices, ensure_ascii=False),
                json.dumps(history, ensure_ascii=False),
                status,
                now(),
                session_id,
            ),
        )
        newly = _unlock_node_gallery(conn, package, session["story_id"], session["player_id"], target)
    payload = session_payload(session_id)
    payload["newly_unlocked"] = newly
    return payload


def save_game(session_id: str, save_name: str = "手动存档") -> dict[str, Any]:
    session = get_session(session_id)
    if not session:
        raise ValueError("session not found")
    save_id = uuid.uuid4().hex
    stamp = now()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO saves
            (id, session_id, story_id, player_id, save_name, current_node_id,
             visited_json, choices_json, history_json, state_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                save_id,
                session_id,
                session["story_id"],
                session["player_id"],
                save_name,
                session["current_node_id"],
                json.dumps(session["visited"], ensure_ascii=False),
                json.dumps(session["choices"], ensure_ascii=False),
                json.dumps(session["history"], ensure_ascii=False),
                json.dumps({"current_node_id": session["current_node_id"]}, ensure_ascii=False),
                stamp,
            ),
        )
    return get_save(save_id) or {}


def get_save(save_id: str) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM saves WHERE id = ?", (save_id,)).fetchone()
    if not row:
        return None
    item = dict(row)
    item["visited"] = _json(item.pop("visited_json", "[]"), [])
    item["choices"] = _json(item.pop("choices_json", "[]"), [])
    item["history"] = _json(item.pop("history_json", "[]"), [])
    item["state"] = _json(item.pop("state_json", "{}"), {})
    return item


def list_saves(story_id: str, player_id: str = PLAYER_ID) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM saves WHERE story_id = ? AND player_id = ? ORDER BY created_at DESC",
            (story_id, player_id),
        ).fetchall()
    saves = []
    for row in rows:
        item = dict(row)
        item["visited"] = _json(item.pop("visited_json", "[]"), [])
        item["choices"] = _json(item.pop("choices_json", "[]"), [])
        item["history"] = _json(item.pop("history_json", "[]"), [])
        item["state"] = _json(item.pop("state_json", "{}"), {})
        saves.append(item)
    return saves


def load_save(save_id: str) -> dict[str, Any]:
    save = get_save(save_id)
    if not save:
        raise ValueError("save not found")
    session_id = uuid.uuid4().hex
    stamp = now()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO sessions
            (id, story_id, player_id, current_node_id, visited_json, choices_json,
             history_json, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
            """,
            (
                session_id,
                save["story_id"],
                save["player_id"],
                save["current_node_id"],
                json.dumps(save["visited"], ensure_ascii=False),
                json.dumps(save["choices"], ensure_ascii=False),
                json.dumps(save["history"], ensure_ascii=False),
                stamp,
                stamp,
            ),
        )
    return session_payload(session_id)


def gallery_for_story(story_id: str, player_id: str = PLAYER_ID) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT ge.*, CASE WHEN gu.id IS NULL THEN 0 ELSE 1 END AS unlocked
            FROM gallery_entries ge
            LEFT JOIN gallery_unlocks gu
              ON gu.entry_id = ge.id AND gu.player_id = ?
            WHERE ge.story_id = ?
            ORDER BY ge.entry_type, ge.sort_order
            """,
            (player_id, story_id),
        ).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["unlocked"] = bool(item["unlocked"])
        item["payload"] = _json(item.pop("payload_json", "{}"), {})
        items.append(item)
    return items


def stats(player_id: str = PLAYER_ID) -> dict[str, int]:
    with _connect() as conn:
        stories = conn.execute("SELECT COUNT(*) AS n FROM stories").fetchone()["n"]
        saves = conn.execute("SELECT COUNT(*) AS n FROM saves WHERE player_id = ?", (player_id,)).fetchone()["n"]
        unlocks = conn.execute(
            "SELECT COUNT(*) AS n FROM gallery_unlocks WHERE player_id = ?", (player_id,)
        ).fetchone()["n"]
        sessions = conn.execute(
            "SELECT COUNT(*) AS n FROM sessions WHERE player_id = ?", (player_id,)
        ).fetchone()["n"]
    return {"stories": stories, "saves": saves, "gallery_unlocks": unlocks, "sessions": sessions}


def get_settings() -> dict[str, Any]:
    defaults = {
        "theme": "morning",
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
        "tts_endpoint": "",
        "tts_voice": "",
        "image_provider": "nanogpt",
        "music_provider": "stability",
        "image_agent_distant": "pixelwave",
        "image_agent_scene": "prunaai:1@1",
        "image_agent_special_cg": "seedream-v4.5",
        "image_agent_draft": "blackforestlabs/flux-3/klein/edit-image",
        "image_agent_character_final": "bytedance/seedream-v5.0-flash",
        "image_agent_character_diff": "blackforestlabs/flux-3/klein/edit-image",
    }
    with _connect() as conn:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
    for row in rows:
        defaults[row["key"]] = row["value"]
    return defaults


def set_settings(values: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "theme",
        "model",
        "base_url",
        "tts_endpoint",
        "tts_voice",
        "image_provider",
        "music_provider",
        "image_agent_distant",
        "image_agent_scene",
        "image_agent_special_cg",
        "image_agent_draft",
        "image_agent_character_final",
        "image_agent_character_diff",
    }
    with _connect() as conn:
        for key, value in values.items():
            if key in allowed:
                conn.execute(
                    "INSERT OR REPLACE INTO settings(key, value) VALUES (?, ?)",
                    (key, str(value)),
                )
    return get_settings()


def get_setting(key: str, default: str | None = None) -> str | None:
    with _connect() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO settings(key, value) VALUES (?, ?)",
            (key, str(value)),
        )

