# External Dataset Packs

yumeVNGame does **not** ship third-party plot summaries, game scripts, images, music, or voice assets in the core repository.

Datasets are **external plugins**. This keeps the core application independent from third-party content licenses and lets users choose which style packs they want to install.

## Plugin layout

```text
my-dataset-pack/
├─ plugin.json
├─ works.jsonl
└─ style_notes.md
```

`plugin.json`:

```json
{
  "id": "my-text-vn-pack",
  "name": "My Text VN Pack",
  "version": "0.1.0",
  "type": "dataset",
  "description": "Style and structure reference for text generation.",
  "author": "you",
  "license": "your license / source notes",
  "enabled_by_default": false,
  "data_file": "works.jsonl",
  "context_file": "style_notes.md",
  "tags": ["dataset", "text", "style"]
}
```

Install it from **设置 → 外部数据集 / 插件包 → 安装插件包** in the app.

## Building a local research pack

```bash
python scripts/build_text_dataset.py
python scripts/package_dataset_plugin.py
```

This writes:

```text
datasets/local/text_vn/                 # local, gitignored
dist_plugins/text-vn-official-0.1.0.zip # local, gitignored
```

Only the plugin code and manifest format are part of the core repo. The generated dataset pack is user-owned and can be distributed separately with its own license and attribution.

## Copyright note

Do not upload or redistribute content you do not have rights to. The official pack builder is intended for research and style analysis; it does not include game binaries, full commercial scripts, or asset files.

