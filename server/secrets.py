from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken


def _app_dir() -> Path:
    base = os.getenv("APPDATA") or str(Path.home() / ".config")
    path = Path(base) / "yumeVNGame"
    path.mkdir(parents=True, exist_ok=True)
    return path


APP_DIR = _app_dir()
MASTER_KEY_PATH = APP_DIR / "master.key"
SECRETS_PATH = APP_DIR / "secrets.enc"

PROVIDERS: dict[str, dict[str, str]] = {
    "deepseek": {"name": "DeepSeek", "kind": "text", "key_name": "deepseek_api_key"},
    "fal": {"name": "fal.ai", "kind": "image", "key_name": "fal_api_key"},
    "replicate": {"name": "Replicate", "kind": "image", "key_name": "replicate_api_key"},
    "novelai": {"name": "NovelAI", "kind": "image", "key_name": "novelai_api_key"},
    "stability": {"name": "Stability AI", "kind": "music", "key_name": "stability_api_key"},
    "elevenlabs": {"name": "ElevenLabs", "kind": "music", "key_name": "elevenlabs_api_key"},
}


def _fernet() -> Fernet:
    if not MASTER_KEY_PATH.exists():
        MASTER_KEY_PATH.write_bytes(Fernet.generate_key())
        try:
            os.chmod(MASTER_KEY_PATH, 0o600)
        except OSError:
            pass
    return Fernet(MASTER_KEY_PATH.read_bytes().strip())


def load_all() -> dict[str, Any]:
    if not SECRETS_PATH.exists():
        return {}
    try:
        raw = _fernet().decrypt(SECRETS_PATH.read_bytes())
        data = json.loads(raw.decode("utf-8"))
        return data if isinstance(data, dict) else {}
    except (InvalidToken, json.JSONDecodeError, OSError):
        return {}


def save_all(data: dict[str, Any]) -> None:
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    SECRETS_PATH.write_bytes(_fernet().encrypt(payload))
    try:
        os.chmod(SECRETS_PATH, 0o600)
    except OSError:
        pass


def set_secret(name: str, value: str) -> None:
    data = load_all()
    data[name] = value
    save_all(data)


def get_secret(name: str) -> str | None:
    value = load_all().get(name)
    return str(value) if value else None


def delete_secret(name: str) -> None:
    data = load_all()
    data.pop(name, None)
    save_all(data)


def mask(value: str | None) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "•" * len(value)
    return f"{value[:4]}{'•' * 8}{value[-4:]}"


def deepseek_key() -> str | None:
    return get_secret("deepseek_api_key")


def has_deepseek_key() -> bool:
    return bool(deepseek_key())


def provider_key(provider: str) -> str | None:
    meta = PROVIDERS.get(provider)
    return get_secret(meta["key_name"]) if meta else None


def set_provider_key(provider: str, value: str) -> None:
    meta = PROVIDERS.get(provider)
    if not meta:
        raise ValueError(f"unknown provider: {provider}")
    value = value.strip()
    if not value:
        raise ValueError("api key cannot be empty")
    set_secret(meta["key_name"], value)


def delete_provider_key(provider: str) -> None:
    meta = PROVIDERS.get(provider)
    if not meta:
        raise ValueError(f"unknown provider: {provider}")
    delete_secret(meta["key_name"])


def public_status() -> dict[str, Any]:
    key = deepseek_key()
    providers = {}
    for provider, meta in PROVIDERS.items():
        value = get_secret(meta["key_name"])
        providers[provider] = {
            "id": provider,
            "name": meta["name"],
            "kind": meta["kind"],
            "has_key": bool(value),
            "masked_key": mask(value),
        }
    return {
        "has_api_key": bool(key),
        "masked_key": mask(key),
        "storage": str(SECRETS_PATH),
        "providers": providers,
    }

