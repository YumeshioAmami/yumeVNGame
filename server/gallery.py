from __future__ import annotations

import uuid
from typing import Any


def _image_for_node(node: dict[str, Any], package: dict[str, Any]) -> str:
    scene = node.get("scene") or {}
    if scene.get("cg"):
        return f"/assets/cg/{scene['cg']}.svg"
    if scene.get("background"):
        return f"/assets/backgrounds/{scene['background']}.svg"
    return f"/assets/backgrounds/{package.get('cover', 'rain_classroom')}.svg"


def build_gallery_entries(package: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    order = 0

    for node in package.get("nodes", []):
        node_id = node.get("id")
        if not node_id:
            continue
        title = node.get("title") or node_id
        image = _image_for_node(node, package)

        entries.append(
            {
                "id": uuid.uuid4().hex,
                "entry_key": f"scene:{node_id}",
                "entry_type": "scene",
                "title": title,
                "image": image,
                "node_id": node_id,
                "payload_json": {"node_id": node_id},
                "sort_order": order,
            }
        )
        order += 1

        scene = node.get("scene") or {}
        if scene.get("cg"):
            entries.append(
                {
                    "id": uuid.uuid4().hex,
                    "entry_key": f"cg:{node_id}",
                    "entry_type": "cg",
                    "title": title,
                    "image": image,
                    "node_id": node_id,
                    "payload_json": {"node_id": node_id, "cg": scene["cg"]},
                    "sort_order": order,
                }
            )
            order += 1

        ending = node.get("ending")
        if ending:
            entries.append(
                {
                    "id": uuid.uuid4().hex,
                    "entry_key": f"ending:{ending.get('id', node_id)}",
                    "entry_type": "ending",
                    "title": ending.get("title") or title,
                    "image": image,
                    "node_id": node_id,
                    "payload_json": ending,
                    "sort_order": order,
                }
            )
            order += 1

    for character in package.get("characters", []):
        char_id = character.get("id")
        if not char_id:
            continue
        sprite = character.get("sprite") or char_id
        entries.append(
            {
                "id": uuid.uuid4().hex,
                "entry_key": f"sprite:{char_id}",
                "entry_type": "sprite_differential",
                "title": f"{character.get('name', char_id)} · 立绘差分",
                "image": f"/assets/sprites/{sprite}_calm.svg",
                "node_id": None,
                "payload_json": {
                    "character_id": char_id,
                    "sprite": sprite,
                    "expressions": character.get("expressions", ["calm"]),
                },
                "sort_order": order,
            }
        )
        order += 1

    return entries

