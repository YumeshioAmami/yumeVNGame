from __future__ import annotations

import json
import re
from typing import Any

import requests

from . import db, plugins, secrets


ALLOWED_BACKGROUNDS = [
    "rain_classroom",
    "school_corridor",
    "old_port",
    "dorm_night",
    "rooftop_rain",
    "void",
    "library",
    "station",
]
ALLOWED_CG = ["cg_letter", "cg_truth", "cg_rain"]
ALLOWED_SPRITES = {
    "rin": ["calm", "smile", "sad", "surprised"],
    "keeper": ["calm", "grim", "sad"],
    "teacher": ["calm", "sad"],
    "you": ["calm", "surprised"],
}


SYSTEM_PROMPT = f"""
你是 yumeVNGame 的故事编译导演。你的任务不是聊天，而是把用户的需求编译成一部完整、可玩的短篇视觉小说故事包。

只输出一个合法 JSON 对象。不要 Markdown，不要解释，不要代码块。

故事必须满足：
1. 8 到 10 个节点，包含至少 2 个真正的选择节点和 2 到 3 个结局。
2. 每个节点都必须有 scene。视觉小说模式下不允许没有背景或 CG 的场景。
3. 同一地点的背景优先复用；时段变化用 filter 表达，不重复生成背景。
4. 旁白节点可以没有立绘；有可见人物以立绘形式出现时必须有 cast 和表情差分；特殊 CG 节点 visual_mode 必须是 cg，cast 只能是 cg_only，不能叠加立绘。
5. 中文写作，重视氛围、潜台词、人物声音和因果；不要写成大纲，要有可直接播放的台词和旁白。
6. 不要输出露骨性描写；可以写黑暗、悬疑、恋爱、暴力后果和心理压迫。
7. 每个节点的 text 控制在 2 到 4 句，避免把整个故事写成小说长文；要留出画面和停顿。

可选背景 key：{json.dumps(ALLOWED_BACKGROUNDS, ensure_ascii=False)}
可选 CG key：{json.dumps(ALLOWED_CG, ensure_ascii=False)}
可选立绘：{json.dumps(ALLOWED_SPRITES, ensure_ascii=False)}

JSON 结构：
{{
  "title": "故事标题",
  "logline": "一句话卖点",
  "synopsis": "不剧透的简介",
  "genre": ["悬疑", "恋爱"],
  "tone": "整体基调",
  "theme": "主题",
  "cover": "rain_classroom",
  "characters": [
    {{
      "id": "rin",
      "name": "凛",
      "role": "女主角",
      "color": "#67e8f9",
      "bio": "人物简介",
      "sprite": "rin",
      "expressions": ["calm", "smile", "sad", "surprised"]
    }}
  ],
  "start_node": "n_start",
  "nodes": [
    {{
      "id": "n_start",
      "title": "场景标题",
      "type": "scene",
      "speaker": "凛",
      "narration": "旁白",
      "text": "台词",
      "scene": {{
        "visual_mode": "background_sprites",
        "background": "rain_classroom",
        "cg": null,
        "filter": "cool",
        "cast": [
          {{"character": "rin", "expression": "calm", "position": "right", "layer": 10}}
        ]
      }},
      "next": "n_choice"
    }},
    {{
      "id": "n_choice",
      "title": "选择",
      "type": "choice",
      "speaker": "旁白",
      "narration": "选择前的氛围",
      "text": "你要怎么做？",
      "scene": {{
        "visual_mode": "background_sprites",
        "background": "rain_classroom",
        "cg": null,
        "filter": "cool",
        "cast": []
      }},
      "choices": [
        {{"text": "选项 A", "to": "n_a", "hint": "暗示"}},
        {{"text": "选项 B", "to": "n_b", "hint": "暗示"}}
      ]
    }},
    {{
      "id": "n_end",
      "title": "结局标题",
      "type": "ending",
      "speaker": "旁白",
      "narration": "结局旁白",
      "text": "结局台词",
      "scene": {{
        "visual_mode": "cg",
        "background": null,
        "cg": "cg_truth",
        "filter": "warm",
        "cast": [{{"character": "rin", "expression": "smile", "position": "cg", "layer": 0}}]
      }},
      "ending": {{
        "id": "end_truth",
        "title": "真相结局",
        "type": "true",
        "description": "结局说明"
      }}
    }}
  ]
}}

注意：
- 每个 choice 的 to 必须指向存在的节点。
- 非 choice 非 ending 节点必须有 next。
- 每个 ending 节点必须有 ending 对象。
- scene.cast 里的 character 必须出现在 characters 里。
- 同一个角色在不同场景可以换表情差分。
""".strip()


class LLMError(RuntimeError):
    pass


def _style_context() -> str:
    return plugins.dataset_context(5000)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise LLMError("model did not return a JSON object")
    candidate = text[start : end + 1]
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise LLMError(f"invalid JSON from model: {exc}") from exc
    if not isinstance(data, dict):
        raise LLMError("model JSON is not an object")
    return data


def _post(messages: list[dict[str, str]], base_url: str, model: str, key: str) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.9,
        "max_tokens": 16000,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload, timeout=180)
    if response.status_code >= 400:
        # Some OpenAI-compatible gateways reject response_format. Retry once without it.
        payload.pop("response_format", None)
        response = requests.post(url, headers=headers, json=payload, timeout=180)
    if response.status_code >= 400:
        raise LLMError(f"model request failed: HTTP {response.status_code}: {response.text[:400]}")
    return response.json()


def generate_story(
    premise: str,
    genre: str = "悬疑、恋爱",
    tone: str = "冷峻、克制",
    length: str = "短篇",
    extra: str = "",
) -> dict[str, Any]:
    key = secrets.deepseek_key()
    if not key:
        raise LLMError("DeepSeek API Key 尚未配置。请先在设置中保存 API Key。")
    settings = db.get_settings()
    base_url = settings.get("base_url") or "https://api.deepseek.com"
    model = settings.get("model") or "deepseek-chat"
    style = _style_context()
    user_prompt = f"""
请生成一部{length}视觉小说。

用户前提：
{premise}

类型：{genre}
基调：{tone}
补充要求：{extra or "无"}

{'以下是我们收集的视觉小说风格参考，只用于学习节奏、人物声音和叙事结构，不要照抄任何具体作品：' + chr(10) + style if style else ''}

请现在输出完整 JSON 故事包。
""".strip()
    data = _post(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        base_url,
        model,
        key,
    )
    try:
        content = data["choices"][0]["message"].get("content") or ""
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("model response has no choices") from exc
    if not content.strip():
        reasoning = data["choices"][0]["message"].get("reasoning_content") or ""
        if reasoning:
            content = reasoning
    package = _extract_json(content)
    story = db.save_story_package(package, source="ai")
    return story

