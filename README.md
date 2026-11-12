# yumeVNGame

> An open-source, AI-native visual novel runtime. Stories are compiled as complete narrative packages — not improvised chat — then rendered with backgrounds, sprites, CG, branching, saves, and a memory gallery.

![Home](docs/screenshots/home.jpg)

## What is this?

yumeVNGame is a local-first AI visual novel engine and story compiler.

- **Not an AI companion chatbot.** The model first designs a complete story graph, then renders scenes.
- **Visual novel first.** Every scene must have a background or CG. Sprites appear when characters appear; CG scenes never stack sprites.
- **Branching and memory.** Choices, endings, saves, CG replay, scene replay, and sprite differential viewing are first-class features.
- **Bring your own model.** DeepSeek-compatible chat completions are supported first; the model layer is intentionally replaceable.
- **Local secrets.** API keys are encrypted at rest in the user data directory, never committed to the repository.

## Screenshots

| Story library | Story compiler |
|---|---|
| ![Library](docs/screenshots/home.jpg) | ![Compiler](docs/screenshots/create.jpg) |

| VN player | Branch choices |
|---|---|
| ![Player](docs/screenshots/player.jpg) | ![Choices](docs/screenshots/choices.jpg) |

| Memory gallery | Settings |
|---|---|
| ![Gallery](docs/screenshots/gallery.jpg) | ![Settings](docs/screenshots/settings.jpg) |

## Features

### Story runtime

- Full-screen visual novel stage with glass dialogue panel;
- Typewriter dialogue, narration, speaker color, click-to-continue;
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

### UI

- Modern floating glass UI;
- Animated aurora / grid / noise background;
- Four themes: Aurora, Neon, Ember, Mono;
- Responsive layout;
- Story cards, creation pipeline, archive, control room.

## Tech stack

- Frontend: React 18 + TypeScript + Vite + Framer Motion + Lucide
- Backend: Python FastAPI + SQLite
- Model: OpenAI-compatible chat completions (DeepSeek by default)
- Assets: local procedural SVG concept backgrounds, sprites and CG placeholders
- Storage: local SQLite + encrypted local secrets

## Quick start

Requirements:

- Node.js 20+
- Python 3.10+

```bash
npm install
pip install -r requirements.txt
```

Start the local API and Vite dev server:

```bash
npm run dev
```

Open `http://localhost:5173`.

Production build:

```bash
npm run build
npm start
```

Then open `http://127.0.0.1:8787`.

## Configure a text model

### Option A: Settings UI

Open **设置 → 文本模型**, paste your API key, choose model / base URL, then save.

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

The master key is stored separately at `%APPDATA%\yumeVNGame\master.key`.  
Neither file is inside the repository.

> The model name is configurable. `deepseek-chat` is the default because it produces stable structured JSON faster through the tested OpenAI-compatible endpoint.

## Dataset

The text dataset lives at `datasets/text_vn/`.

- 17 real visual novel works;
- Chinese plot summaries from public encyclopedia sources;
- editorial metadata: genres, themes, narrative devices, pacing and character notes;
- source URLs and license notes;
- style notes for prompting.

Rebuild:

```bash
python scripts/build_text_dataset.py
```

The dataset deliberately does **not** package game binaries or full commercial scripts. See `datasets/text_vn/README.md`.

## Architecture

```text
web/                 React UI, VN player, compiler, gallery, settings
server/              FastAPI API, SQLite layer, DeepSeek client, encrypted secrets
scripts/             asset generation, dataset builder, smoke tests, validators
datasets/            curated text VN style dataset
docs/                design documents, MVP plan, screenshots
data/                local runtime database (gitignored)
```

Key design documents:

- `docs/PROJECT_PLAN.md`
- `docs/AGENT_AND_PRODUCTION.md`
- `docs/DATA_MODEL_V0.md`
- `docs/DATA_AND_QUALITY.md`
- `docs/MODEL_AND_DEGRADATION.md`
- `docs/MVP_PLAN.md`

## API overview

```text
GET    /api/health
GET    /api/bootstrap
GET    /api/stories
GET    /api/stories/{id}
POST   /api/stories/generate
POST   /api/sessions
GET    /api/sessions/{id}
POST   /api/sessions/{id}/next
POST   /api/sessions/{id}/choose
POST   /api/sessions/{id}/save
GET    /api/stories/{id}/saves
POST   /api/saves/{id}/load
GET    /api/stories/{id}/gallery
GET    /api/settings
PUT    /api/settings
POST   /api/settings/secret
DELETE /api/settings/secret
POST   /api/tts
GET    /api/dataset
```

## Verification

```bash
# Type-check frontend
npx tsc --noEmit -p web/tsconfig.json

# Build frontend
npm run build

# Validate all story packages and visual assets
python scripts/validate_packages.py

# API smoke test (server must be running)
python scripts/smoke_test.py

# Include a real model generation test
python scripts/smoke_test.py --generate
```

## Current v1.0 boundaries

Working:

- text generation through DeepSeek-compatible API;
- complete story package generation;
- branching playback;
- save / load;
- CG / scene / sprite / ending gallery;
- local encrypted key storage;
- 17-work text VN style dataset.

Placeholder / next:

- real image generation backend;
- real music generation backend;
- tested GPT-SoVITS voice backend (adapter exists, browser TTS fallback works);
- full production editor;
- Ren'Py export;
- cloud sync and multiplayer.

## Security

- No API key is committed to the repository.
- Secrets are encrypted with Fernet.
- The local backend binds to `127.0.0.1` by default.
- Story data and saves stay in local SQLite.
- The app does not upload keys to any third-party storage; model calls go directly to the configured endpoint.

## License

MIT. See [LICENSE](LICENSE).

