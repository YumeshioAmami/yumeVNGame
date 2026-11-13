from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import db, llm, plugins, secrets


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "web" / "dist"

app = FastAPI(title="yumeVNGame API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    premise: str = Field(min_length=4, max_length=4000)
    genre: str = "悬疑、恋爱"
    tone: str = "冷峻、克制"
    length: str = "短篇"
    extra: str = ""


class SessionCreate(BaseModel):
    story_id: str


class ChoiceRequest(BaseModel):
    choice_index: int | None = None


class SaveRequest(BaseModel):
    save_name: str = "手动存档"


class SettingsUpdate(BaseModel):
    theme: str | None = None
    model: str | None = None
    base_url: str | None = None
    tts_endpoint: str | None = None
    tts_voice: str | None = None


class SecretRequest(BaseModel):
    api_key: str = Field(min_length=8, max_length=512)
    model: str | None = None
    base_url: str | None = None


class PluginInstallRequest(BaseModel):
    filename: str
    data_base64: str


class PluginToggleRequest(BaseModel):
    enabled: bool


@app.on_event("startup")
def startup() -> None:
    db.init_db()


def _dataset_summary() -> dict[str, Any]:
    return plugins.dataset_summary()


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "service": "yumeVNGame", "version": "0.1.0"}


@app.get("/api/bootstrap")
def bootstrap() -> dict[str, Any]:
    return {
        "stories": db.list_stories(),
        "settings": db.get_settings(),
        "secrets": secrets.public_status(),
        "stats": db.stats(),
        "dataset": _dataset_summary(),
        "plugins": plugins.list_plugins(),
    }


@app.get("/api/stories")
def stories() -> list[dict[str, Any]]:
    return db.list_stories()


@app.get("/api/stories/{story_id}")
def story(story_id: str) -> dict[str, Any]:
    item = db.get_story(story_id)
    if not item:
        raise HTTPException(404, "story not found")
    return item


@app.post("/api/stories/generate")
def generate(payload: GenerateRequest) -> dict[str, Any]:
    try:
        item = llm.generate_story(
            premise=payload.premise,
            genre=payload.genre,
            tone=payload.tone,
            length=payload.length,
            extra=payload.extra,
        )
    except llm.LLMError as exc:
        raise HTTPException(502, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, f"generation failed: {exc}") from exc
    return item


@app.post("/api/sessions")
def create_session(payload: SessionCreate) -> dict[str, Any]:
    try:
        return db.session_payload(db.create_session(payload.story_id)["id"])
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str) -> dict[str, Any]:
    try:
        return db.session_payload(session_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.post("/api/sessions/{session_id}/next")
def next_scene(session_id: str) -> dict[str, Any]:
    try:
        return db.advance(session_id, None)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/api/sessions/{session_id}/choose")
def choose(session_id: str, payload: ChoiceRequest) -> dict[str, Any]:
    try:
        return db.advance(session_id, payload.choice_index)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/api/sessions/{session_id}/save")
def save_game(session_id: str, payload: SaveRequest) -> dict[str, Any]:
    try:
        return db.save_game(session_id, payload.save_name)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/api/stories/{story_id}/saves")
def saves(story_id: str) -> list[dict[str, Any]]:
    return db.list_saves(story_id)


@app.post("/api/saves/{save_id}/load")
def load_save(save_id: str) -> dict[str, Any]:
    try:
        return db.load_save(save_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/api/stories/{story_id}/gallery")
def gallery(story_id: str) -> list[dict[str, Any]]:
    return db.gallery_for_story(story_id)


@app.get("/api/settings")
def settings() -> dict[str, Any]:
    return {"settings": db.get_settings(), "secrets": secrets.public_status()}


@app.put("/api/settings")
def update_settings(payload: SettingsUpdate) -> dict[str, Any]:
    values = {key: value for key, value in payload.model_dump().items() if value is not None}
    return {"settings": db.set_settings(values), "secrets": secrets.public_status()}


@app.post("/api/settings/secret")
def set_secret(payload: SecretRequest) -> dict[str, Any]:
    secrets.set_secret("deepseek_api_key", payload.api_key.strip())
    values: dict[str, str] = {}
    if payload.model:
        values["model"] = payload.model
    if payload.base_url:
        values["base_url"] = payload.base_url
    if values:
        db.set_settings(values)
    return {"settings": db.get_settings(), "secrets": secrets.public_status()}


@app.delete("/api/settings/secret")
def delete_secret() -> dict[str, Any]:
    secrets.delete_secret("deepseek_api_key")
    return {"settings": db.get_settings(), "secrets": secrets.public_status()}


@app.get("/api/tts/status")
def tts_status() -> dict[str, Any]:
    settings = db.get_settings()
    return {
        "mode": "browser" if not settings.get("tts_endpoint") else "gpt_sovits",
        "endpoint_configured": bool(settings.get("tts_endpoint")),
    }


@app.post("/api/tts")
def tts(payload: dict[str, Any]) -> dict[str, Any]:
    settings = db.get_settings()
    text = str(payload.get("text", ""))[:1200]
    endpoint = settings.get("tts_endpoint", "").strip()
    if not endpoint:
        return {
            "mode": "browser",
            "text": text,
            "message": "未配置 GPT-SoVITS，使用浏览器语音合成。",
        }
    body = {
        "text": text,
        "text_lang": payload.get("text_lang", "zh"),
        "prompt_lang": payload.get("prompt_lang", "zh"),
        "voice": settings.get("tts_voice", ""),
        "speaker": settings.get("tts_voice", ""),
    }
    errors: list[str] = []
    for url in [endpoint, endpoint.rstrip("/") + "/tts"]:
        try:
            response = requests.post(url, json=body, timeout=60)
            content_type = response.headers.get("content-type", "")
            if response.ok and ("audio" in content_type or response.content[:4] in (b"RIFF", b"OggS", b"ID3\x03")):
                return {
                    "mode": "gpt_sovits",
                    "mime": content_type or "audio/wav",
                    "audio_base64": base64.b64encode(response.content).decode("ascii"),
                }
            if response.ok:
                try:
                    data = response.json()
                except Exception:
                    data = {"detail": response.text[:300]}
                return {"mode": "gpt_sovits", "response": data}
            errors.append(f"{url}: HTTP {response.status_code}")
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    return {"mode": "gpt_sovits_error", "detail": "; ".join(errors)[:600], "text": text}


@app.get("/api/dataset")
def dataset() -> dict[str, Any]:
    summary = _dataset_summary()
    return {"summary": summary, "preview": plugins.dataset_preview()}


@app.get("/api/plugins")
def plugin_list() -> list[dict[str, Any]]:
    return plugins.list_plugins()


@app.post("/api/plugins/install")
def plugin_install(payload: PluginInstallRequest) -> dict[str, Any]:
    try:
        return plugins.install_plugin_zip(payload.filename, payload.data_base64)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.put("/api/plugins/{plugin_id}")
def plugin_toggle(plugin_id: str, payload: PluginToggleRequest) -> dict[str, Any]:
    try:
        return plugins.set_enabled(plugin_id, payload.enabled)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.delete("/api/plugins/{plugin_id}")
def plugin_delete(plugin_id: str) -> dict[str, Any]:
    try:
        plugins.delete_plugin(plugin_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"ok": True}


if DIST.exists():
    app.mount("/", StaticFiles(directory=str(DIST), html=True), name="web")
else:
    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "service": "yumeVNGame",
            "message": "Frontend dev server: http://localhost:5173",
            "api": "/api/health",
        }

