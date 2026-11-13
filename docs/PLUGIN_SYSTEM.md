# Plugin System

> Status: 0.1 prototype design and implementation

## Why plugins

The core app should not bundle third-party stories, images, music, voice, or commercial game scripts. Those are optional content packs with their own licenses.

The plugin system is the boundary between:

- the **engine** (runtime, rendering, saves, generation, gallery);
- the **content** (datasets, worlds, stories, images, music, voice, visual packs).

## Plugin types

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

The first implemented type is `dataset`. The manifest and install flow are designed to extend to the rest.

## Manifest

Every plugin is a directory containing `plugin.json`:

```json
{
  "id": "text-vn-official",
  "name": "Official Text VN Style Pack",
  "version": "0.1.0",
  "type": "dataset",
  "description": "Optional style and structure reference pack.",
  "author": "yumeVNGame contributors",
  "license": "CC BY-SA summaries + editorial metadata",
  "enabled_by_default": false,
  "data_file": "works.jsonl",
  "context_file": "style_notes.md",
  "tags": ["dataset", "text", "style"]
}
```

## Install flow

1. User builds or receives a `.zip` plugin pack.
2. User opens **设置 → 外部数据集与插件包**.
3. App uploads the zip as base64 JSON, validates it, checks path traversal, extracts it into:

```text
%APPDATA%\yumeVNGame\plugins\<plugin-id>\
```

4. User can enable / disable / delete user plugins.

## Dataset context

When generating a story, the engine reads only **enabled dataset plugins**:

- `context_file` for style guidance;
- `data_file` for compact work references;
- total context is capped to avoid prompt bloat.

If no dataset plugin is enabled, the engine uses `server/style_guide.md`, an original fallback style guide shipped with the core.

## Security

- plugin archives are limited to 30 MB;
- zip path traversal is blocked;
- bundled plugins cannot be deleted from the UI;
- user plugins live outside the repository;
- plugin content is never executed as code in v0.1. It is data only.

## Official pack

The official text dataset is not committed to the core repo. It can be generated locally:

```bash
python scripts/build_text_dataset.py
python scripts/package_dataset_plugin.py
```

The resulting `dist_plugins/text-vn-official-0.1.0.zip` can be installed from the UI or distributed separately with its own source / license notice.

## Roadmap

- world plugin schema;
- story package import/export;
- image / sprite pack validation;
- music motif / cue pack;
- voice profile pack;
- plugin signing and version constraints;
- plugin repository UI.

