import { useState } from "react";
import { Check, ExternalLink, KeyRound, Save, Trash2 } from "lucide-react";
import { api } from "../api";
import type { ProviderKeyStatus } from "../types";

export default function ProviderKeyRow({
  provider,
  hint,
  keyUrl,
  onChanged,
}: {
  provider: ProviderKeyStatus;
  hint: string;
  keyUrl: string;
  onChanged: () => Promise<void>;
}) {
  const [value, setValue] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function save() {
    if (!value.trim()) {
      setMessage("请先粘贴 Key。");
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      await api.setProviderKey(provider.id, value.trim());
      setValue("");
      setMessage("已加密保存");
      await onChanged();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "保存失败");
    } finally {
      setBusy(false);
    }
  }

  async function clear() {
    setBusy(true);
    setMessage(null);
    try {
      await api.clearProviderKey(provider.id);
      setMessage("已删除");
      await onChanged();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "删除失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className={`provider-row ${provider.has_key ? "configured" : ""}`}>
      <div className="provider-head">
        <div className="provider-icon"><KeyRound size={16} /></div>
        <div className="provider-name">
          <strong>{provider.name}</strong>
          <span className="mono">{provider.kind} API</span>
        </div>
        <span className={`provider-status ${provider.has_key ? "on" : ""}`}>
          {provider.has_key ? "已配置" : "未配置"}
        </span>
        <a className="provider-link" href={keyUrl} target="_blank" rel="noreferrer">
          获取 Key <ExternalLink size={12} />
        </a>
      </div>
      <p className="provider-hint">{hint}</p>
      {provider.has_key && <code className="provider-mask">{provider.masked_key}</code>}
      <div className="provider-input-row">
        <input
          type="password"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder={provider.has_key ? "粘贴新 Key 可覆盖" : "粘贴 API Key"}
          autoComplete="off"
        />
        <button className="btn btn-primary small" onClick={() => void save()} disabled={busy}>
          <Save size={14} /> 保存
        </button>
        {provider.has_key && (
          <button className="icon-btn" onClick={() => void clear()} disabled={busy} title="删除 Key">
            <Trash2 size={15} />
          </button>
        )}
      </div>
      {message && <div className="provider-message"><Check size={13} /> {message}</div>}
    </div>
  );
}

