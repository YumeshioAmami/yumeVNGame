import { useState } from "react";
import { Check, FolderOpen, Save, Trash2 } from "lucide-react";
import { api } from "../api";
import type { AgentConfig, AgentMode } from "../types";

const CATEGORY_LABELS: Record<AgentConfig["category"], string> = {
  image: "图像",
  text: "文本",
  music: "音乐",
};

interface Props {
  config: AgentConfig;
  onSaved: (config: AgentConfig) => void;
}

export default function AgentConfigCard({ config, onSaved }: Props) {
  const [mode, setMode] = useState<AgentMode>(config.mode);
  const [model, setModel] = useState(config.model);
  const [baseUrl, setBaseUrl] = useState(config.base_url);
  const [localPath, setLocalPath] = useState(config.local_path);
  const [localEndpoint, setLocalEndpoint] = useState(config.local_endpoint);
  const [apiKey, setApiKey] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function save() {
    setBusy(true);
    setMessage(null);
    try {
      const result = await api.updateAgentConfig(config.id, {
        mode,
        model,
        base_url: baseUrl,
        local_path: localPath,
        local_endpoint: localEndpoint,
        ...(mode === "api" && apiKey.trim() ? { api_key: apiKey.trim() } : {}),
      });
      setApiKey("");
      onSaved(result.agent);
      setMessage("已保存到本地配置。");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "保存失败");
    } finally {
      setBusy(false);
    }
  }

  async function clearKey() {
    setBusy(true);
    setMessage(null);
    try {
      const result = await api.clearAgentKey(config.id);
      onSaved(result.agent);
      setMessage("Key 已删除。");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "删除失败");
    } finally {
      setBusy(false);
    }
  }

  async function pick(directory: boolean) {
    try {
      const result = await api.pickAgentFile(directory);
      if (result.path) setLocalPath(result.path);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "选择文件失败");
    }
  }

  return (
    <article className="glass agent-config-card">
      <div className="agent-config-head">
        <div>
          <span className="section-label mono">{CATEGORY_LABELS[config.category]}</span>
          <h3>{config.label}</h3>
        </div>
        <span className={`agent-mode-pill ${mode}`}>{mode === "api" ? "API" : "本地"}</span>
      </div>

      <div className="agent-mode-switch">
        <button
          type="button"
          className={mode === "api" ? "active" : ""}
          onClick={() => setMode("api")}
        >
          API
        </button>
        <button
          type="button"
          className={mode === "local" ? "active" : ""}
          onClick={() => setMode("local")}
        >
          本地
        </button>
      </div>

      <label className="field">
        <span>模型名</span>
        <input value={model} onChange={(event) => setModel(event.target.value)} />
      </label>

      {mode === "api" ? (
        <>
          <label className="field">
            <span>服务地址</span>
            <input
              value={baseUrl}
              onChange={(event) => setBaseUrl(event.target.value)}
              placeholder="https://api.example.com/v1"
            />
          </label>
          <label className="field">
            <span>API Key</span>
            <input
              type="password"
              value={apiKey}
              onChange={(event) => setApiKey(event.target.value)}
              placeholder={config.has_key ? `已保存：${config.masked_key}` : "未保存"}
              autoComplete="off"
            />
          </label>
          <div className="button-row">
            <button className="btn btn-primary" onClick={() => void save()} disabled={busy}>
              <Save size={14} /> 保存
            </button>
            {config.has_key && (
              <button className="btn btn-danger" onClick={() => void clearKey()} disabled={busy}>
                <Trash2 size={14} /> 删除 Key
              </button>
            )}
          </div>
        </>
      ) : (
        <>
          <label className="field">
            <span>本地服务地址</span>
            <input
              value={localEndpoint}
              onChange={(event) => setLocalEndpoint(event.target.value)}
              placeholder="http://127.0.0.1:11434/v1"
            />
          </label>
          <label className="field">
            <span>本地模型文件 / 目录</span>
            <input
              value={localPath}
              onChange={(event) => setLocalPath(event.target.value)}
              placeholder="选择或填写本地路径"
            />
          </label>
          <div className="button-row">
            <button className="btn" onClick={() => void pick(false)}>
              <FolderOpen size={14} /> 选择文件
            </button>
            <button className="btn" onClick={() => void pick(true)}>
              <FolderOpen size={14} /> 选择目录
            </button>
            <button className="btn btn-primary" onClick={() => void save()} disabled={busy}>
              <Save size={14} /> 保存
            </button>
          </div>
        </>
      )}

      {message && (
        <div className="settings-message">
          <Check size={14} /> {message}
        </div>
      )}
    </article>
  );
}
