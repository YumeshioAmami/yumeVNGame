# yumeVNGame v1.0.0 Release Notes

> Local-first AI visual novel runtime / story compiler.

## Delivered

- React + TypeScript + Vite frontend with floating glass UI and four themes;
- FastAPI + SQLite local backend;
- DeepSeek-compatible text model integration;
- Complete story package generation (characters, nodes, choices, endings, scenes);
- Visual novel player with backgrounds, sprites, expression differentials and CG;
- Branching playback, save / load, visited-node history;
- CG gallery, scene replay, sprite differential viewer, ending collection;
- Encrypted local API key storage;
- 17-work text VN style dataset with public-source plot summaries;
- smoke test, package validator, asset generator, dataset builder;
- MIT license and GitHub-ready repository.

## Verified locally

```text
PASS  health
PASS  bootstrap
PASS  dataset
PASS  demo package
PASS  visual coverage
PASS  session
PASS  advance to choice
PASS  choose
PASS  save
PASS  load
PASS  gallery
PASS  gallery unlock
PASS  dataset detail
PASS  deepseek generation
PASS  generated package
ALL SMOKE TESTS PASSED
```

```text
OK: all local story packages validated
```

```text
PASS  home
PASS  player loads
PASS  advance
PASS  choices visible
PASS  choose branch
PASS  gallery
PASS  settings
ALL UI SMOKE TESTS PASSED
```

Frontend type-check and production build pass.

## Notes for the first morning review

1. Start with `npm run dev` and open `http://localhost:5173`.
2. The demo story **雾港来信** works without any model key.
3. To test generation, the DeepSeek key is already stored encrypted on this machine; the UI never displays it in full.
4. Image, music and GPT-SoVITS generation are placeholders / adapters for v1. Text, branching, saves and gallery are the tested core.
5. The visual assets are intentional procedural placeholders, ready to be replaced by generated art.

## Suggested next milestone

- Replace procedural backgrounds and sprites with a real asset pipeline;
- integrate ComfyUI / Stable Diffusion adapter;
- wire GPT-SoVITS with a tested local service;
- add music motif + cue playback;
- implement the full production dashboard and review queue from `docs/AGENT_AND_PRODUCTION.md`.

