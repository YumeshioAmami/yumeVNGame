from __future__ import annotations

import argparse
import base64
import io
import json
import sys
import zipfile

import requests


BASE = "http://127.0.0.1:8787/api"


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"PASS  {label}")
    else:
        print(f"FAIL  {label} {detail}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true", help="also test real model generation")
    args = parser.parse_args()

    health = requests.get(f"{BASE}/health", timeout=10).json()
    check("health", health.get("ok") is True, json.dumps(health, ensure_ascii=False))

    boot = requests.get(f"{BASE}/bootstrap", timeout=20).json()
    check("bootstrap", bool(boot.get("stories")), str(boot)[:200])
    check("plugins", len(boot.get("plugins", [])) >= 1, str(boot.get("plugins"))[:300])
    check(
        "dataset plugin",
        boot.get("dataset", {}).get("active_plugins", 0) >= 1
        and boot.get("dataset", {}).get("works", 0) >= 1,
        str(boot.get("dataset")),
    )

    story_id = "demo-mistharbor"
    story = requests.get(f"{BASE}/stories/{story_id}", timeout=20).json()
    package = story.get("package", {})
    check("demo package", len(package.get("nodes", [])) >= 8, f"nodes={len(package.get('nodes', []))}")
    check("visual coverage", all((n.get("scene") or {}).get("background") or (n.get("scene") or {}).get("cg") for n in package.get("nodes", [])))

    session = requests.post(f"{BASE}/sessions", json={"story_id": story_id}, timeout=20).json()
    sid = session["session"]["id"]
    check("session", session["node"]["id"] == "n_start", session["node"]["id"])

    payload = session
    for _ in range(2):
        payload = requests.post(f"{BASE}/sessions/{sid}/next", timeout=20).json()
    check("advance to choice", bool(payload["node"].get("choices")), payload["node"]["id"])
    payload = requests.post(
        f"{BASE}/sessions/{sid}/choose",
        json={"choice_index": 0},
        timeout=20,
    ).json()
    check("choose", payload["node"]["id"] == "n_old_port", payload["node"]["id"])

    save = requests.post(
        f"{BASE}/sessions/{sid}/save",
        json={"save_name": "smoke-test"},
        timeout=20,
    ).json()
    check("save", bool(save.get("id")), str(save)[:200])
    loaded = requests.post(f"{BASE}/saves/{save['id']}/load", timeout=20).json()
    check("load", loaded["node"]["id"] == "n_old_port", loaded["node"]["id"])

    gallery = requests.get(f"{BASE}/stories/{story_id}/gallery", timeout=20).json()
    check("gallery", len(gallery) >= 10, f"entries={len(gallery)}")
    check("gallery unlock", any(entry.get("unlocked") for entry in gallery))

    dataset = requests.get(f"{BASE}/dataset", timeout=20).json()
    check("dataset detail", len(dataset.get("preview", [])) >= 1, str(dataset.get("summary"))[:200])

    agents = requests.get(f"{BASE}/agent-configs", timeout=20).json().get("agents", [])
    check("agent configs", len(agents) >= 18, f"agents={len(agents)}")
    check(
        "agent categories",
        {"image", "text", "music"}.issubset({agent.get("category") for agent in agents}),
        str(sorted({agent.get("category") for agent in agents})),
    )
    text_agent = next((agent for agent in agents if agent.get("id") == "text_intake"), None)
    check("agent config detail", bool(text_agent), str(text_agent)[:200])
    if text_agent:
        original = {
            key: text_agent.get(key, "")
            for key in ("mode", "model", "base_url", "local_path", "local_endpoint")
        }
        probe = {**original, "model": text_agent.get("model", "") + "-smoke"}
        updated = requests.put(
            f"{BASE}/agent-configs/text_intake",
            json=probe,
            timeout=20,
        )
        check("agent config update", updated.status_code == 200 and updated.json()["agent"]["model"].endswith("-smoke"), updated.text[:300])
        restored = requests.put(
            f"{BASE}/agent-configs/text_intake",
            json=original,
            timeout=20,
        )
        check("agent config restore", restored.status_code == 200 and restored.json()["agent"]["model"] == text_agent.get("model"), restored.text[:300])

    # External plugin install / toggle / delete.
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "plugin.json",
            json.dumps(
                {
                    "id": "smoke-plugin",
                    "name": "Smoke Plugin",
                    "version": "0.1.0",
                    "type": "dataset",
                    "description": "temporary plugin for smoke test",
                    "enabled_by_default": False,
                    "data_file": "works.jsonl",
                }
            ),
        )
        archive.writestr(
            "works.jsonl",
            json.dumps({"title_zh": "Smoke Story", "genres": ["test"]}) + "\n",
        )
    installed = requests.post(
        f"{BASE}/plugins/install",
        json={
            "filename": "smoke-plugin.zip",
            "data_base64": base64.b64encode(buffer.getvalue()).decode("ascii"),
        },
        timeout=20,
    )
    check("plugin install", installed.status_code == 200, installed.text[:300])
    toggled = requests.put(f"{BASE}/plugins/smoke-plugin", json={"enabled": True}, timeout=20)
    check("plugin toggle", toggled.status_code == 200 and toggled.json().get("enabled") is True)
    deleted = requests.delete(f"{BASE}/plugins/smoke-plugin", timeout=20)
    check("plugin delete", deleted.status_code == 200, deleted.text[:200])

    if args.generate:
        result = requests.post(
            f"{BASE}/stories/generate",
            json={
                "premise": "雨夜校园悬疑，带一点恋爱。主角在旧教学楼收到一封来自十年前的匿名信。",
                "genre": "悬疑、恋爱",
                "tone": "冷峻、潮湿、克制",
                "length": "短篇",
                "extra": "8 到 10 个节点，至少 2 个选择点，2 个结局，至少一场雨中 CG。",
            },
            timeout=240,
        )
        check("deepseek generation", result.status_code == 200, result.text[:300])
        generated = result.json()
        check("generated package", len(generated.get("package", {}).get("nodes", [])) >= 8)

    print("ALL SMOKE TESTS PASSED")


if __name__ == "__main__":
    main()

