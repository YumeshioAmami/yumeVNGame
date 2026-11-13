import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  Check,
  Package,
  Puzzle,
  ToggleLeft,
  ToggleRight,
  Trash2,
  Upload,
  ArrowRight,
} from "lucide-react";
import { api } from "../api";
import { useApp } from "../app-context";
import Tag from "../components/Tag";
import type { PluginInfo } from "../types";

const TYPES = ["全部", "dataset", "world", "story", "music", "image", "voice", "asset_pack"];

export default function Plugins() {
  const { data, refresh } = useApp();
  const [plugins, setPlugins] = useState<PluginInfo[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [installing, setInstalling] = useState(false);
  const [filter, setFilter] = useState("全部");
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    void api.plugins().then(setPlugins);
  }, []);

  async function installPlugin(file: File) {
    setInstalling(true);
    setMessage(null);
    try {
      const bytes = new Uint8Array(await file.arrayBuffer());
      let binary = "";
      const chunk = 0x8000;
      for (let index = 0; index < bytes.length; index += chunk) {
        binary += String.fromCharCode(...bytes.subarray(index, index + chunk));
      }
      const plugin = await api.installPlugin(file.name, btoa(binary));
      setPlugins(await api.plugins());
      await refresh();
      setMessage(`已安装 ${plugin.name} v${plugin.version}，可以启用了。`);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "插件安装失败");
    } finally {
      setInstalling(false);
    }
  }

  async function togglePlugin(plugin: PluginInfo) {
    try {
      await api.setPluginEnabled(plugin.id, !plugin.enabled);
      setPlugins(await api.plugins());
      await refresh();
      setMessage(`${plugin.name} 已${plugin.enabled ? "停用" : "启用"}。`);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "插件状态更新失败");
    }
  }

  async function removePlugin(plugin: PluginInfo) {
    try {
      await api.deletePlugin(plugin.id);
      setPlugins(await api.plugins());
      await refresh();
      setMessage(`${plugin.name} 已删除。`);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "插件删除失败");
    }
  }

  const visible = filter === "全部" ? plugins : plugins.filter((plugin) => plugin.type === filter);

  return (
    <div className="page plugins-page">
      <header className="page-head">
        <div>
          <div className="eyebrow mono"><span className="pulse-dot" /> CONTENT GARDEN</div>
          <h1>插件与数据集</h1>
          <p className="page-lead">
            把世界、故事、音乐、图片、语音和风格包变成可插拔内容。核心不内置第三方素材，用户自己决定要装什么。
          </p>
        </div>
        <div className="head-badge glass">
          <span className="mono">ACTIVE</span>
          <strong>{data.dataset.active_plugins || 0}<small>/{plugins.length}</small></strong>
        </div>
      </header>

      <div className="plugin-hero glass">
        <div className="plugin-hero-copy">
          <div className="section-label mono">EXTERNAL CONTENT</div>
          <h2>内容不塞进引擎，插件自己生长</h2>
          <p>
            数据集、世界包、故事包、素材包、音乐包、语音包都可以独立安装、启停和删除。
            官方数据包也只是插件，不随核心仓库分发。
          </p>
          <div className="plugin-stats">
            <div><strong>{data.dataset.active_plugins || 0}</strong><span>启用插件</span></div>
            <div><strong>{data.dataset.works || 0}</strong><span>作品样本</span></div>
            <div><strong>{plugins.length}</strong><span>已安装</span></div>
          </div>
          <div className="plugin-actions">
            <button className="btn btn-primary" onClick={() => fileRef.current?.click()} disabled={installing}>
              <Upload size={15} /> {installing ? "正在安装..." : "安装插件包 (.zip)"}
            </button>
            <input
              ref={fileRef}
              type="file"
              accept=".zip"
              style={{ display: "none" }}
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) void installPlugin(file);
                event.target.value = "";
              }}
            />
            <Link to="/settings" className="btn btn-ghost">
              插件目录设置 <ArrowRight size={15} />
            </Link>
          </div>
          {message && <div className="settings-message"><Check size={15} /> {message}</div>}
        </div>
        <div className="plugin-hero-art">
          <div className="plugin-art-ring ring-one" />
          <div className="plugin-art-ring ring-two" />
          <div className="plugin-art-core"><Puzzle size={44} /></div>
          <span className="plugin-art-tag tag-one">world</span>
          <span className="plugin-art-tag tag-two">story</span>
          <span className="plugin-art-tag tag-three">music</span>
          <span className="plugin-art-tag tag-four">art</span>
        </div>
      </div>

      <div className="plugin-toolbar">
        <div className="gallery-tabs">
          {TYPES.map((type) => (
            <button
              key={type}
              className={`filter-chip ${filter === type ? "active" : ""}`}
              onClick={() => setFilter(type)}
            >
              {type === "全部" ? "全部" : type}
              <span className="mono">
                {type === "全部" ? plugins.length : plugins.filter((plugin) => plugin.type === type).length}
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="plugin-list plugin-page-list">
        {visible.map((plugin) => (
          <div key={plugin.id} className={`plugin-card ${plugin.enabled ? "enabled" : ""}`}>
            <div className="plugin-icon"><Package size={18} /></div>
            <div className="plugin-info">
              <div className="plugin-title">
                <strong>{plugin.name}</strong>
                <Tag tone="accent">{plugin.type}</Tag>
                {plugin.enabled && <Tag tone="warm">enabled</Tag>}
              </div>
              <p>{plugin.description}</p>
              <div className="plugin-meta mono">
                <span>{plugin.id}</span>
                <span>v{plugin.version}</span>
                <span>{plugin.source}</span>
                {plugin.works > 0 && <span>{plugin.works} works</span>}
              </div>
              <div className="plugin-license mono">License: {plugin.license || "not specified"}</div>
            </div>
            <div className="plugin-controls">
              <button
                className="icon-btn"
                onClick={() => void togglePlugin(plugin)}
                title={plugin.enabled ? "停用" : "启用"}
              >
                {plugin.enabled ? <ToggleRight size={21} /> : <ToggleLeft size={21} />}
              </button>
              {plugin.source === "user" && (
                <button className="icon-btn" onClick={() => void removePlugin(plugin)} title="删除">
                  <Trash2 size={16} />
                </button>
              )}
            </div>
          </div>
        ))}
        {visible.length === 0 && (
          <div className="empty-state glass">
            <div className="empty-glyph"><Puzzle size={28} /></div>
            <h3>这个分类还没有插件</h3>
            <p>安装一个 .zip 插件包，或者切换分类看看。</p>
          </div>
        )}
      </div>

      <div className="plugin-note glass">
        <div>
          <div className="section-label mono">PLUGIN FORMAT</div>
          <h3>一个 zip，一个 plugin.json</h3>
          <p>
            插件只作为数据加载，不执行代码。核心会校验 manifest、限制包大小、阻止路径穿越。
          </p>
        </div>
        <code>{`{
  "id": "my-pack",
  "type": "dataset",
  "version": "0.1.0"
}`}</code>
      </div>
    </div>
  );
}

