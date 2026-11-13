import { useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Check,
  Image,
  KeyRound,
  Music,
  Package,
  Palette,
  Save,
  ShieldCheck,
  Trash2,
  Volume2,
} from "lucide-react";
import { api } from "../api";
import { useApp } from "../app-context";
import ProviderKeyRow from "../components/ProviderKeyRow";

const IMAGE_PROVIDERS = [
  {
    id: "nanogpt",
    name: "NanoGPT",
    hint: "PixelWave / P-Image / Seedream / FLUX.3，低门槛按量 API",
    keyUrl: "https://nano-gpt.com/api",
  },
  {
    id: "fal",
    name: "fal.ai",
    hint: "Nano Banana / FLUX / Z Image / Qwen 等图片模型",
    keyUrl: "https://fal.ai/dashboard/keys",
  },
  {
    id: "replicate",
    name: "Replicate",
    hint: "Qwen Image Edit / FLUX Kontext / Seedream / SDXL",
    keyUrl: "https://replicate.com/account/api-tokens",
  },
  {
    id: "novelai",
    name: "NovelAI",
    hint: "动漫向、订阅制、可选 NSFW 单图通道",
    keyUrl: "https://novelai.net/",
  },
];

const MUSIC_PROVIDERS = [
  {
    id: "stability",
    name: "Stability AI",
    hint: "Stable Audio API：BGM loop / 环境氛围",
    keyUrl: "https://platform.stability.ai/account/keys",
  },
  {
    id: "elevenlabs",
    name: "ElevenLabs",
    hint: "Music API：完整歌曲 / 主题曲",
    keyUrl: "https://elevenlabs.io/app/settings/api-keys",
  },
];

const THEMES = [
  { id: "morning", label: "晨光 Morning", desc: "奶油白、浅杏、淡紫。最温柔的一档。" },
  { id: "sakura", label: "樱雾 Sakura", desc: "樱花粉、雾紫、奶白。轻软、亲近。" },
  { id: "mint", label: "薄荷 Mint", desc: "薄荷绿、天空蓝、奶油黄。清爽、安静。" },
  { id: "night", label: "夜灯 Night", desc: "深紫、暖粉、灯光黄。适合夜里慢慢看。" },
];

export default function Settings() {
  const { data, refresh, theme, setTheme } = useApp();
  const [keyInput, setKeyInput] = useState("");
  const [model, setModel] = useState(data.settings.model);
  const [baseUrl, setBaseUrl] = useState(data.settings.base_url);
  const [ttsEndpoint, setTtsEndpoint] = useState(data.settings.tts_endpoint);
  const [ttsVoice, setTtsVoice] = useState(data.settings.tts_voice);
  const [imageProvider, setImageProvider] = useState(data.settings.image_provider || "nanogpt");
  const [musicProvider, setMusicProvider] = useState(data.settings.music_provider || "stability");
  const [agentDistant, setAgentDistant] = useState(
    data.settings.image_agent_distant || "pixelwave",
  );
  const [agentScene, setAgentScene] = useState(
    data.settings.image_agent_scene || "prunaai:1@1",
  );
  const [agentSpecialCg, setAgentSpecialCg] = useState(
    data.settings.image_agent_special_cg || "seedream-v4.5",
  );
  const [agentDraft, setAgentDraft] = useState(
    data.settings.image_agent_draft || "blackforestlabs/flux-3/klein/edit-image",
  );
  const [agentCharacterFinal, setAgentCharacterFinal] = useState(
    data.settings.image_agent_character_final || "bytedance/seedream-v5.0-flash",
  );
  const [agentCharacterDiff, setAgentCharacterDiff] = useState(
    data.settings.image_agent_character_diff || "blackforestlabs/flux-3/klein/edit-image",
  );
  const [message, setMessage] = useState<string | null>(null);
  const [providerMessage, setProviderMessage] = useState<string | null>(null);
  const [imageAgentMessage, setImageAgentMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function saveKey() {
    if (!keyInput.trim()) {
      setMessage("请输入 API Key。");
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      const result = await api.setSecret(keyInput.trim(), model, baseUrl);
      setKeyInput("");
      setMessage(`已加密保存：${result.secrets.masked_key}`);
      await refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "保存失败");
    } finally {
      setBusy(false);
    }
  }

  async function clearKey() {
    setBusy(true);
    try {
      await api.clearSecret();
      setMessage("已删除本地 API Key。");
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function saveSettings() {
    setBusy(true);
    setMessage(null);
    try {
      await api.updateSettings({
        model,
        base_url: baseUrl,
        tts_endpoint: ttsEndpoint,
        tts_voice: ttsVoice,
        theme,
      });
      setMessage("设置已保存。");
      await refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "保存失败");
    } finally {
      setBusy(false);
    }
  }

  async function saveProviderDefaults() {
    setProviderMessage(null);
    try {
      await api.updateSettings({
        image_provider: imageProvider,
        music_provider: musicProvider,
      });
      await refresh();
      setProviderMessage("默认 API 通道已保存。");
    } catch (err) {
      setProviderMessage(err instanceof Error ? err.message : "保存失败");
    }
  }

  async function saveImageAgents() {
    setImageAgentMessage(null);
    try {
      await api.updateSettings({
        image_agent_distant: agentDistant,
        image_agent_scene: agentScene,
        image_agent_special_cg: agentSpecialCg,
        image_agent_draft: agentDraft,
        image_agent_character_final: agentCharacterFinal,
        image_agent_character_diff: agentCharacterDiff,
      });
      await refresh();
      setImageAgentMessage("图像 Agent 路由已保存。");
    } catch (err) {
      setImageAgentMessage(err instanceof Error ? err.message : "保存失败");
    }
  }

  return (
    <div className="page settings-page">
      <header className="page-head">
        <div>
          <div className="eyebrow mono"><span className="pulse-dot" /> COZY CONTROL ROOM</div>
          <h1>设置</h1>
          <p className="page-lead">
            模型、密钥、主题和声音。所有敏感信息都只留在这台电脑上。
          </p>
        </div>
        <div className="head-badge glass">
          <span className="mono">PRIVACY</span>
          <strong className="security-badge"><ShieldCheck size={18} /> LOCAL</strong>
        </div>
      </header>

      <div className="settings-grid">
        <section className="glass settings-panel">
          <div className="panel-head">
            <div>
              <div className="section-label mono">TEXT MODEL</div>
              <h2>文本模型</h2>
            </div>
            <KeyRound size={20} className="accent" />
          </div>

          <div className="secret-status">
            <span className={`status-dot ${data.secrets.has_api_key ? "online" : "warn"}`} />
            <span>{data.secrets.has_api_key ? "已配置加密密钥" : "尚未配置密钥"}</span>
            {data.secrets.has_api_key && <code>{data.secrets.masked_key}</code>}
          </div>

          <label className="field">
            <span>文本模型 API Key</span>
            <input
              type="password"
              value={keyInput}
              onChange={(event) => setKeyInput(event.target.value)}
              placeholder="sk-..."
              autoComplete="off"
            />
          </label>
          <div className="field-row">
            <label className="field">
              <span>模型名</span>
              <input value={model} onChange={(event) => setModel(event.target.value)} />
            </label>
            <label className="field">
              <span>Base URL</span>
              <input value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} />
            </label>
          </div>
          <p className="mono micro muted">
            硅基流动：https://api.siliconflow.cn/v1 · DeepSeek：https://api.deepseek.com
          </p>
          <p className="mono micro muted">
            填写 Key 后请点「加密保存 Key」；另一个「保存设置」只保存界面与语音配置。
          </p>
          <div className="button-row">
            <button className="btn btn-primary" onClick={() => void saveKey()} disabled={busy}>
              <Save size={15} /> 加密保存 Key
            </button>
            {data.secrets.has_api_key && (
              <button className="btn btn-danger" onClick={() => void clearKey()} disabled={busy}>
                <Trash2 size={15} /> 删除 Key
              </button>
            )}
          </div>
          <p className="mono micro muted">
            Fernet 加密 · {data.secrets.storage}
          </p>
        </section>

        <section className="glass settings-panel">
          <div className="panel-head">
            <div>
              <div className="section-label mono">VOICE</div>
              <h2>语音</h2>
            </div>
            <Volume2 size={20} className="accent" />
          </div>
          <p className="muted small">
            默认使用浏览器语音合成。GPT-SoVITS 适配器保留在本机，填入本地服务地址后即可尝试。
          </p>
          <label className="field">
            <span>GPT-SoVITS Endpoint</span>
            <input
              value={ttsEndpoint}
              onChange={(event) => setTtsEndpoint(event.target.value)}
              placeholder="http://127.0.0.1:9880"
            />
          </label>
          <label className="field">
            <span>音色 / Voice ID</span>
            <input
              value={ttsVoice}
              onChange={(event) => setTtsVoice(event.target.value)}
              placeholder="任意已有音色"
            />
          </label>
          <div className="tts-note">
            <Volume2 size={16} />
            <span>播放器右上角的朗读按钮当前使用浏览器 TTS。</span>
          </div>
        </section>

        <section className="glass settings-panel">
          <div className="panel-head">
            <div>
              <div className="section-label mono">THEME</div>
              <h2>界面主题</h2>
            </div>
            <Palette size={20} className="accent" />
          </div>
          <div className="theme-cards">
            {THEMES.map((item) => (
              <button
                key={item.id}
                className={`theme-card theme-${item.id} ${theme === item.id ? "active" : ""}`}
                onClick={() => setTheme(item.id)}
              >
                <span className="theme-preview" />
                <strong>{item.label}</strong>
                <em>{item.desc}</em>
                {theme === item.id && <Check size={16} />}
              </button>
            ))}
          </div>
          <button className="btn btn-primary" onClick={() => void saveSettings()} disabled={busy}>
            <Save size={15} /> 保存设置
          </button>
          {message && <div className="settings-message"><Check size={15} /> {message}</div>}
        </section>

        <section className="glass settings-panel provider-panel">
          <div className="panel-head">
            <div>
              <div className="section-label mono">IMAGE / MUSIC APIs</div>
              <h2>图片与音乐 API Keys</h2>
            </div>
            <KeyRound size={20} className="accent" />
          </div>
          <p className="muted small">
            Key 会加密保存在本机。这里保存后，下一步的图片 / 音乐 adapter 会直接读取对应 provider。
          </p>

          <div className="provider-section-head"><Image size={16} /> 图片 API</div>
          <div className="provider-grid">
            {IMAGE_PROVIDERS.map((meta) => {
              const status = data.secrets.providers?.[meta.id] ?? {
                id: meta.id,
                name: meta.name,
                kind: "image" as const,
                has_key: false,
                masked_key: "",
              };
              return (
                <ProviderKeyRow
                  key={meta.id}
                  provider={status}
                  hint={meta.hint}
                  keyUrl={meta.keyUrl}
                  onChanged={refresh}
                />
              );
            })}
          </div>

          <div className="provider-section-head"><Music size={16} /> 音乐 / BGM API</div>
          <div className="provider-grid">
            {MUSIC_PROVIDERS.map((meta) => {
              const status = data.secrets.providers?.[meta.id] ?? {
                id: meta.id,
                name: meta.name,
                kind: "music" as const,
                has_key: false,
                masked_key: "",
              };
              return (
                <ProviderKeyRow
                  key={meta.id}
                  provider={status}
                  hint={meta.hint}
                  keyUrl={meta.keyUrl}
                  onChanged={refresh}
                />
              );
            })}
          </div>

          <div className="provider-defaults">
            <label className="field">
              <span>默认图片 API</span>
              <select value={imageProvider} onChange={(event) => setImageProvider(event.target.value)}>
                <option value="nanogpt">NanoGPT</option>
                <option value="fal">fal.ai</option>
                <option value="replicate">Replicate</option>
                <option value="novelai">NovelAI</option>
              </select>
            </label>
            <label className="field">
              <span>默认音乐 API</span>
              <select value={musicProvider} onChange={(event) => setMusicProvider(event.target.value)}>
                <option value="stability">Stability AI</option>
                <option value="elevenlabs">ElevenLabs</option>
                <option value="replicate">Replicate</option>
              </select>
            </label>
            <button className="btn btn-primary" onClick={() => void saveProviderDefaults()}>
              <Save size={15} /> 保存默认通道
            </button>
          </div>
          {providerMessage && <div className="settings-message"><Check size={15} /> {providerMessage}</div>}
        </section>

        <section className="glass settings-panel image-agent-panel">
          <div className="panel-head">
            <div>
              <div className="section-label mono">IMAGE AGENTS</div>
              <h2>图像 Agent</h2>
            </div>
            <Image size={20} className="accent" />
          </div>
          <p className="muted small">
            每个任务走独立模型。“草稿”默认用 FLUX.3 Klein 出构图 / 角度 / 姿势参考，
            再由 Seedream 5.0 Flash 一次定版。特殊CG 只作为界面展示名。
          </p>
          <div className="field-row">
            <label className="field">
              <span>远景</span>
              <input value={agentDistant} onChange={(event) => setAgentDistant(event.target.value)} />
            </label>
            <label className="field">
              <span>具体场景</span>
              <input value={agentScene} onChange={(event) => setAgentScene(event.target.value)} />
            </label>
          </div>
          <div className="field-row">
            <label className="field">
              <span>特殊CG</span>
              <input value={agentSpecialCg} onChange={(event) => setAgentSpecialCg(event.target.value)} />
            </label>
            <label className="field">
              <span>草稿</span>
              <input value={agentDraft} onChange={(event) => setAgentDraft(event.target.value)} />
            </label>
          </div>
          <div className="field-row">
            <label className="field">
              <span>角色最终图 / 设定图</span>
              <input
                value={agentCharacterFinal}
                onChange={(event) => setAgentCharacterFinal(event.target.value)}
              />
            </label>
            <label className="field">
              <span>日常角色差分</span>
              <input
                value={agentCharacterDiff}
                onChange={(event) => setAgentCharacterDiff(event.target.value)}
              />
            </label>
          </div>
          <button className="btn btn-primary" onClick={() => void saveImageAgents()}>
            <Save size={15} /> 保存图像 Agent 路由
          </button>
          {imageAgentMessage && (
            <div className="settings-message"><Check size={15} /> {imageAgentMessage}</div>
          )}
        </section>

        <section className="glass settings-panel plugin-link-panel">
          <div className="panel-head">
            <div>
              <div className="section-label mono">CONTENT PACKS</div>
              <h2>插件与数据集</h2>
            </div>
            <Package size={20} className="accent" />
          </div>
          <p className="muted small">
            数据集、世界包、故事包、音乐、图片、语音和素材包都在独立插件页管理。
          </p>
          <div className="dataset-stats">
            <div><strong>{data.dataset.active_plugins || 0}</strong><span>启用插件</span></div>
            <div><strong>{data.dataset.works || 0}</strong><span>作品样本</span></div>
            <div><strong>EXTERNAL</strong><span>数据模式</span></div>
          </div>
          <Link to="/plugins" className="btn btn-primary">
            <Package size={15} /> 打开插件页 <ArrowRight size={15} />
          </Link>
        </section>
      </div>
    </div>
  );
}

