# yumeVNGame

[English](README.md) | [简体中文](README.zh-CN.md)

[![CI](https://github.com/YumeshioAmami/yumeVNGame/actions/workflows/ci.yml/badge.svg)](https://github.com/YumeshioAmami/yumeVNGame/actions/workflows/ci.yml)

> 一个本地优先、AI 原生的视觉小说**桌面应用**。故事先被编译成完整的叙事包，再渲染成带背景、立绘、CG、分支、存档和记忆回廊的可玩作品。

仓库：<https://github.com/YumeshioAmami/yumeVNGame>

**当前状态：`0.1.0` 源码原型。** 这不是打包版。`1.0.0` 保留到你验收通过、并且真实图片 / 音频后端接上之后。

## 桌面应用

yumeVNGame 运行在原生桌面窗口中，不是网页产品。

- **桌面外壳：** Python + PyWebView（Windows 使用 WebView2）
- **本地后端：** FastAPI，绑定 `127.0.0.1`
- **本地存储：** SQLite + 本地素材 / 插件目录
- **启动：** `start.bat` 或 `start.ps1`
- **仅开发用：** `dev.bat` 或 `npm run dev`（Vite + API 浏览器开发模式）
- **单实例：** 重复启动只会聚焦已打开窗口，不会再开第二个应用
- **自动重启：** `watch-desktop.bat` 在源码变化后自动重启桌面版

桌面启动器会启动本地 API、必要时构建前端、打开原生窗口，并在窗口关闭时关闭本地 API。

## 项目定位

- **不是 AI 陪伴聊天。** 模型先设计完整故事图，再渲染场景。
- **视觉小说优先。** 每个场景必须有背景或 CG；有立绘人物时必须出现立绘和差分；特殊 CG 不叠加立绘。
- **分支与记忆。** 选择、结局、存档、CG 回看、场景回看、立绘差分查看都是正式功能。
- **自带模型。** 先支持 DeepSeek-compatible chat completions，模型层保持可替换。
- **本地密钥。** API Key 加密保存在用户数据目录，不进入仓库。
- **内容外置。** 数据集、世界包、故事包、音乐、图片、语音、素材包都通过插件安装，不塞进核心。

## 功能

### 故事运行时

- 原生桌面窗口 + 本地 FastAPI 后端；
- 柔和故事房间 UI，四套主题：晨光 / 樱雾 / 薄荷 / 夜灯；
- 全屏视觉小说舞台；
- 打字机对话、旁白、角色色；
- 带提示的分支选择；
- 背景时段 / 氛围滤镜；
- 立绘图层与表情差分；
- 特殊 CG 场景自动隐藏立绘；
- 结局解锁回廊；
- 浏览器 TTS + GPT-SoVITS HTTP 适配器。

### 故事编译

- 自然语言前提 → 结构化故事包；
- 8–12 个节点、多个选择、2–3 个结局；
- 角色表、背景使用、立绘差分、CG 节点；
- 严格 JSON 输出与故事包规范化；
- 没有配置模型时仍有内置示例故事可玩。

### 进度与回廊

- 本地 SQLite 存档；
- 存档 / 读档：当前节点、历史、已访问节点、选择记录；
- CG 回看；
- 场景回看；
- 立绘差分查看；
- 结局收集；
- 按本地玩家持久化解锁状态。
- fal / Replicate / NovelAI / Stability / ElevenLabs 的加密 API Key 管理。

### 插件系统

```text
dataset      风格 / 结构 / Few-shot / RAG 数据
world        世界观、规则、地点、阵营、Lore
story        完整故事包或故事链
music        主题、音轨、Cue
image        背景、立绘、CG、UI 包
voice        音色档案 / 参考音频
asset_pack   混合素材包
theme        UI 主题包
```

第一种已实现的类型是 `dataset`。用户在 **插件页** 里安装 `.zip` 包。核心仓库只带一个原创示例数据集插件，不内置第三方剧情摘要或商业游戏内容。

详见 `docs/PLUGIN_SYSTEM.md` 和 `datasets/README.md`。

## 技术栈

- 桌面外壳：Python + PyWebView
- 后端：FastAPI + SQLite
- 前端：React 18 + TypeScript + Vite + Framer Motion + Lucide
- 模型：OpenAI-compatible chat completions（默认 DeepSeek）
- 素材：本地程序化 SVG 概念背景、立绘、CG 占位
- 存储：本地 SQLite + 加密本地密钥

## 快速开始

环境要求：

- Windows 10/11，带 WebView2 Runtime
- Node.js 20+
- Python 3.10+

```bash
npm install
pip install -r requirements.txt
```

然后双击：

```text
start.bat
```

或者运行：

```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```

桌面启动器会自动安装缺失依赖、必要时构建前端、启动本地 API，并打开原生应用窗口。

仅开发使用：

```text
dev.bat
```

桌面版源码自动重启：

```text
watch-desktop.bat
```

手动重启 / 停止：

```text
restart-desktop.bat
stop-desktop.bat
```

## 配置文本模型

### 方式 A：设置页

打开 **设置 → 文本模型**，粘贴 API Key，选择模型 / Base URL，保存即可。

### 方式 B：环境变量 + 加密存储

```powershell
$env:DEEPSEEK_API_KEY="sk-your-key"
$env:DEEPSEEK_MODEL="deepseek-chat"
python scripts/set_secret.py
```

Key 加密保存在：

```text
%APPDATA%\yumeVNGame\secrets.enc
```

主密钥单独保存在 `%APPDATA%\yumeVNGame\master.key`。两个文件都不在仓库里。

显存较低的用户可以直接使用在线图片 / 音乐 API，详见 `docs/MODEL_RECOMMENDATIONS.md`。

## 外置数据集包

核心仓库故意不内置任何第三方剧情摘要、游戏脚本、图片、音乐或语音素材。

构建一个外置研究数据包：

```bash
python scripts/build_text_dataset.py
python scripts/package_dataset_plugin.py
```

输出：

```text
datasets/local/text_vn/                 # gitignored 本地包
dist_plugins/text-vn-official-0.1.0.zip # 可安装插件包
```

在 **插件页** 中安装 zip。插件保存在：

```text
%APPDATA%\yumeVNGame\plugins\<plugin-id>\
```

## 项目结构

```text
desktop.py            原生桌面启动器（PyWebView + 本地 API）
web/                  React UI、VN 播放器、编译器、回廊、设置
server/               FastAPI、SQLite、DeepSeek 客户端、加密密钥、插件
scripts/              素材生成、数据集构建、打包、冒烟测试、校验器
plugins/              插件格式 + 原创示例数据集插件
datasets/             外置数据集工作目录（本地包 gitignored）
docs/                 设计文档、插件系统、原型说明
data/                 本地运行时数据库（gitignored）
```

UI 截图、生成的占位素材和用户数据只保留在本地，绝不提交到仓库。

核心设计文档：

- `docs/PROJECT_PLAN.md`
- `docs/AGENT_AND_PRODUCTION.md`
- `docs/DATA_MODEL_V0.md`
- `docs/DATA_AND_QUALITY.md`
- `docs/MODEL_AND_DEGRADATION.md`
- `docs/PLUGIN_SYSTEM.md`
- `docs/MODEL_RECOMMENDATIONS.md`
- `docs/IMAGE_AGENT_DESIGN.md`
- `docs/TEXT_MODEL_TEST_2026-11-13.md`
- `docs/CHARACTER_CONSISTENCY.md`
- `docs/CHARACTER_PIPELINE.md`
- `docs/API_KEYS.md`
- `docs/REFERENCE_DATASET.md`
- `docs/MVP_PLAN.md`
- `docs/PROTOTYPE_NOTES.md`

## 验证

```bash
# 前端类型检查
npx tsc --noEmit -p web/tsconfig.json

# 前端构建
npm run build

# 故事包与视觉资源校验
python scripts/validate_packages.py

# API 冒烟测试（需要本地 API 已启动）
python scripts/smoke_test.py

# 包含真实模型生成测试
python scripts/smoke_test.py --generate

# 本地浏览器 UI 冒烟测试（开发用）
npm run test:ui

# 原生桌面启动测试（4 秒后自动关闭）
$env:YUME_AUTO_CLOSE_MS="4000"; python desktop.py
```

## 0.1.0 边界与 1.0.0 门槛

已可用：

- 原生桌面启动器；
- DeepSeek-compatible 文本生成；
- 完整故事包生成；
- 分支播放；
- 存档 / 读档；
- CG / 场景 / 立绘差分 / 结局回廊；
- 本地加密密钥；
- 外置数据集 / 插件包系统；
- 源码启动脚本（`start.bat` / `start.ps1`）。

0.1.0 尚未包含：

- 打包安装器 / 独立发行版；
- 真实图片生成后端；
- 真实音乐生成后端；
- 实测 GPT-SoVITS 语音后端（适配器已有，浏览器 TTS 回退可用）；
- 完整制作编辑器；
- Ren'Py 导出；
- 云同步与多人。

`1.0.0` 的门槛：你验收通过、真实图片 / 音频后端接上、打包分发策略确定。

## 安全

- 仓库不含任何 API Key；
- 密钥使用 Fernet 加密；
- 本地后端默认只绑定 `127.0.0.1`；
- 故事与存档保存在本地 SQLite；
- 插件包经过校验并解压到仓库外；
- 密钥不会上传到第三方存储，模型请求直接发往用户配置的端点。

## 许可证

MIT，见 [LICENSE](LICENSE)。

