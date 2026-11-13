# yumeVNGame 0.1.0 Prototype Plan

> 目标：在一个晚上交付可运行的 0.1.0 垂直原型，第二天可以验收。1.0.0 等验收通过并且图片 / 音频模型真正接上后再做。

## 1. 第一版范围

### 必须完成

- 现代化、悬浮化、动态化、科技化的 Web UI；
- 多主题色切换；
- 故事库、创建故事、游玩、画廊、设置；
- DeepSeek 文本模型接入；
- 完整故事包生成：角色、场景、分支、结局；
- 视觉小说播放器：背景、立绘、差分、CG、对话框、选项；
- 存档 / 读档；
- 分支进度；
- CG 回看、场景回看、立绘差分查看；
- API Key 加密保存在本地用户数据目录；
- 外置数据集插件系统（核心不内置第三方数据）；
- Git 仓库与 MIT 协议。

### 暂不完成

- 图片生成模型真实接入；
- 音乐生成模型真实接入；
- GPT-SoVITS 真实服务接入（保留适配接口和浏览器 TTS 回退）；
- 多人 / 云同步；
- 完整编辑器；
- Ren'Py 导出。

## 2. 技术栈

- 前端：React + TypeScript + Vite + Framer Motion + Lucide
- 后端：Python FastAPI + SQLite
- 模型：DeepSeek OpenAI-compatible API
- 素材：本地 SVG 概念背景 / 立绘占位，后续可替换为生成资产
- 存储：本地 SQLite + 用户数据目录加密密钥

## 3. 验收标准

1. `npm install` 后可以启动前后端；
2. 首页能打开并展示故事库；
3. 能打开内置示例故事并完成一次分支游玩；
4. 能存档、读档；
5. 能查看 CG / 场景 / 立绘差分回看；
6. 能输入 API Key 并真实调用 DeepSeek 生成一个新故事；
7. 新故事能进入播放器并产生分支；
8. 仓库不含 API Key；
9. 数据集以外部插件形式存在，核心仓库不内置第三方剧情/图片/音频。

## 4. 文件结构

```text
server/        FastAPI + SQLite + DeepSeek + secrets
web/           React UI + VN player + gallery
scripts/       asset generation / dataset build / smoke test
plugins/       plugin format + original example dataset plugin
datasets/      external dataset workspace (local packs gitignored)
docs/          design docs + this MVP plan
```

