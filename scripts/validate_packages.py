from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from server import db


ASSETS = ROOT / "web" / "public" / "assets"


def main() -> None:
    db.init_db()
    stories = db.list_stories()
    errors: list[str] = []
    for summary in stories:
        story = db.get_story(summary["id"])
        package = story["package"]
        node_ids = {node["id"] for node in package.get("nodes", [])}
        characters = {character["id"]: character for character in package.get("characters", [])}
        for node in package.get("nodes", []):
            scene = node.get("scene") or {}
            mode = scene.get("visual_mode")
            if not scene.get("background") and not scene.get("cg"):
                errors.append(f"{story['id']}/{node['id']}: no background or CG")
            if mode == "cg" and not scene.get("cg"):
                errors.append(f"{story['id']}/{node['id']}: CG mode without CG")
            if mode != "cg" and not scene.get("background"):
                errors.append(f"{story['id']}/{node['id']}: background mode without background")
            if scene.get("background") and not (ASSETS / "backgrounds" / f"{scene['background']}.svg").exists():
                errors.append(f"{story['id']}/{node['id']}: missing background asset {scene['background']}")
            if scene.get("cg") and not (ASSETS / "cg" / f"{scene['cg']}.svg").exists():
                errors.append(f"{story['id']}/{node['id']}: missing CG asset {scene['cg']}")
            for cast in scene.get("cast") or []:
                character = characters.get(cast.get("character"))
                if not character:
                    errors.append(f"{story['id']}/{node['id']}: unknown cast {cast.get('character')}")
                    continue
                sprite = ASSETS / "sprites" / f"{character['sprite']}_{cast.get('expression', 'calm')}.svg"
                if not sprite.exists():
                    errors.append(f"{story['id']}/{node['id']}: missing sprite {sprite.name}")
            for choice in node.get("choices") or []:
                if choice.get("to") not in node_ids:
                    errors.append(f"{story['id']}/{node['id']}: invalid choice target {choice.get('to')}")
            if node.get("next") and node["next"] not in node_ids:
                errors.append(f"{story['id']}/{node['id']}: invalid next {node['next']}")
        if not any(node.get("ending") for node in package.get("nodes", [])):
            errors.append(f"{story['id']}: no ending")

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"OK: {len(stories)} story packages validated")


if __name__ == "__main__":
    main()

