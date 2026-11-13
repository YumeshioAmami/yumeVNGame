# yumeVNGame

[English](README.md) | [简体中文](README.zh-CN.md)

[![CI](https://github.com/YumeshioAmami/yumeVNGame/actions/workflows/ci.yml/badge.svg)](https://github.com/YumeshioAmami/yumeVNGame/actions/workflows/ci.yml)

> A local-first, AI-native visual novel **desktop application**. Stories are compiled as complete narrative packages — not improvised chat — then rendered with backgrounds, sprites, CG, branching, saves, and a memory gallery.

Repository: <https://github.com/YumeshioAmami/yumeVNGame>

**Current status: `0.1.0` source prototype.** This is not a packaged release. `1.0.0` is reserved for after user acceptance and after real image / audio backends are connected.

![Home](docs/screenshots/home.jpg)

## Desktop application

yumeVNGame runs as a native desktop window, not as a website.

- **Desktop shell:** Python + PyWebView (WebView2 on Windows)
- **Local backend:** FastAPI on `127.0.0.1`
- **Local storage:** SQLite + local asset / plugin directories
- **Launch:** `start.bat` or `start.ps1`
- **Development only:** `dev.bat` or `npm run dev` (Vite + API in a browser)

The desktop app starts the local API, builds the frontend bundle if needed, opens the native window, and shuts the local API down when the window closes.

## What it is

- **Not an AI companion chatbot.** The model first designs a complete story graph, then renders scenes.
- **Visual novel first.** Every scene must have a background or CG. Sprites appear when characters appear; CG scenes never stack sprites.
- **Branching and memory.** Choices, endings, saves, CG replay, scene replay, and sprite differential viewing are first-class features.
- **Bring your own model.** DeepSeek-compatible chat completions are supported first; the model layer is intentionally replaceable.
- **Local secrets.** API keys are encrypted at rest in the user data directory, never committed to the repository.
- **External content packs.** Datasets, worlds, stories, music, images, voice and asset packs are plugins, not core content.

## Features

### Story runtime

- Native desktop window with local FastAPI backend;
- Full-screen visual novel stage;
- Typewriter dialogue, narration, speaker colors;
- Branch choices with hints;
- Backgrounds with time-of-day / mood filters;
- Sprite layers with expression differentials;
- Special CG scenes that hide sprites;
- Endings with gallery unlock;
- Browser TTS + generic GPT-SoVITS HTTP adapter.

### Story compiler

- Natural-language premise → structured story package;
- 8–12 nodes, multiple choices, 2–3 endings;
- Character sheets, background usage, sprite differentials, CG nodes;
- Strict JSON output and package normalization;
- Built-in fallback demo story if no key is configured.

### Progress & gallery

- Local SQLite saves;
- Save / load with current node, history, visited nodes and choices;
- CG gallery;
- Scene replay;
- Sprite differential viewer;
- Ending collection;
- Unlock state persisted per local player.

### Plugin system

```text
dataset      style / structure / few-shot / RAG data
world        world canon, rules, locations, factions, lore
story        complete story packages or story chains
music        themes, tracks, cues
image        backgrounds, sprites, CG, UI packs
voice        voice profiles / reference audio
asset_pack   bundled mixed assets
theme        UI theme packs
```

The first implemented type is `dataset`. Users install `.zip` packs from **Settings → External dataset / plugins**. The core repository ships only an original example dataset plugin, not third-party plot summaries or commercial game content.

See `docs/PLUGIN_SYSTEM.md` and `datasets/README.md`.

## Screenshots

| Story library | Story compiler |
|---|---|
| ![Library](docs/screenshots/home.jpg) | ![Compiler](docs/screenshots/create.jpg) |

| VN player | Branch choices |
|---|---|
| ![Player](docs/screenshots/player.jpg) | ![Choices](docs/screenshots/choices.jpg) |

| Memory gallery | Settings / plugins |
|---|---|
| ![Gallery](docs/screenshots/gallery.jpg) | ![Settings](docs/screenshots/settings.jpg) |

## Tech stack

- Desktop shell: Python + PyWebView
- Backend: FastAPI + SQLite
- Frontend: React 18 + TypeScript + Vite + Framer Motion + Lucide
- Model: OpenAI-compatible chat completions (DeepSeek by default)
- Assets: local procedural SVG concept backgrounds, sprites and CG placeholders
- Storage: local SQLite + encrypted local secrets

## Quick start

Requirements:

- Windows 10/11 with WebView2 runtime
- Node.js 20+
- Python 3.10+

```bash
npm install
pip install -r requirements.txt
```

Then double-click:

```text
start.bat
```

Or run:

```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```

The desktop launcher installs missing dependencies, builds the frontend if needed, starts the local API and opens the native application window.

For development only:

```text
dev.bat
```

## Configure a text model

### Option A: Settings UI

Open **Settings → Text model**, paste your API key, choose model / base URL, then save.

### Option B: Environment + encrypted store

```powershell
$env:DEEPSEEK_API_KEY="sk-your-key"
$env:DEEPSEEK_MODEL="deepseek-chat"
python scripts/set_secret.py
```

The key is saved encrypted at:

```text
%APPDATA%\yumeVNGame\secrets.enc
```

The master key is stored separately at `%APPDATA%\yumeVNGame\master.key`. Neither file is inside the repository.

## External dataset packs

The core repository intentionally ships **no third-party plot summaries, game scripts, images, music, or voice assets**.

Build an external research pack:

```bash
python scripts/build_text_dataset.py
python scripts/package_dataset_plugin.py
```

Outputs:

```text
datasets/local/text_vn/                 # gitignored local pack
dist_plugins/text-vn-official-0.1.0.zip # installable plugin pack
```

Install the zip from **Settings → External dataset / plugins**. The pack is stored in:

```text
%APPDATA%\yumeVNGame\plugins\<plugin-id>\
```

## Architecture

```text
desktop.py            native desktop launcher (PyWebView + local API)
web/                  React UI, VN player, compiler, gallery, settings
server/               FastAPI API, SQLite layer, DeepSeek client, encrypted secrets, plugins
scripts/              asset generation, dataset builder, packaging, smoke tests, validators
plugins/              plugin format + original example dataset plugin
datasets/             external dataset workspace (local packs gitignored)
docs/                 design documents, plugin system, prototype notes, screenshots
data/                 local runtime database (gitignored)
```

Key design documents:

- `docs/PROJECT_PLAN.md`
- `docs/AGENT_AND_PRODUCTION.md`
- `docs/DATA_MODEL_V0.md`
- `docs/DATA_AND_QUALITY.md`
- `docs/MODEL_AND_DEGRADATION.md`
- `docs/PLUGIN_SYSTEM.md`
- `docs/MVP_PLAN.md`
- `docs/PROTOTYPE_NOTES.md`

## Verification

```bash
# Frontend type-check
npx tsc --noEmit -p web/tsconfig.json

# Frontend build
npm run build

# Validate all story packages and visual assets
python scripts/validate_packages.py

# API smoke test (server must be running)
python scripts/smoke_test.py

# Include a real model generation test
python scripts/smoke_test.py --generate

# Local browser UI smoke test (development)
npm run test:ui

# Native desktop launch test (auto-closes after 4 seconds)
$env:YUME_AUTO_CLOSE_MS="4000"; python desktop.py
```

## 0.1.0 boundaries and 1.0.0 gate

Working:

- native desktop launcher;
- text generation through DeepSeek-compatible API;
- complete story package generation;
- branching playback;
- save / load;
- CG / scene / sprite / ending gallery;
- local encrypted key storage;
- external dataset / plugin pack system;
- source launcher (`start.bat` / `start.ps1`).

Not yet in 0.1.0:

- packaged installer / standalone build;
- real image generation backend;
- real music generation backend;
- tested GPT-SoVITS voice backend (adapter exists, browser TTS fallback works);
- full production editor;
- Ren'Py export;
- cloud sync and multiplayer.

`1.0.0` is gated on user acceptance, real image / audio backends, and a packaged distribution decision.

## Security

- No API key is committed to the repository.
- Secrets are encrypted with Fernet.
- The local backend binds to `127.0.0.1` by default.
- Story data and saves stay in local SQLite.
- Plugin archives are validated and extracted outside the repository.
- The app does not upload keys to any third-party storage; model calls go directly to the configured endpoint.

## License

MIT. See [LICENSE](LICENSE).

