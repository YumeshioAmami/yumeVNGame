import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { AlertTriangle, ArrowRight, Cpu, KeyRound, Sparkles, Wand2 } from "lucide-react";
import { api } from "../api";
import { useApp } from "../app-context";
import Tag from "../components/Tag";

const PROMPT_CHIPS = [
  "雨夜校园悬疑，带一点恋爱，但别太恐怖。",
  "赛博朋克都市里的记忆走私犯，和一个失去名字的 AI。",
  "末日之后，最后一座图书馆开始自己写故事。",
  "一场只发生在末班地铁上的三角恋。",
];

const STEPS = [
  "解析创作需求",
  "设计完整故事图",
  "分配角色与场景",
  "编译视觉账本",
  "封存故事包",
];

export default function Create() {
  const { data, refresh } = useApp();
  const navigate = useNavigate();
  const [premise, setPremise] = useState(PROMPT_CHIPS[0]);
  const [genre, setGenre] = useState("悬疑、恋爱");
  const [tone, setTone] = useState("冷峻、潮湿、克制");
  const [length, setLength] = useState("短篇");
  const [extra, setExtra] = useState("");
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setError(null);
    if (!data.secrets.has_api_key) {
      setError("还没有配置 DeepSeek API Key。请先去设置页保存密钥。");
      return;
    }
    setLoading(true);
    setStep(0);
    const timer = window.setInterval(() => {
      setStep((current) => Math.min(STEPS.length - 1, current + 1));
    }, 4500);
    try {
      const story = await api.generate({ premise, genre, tone, length, extra });
      await refresh();
      navigate(`/play/${story.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成失败");
    } finally {
      window.clearInterval(timer);
      setLoading(false);
    }
  }

  return (
    <div className="page create-page">
      <header className="page-head">
        <div>
          <div className="eyebrow mono"><span className="pulse-dot" /> STORY COMPILER</div>
          <h1>编译一个新世界</h1>
          <p className="page-lead">
            你只需要给出前提。导演会先设计完整故事图，再交给场景作家、视觉解析和回廊系统。
          </p>
        </div>
        <div className="head-badge glass">
          <span className="mono">MODEL</span>
          <strong className="model-name">{data.settings.model}</strong>
        </div>
      </header>

      <div className="create-layout">
        <motion.section
          initial={false}
          animate={{ opacity: 1, y: 0 }}
          className="glass form-panel"
        >
          <div className="panel-head">
            <div>
              <div className="section-label mono">CREATIVE REQUEST</div>
              <h2>你想看一个什么样的故事？</h2>
            </div>
            <Wand2 size={20} className="accent" />
          </div>

          <label className="field">
            <span>故事前提</span>
            <textarea
              value={premise}
              onChange={(event) => setPremise(event.target.value)}
              rows={6}
              placeholder="例如：雨夜校园悬疑，带一点恋爱，但别太恐怖。"
            />
          </label>

          <div className="prompt-chips">
            {PROMPT_CHIPS.map((chip) => (
              <button key={chip} className="prompt-chip" onClick={() => setPremise(chip)}>
                {chip}
              </button>
            ))}
          </div>

          <div className="field-row">
            <label className="field">
              <span>类型</span>
              <select value={genre} onChange={(event) => setGenre(event.target.value)}>
                <option>悬疑、恋爱</option>
                <option>科幻、悬疑</option>
                <option>奇幻、冒险</option>
                <option>日常、治愈</option>
                <option>黑暗、心理</option>
                <option>赛博朋克、都市</option>
              </select>
            </label>
            <label className="field">
              <span>基调</span>
              <select value={tone} onChange={(event) => setTone(event.target.value)}>
                <option>冷峻、潮湿、克制</option>
                <option>温暖、明亮、轻盈</option>
                <option>压抑、诡异、不安</option>
                <option>热血、浪漫、电影感</option>
                <option>荒诞、黑色幽默</option>
              </select>
            </label>
            <label className="field">
              <span>篇幅</span>
              <select value={length} onChange={(event) => setLength(event.target.value)}>
                <option>短篇</option>
                <option>中篇</option>
                <option>长篇</option>
              </select>
            </label>
          </div>

          <label className="field">
            <span>补充要求 <em>可选</em></span>
            <textarea
              value={extra}
              onChange={(event) => setExtra(event.target.value)}
              rows={3}
              placeholder="例如：想要 2 个结局；希望有一场雨中的 CG；不要出现校园霸凌。"
            />
          </label>

          {error && (
            <div className="inline-error">
              <AlertTriangle size={17} />
              <span>{error}</span>
              {!data.secrets.has_api_key && (
                <Link to="/settings" className="text-link">去设置 <ArrowRight size={14} /></Link>
              )}
            </div>
          )}

          <button className="btn btn-primary generate-btn" onClick={() => void generate()} disabled={loading}>
            {loading ? <span className="spinner" /> : <Sparkles size={17} />}
            {loading ? "正在编译故事..." : "开始编译"}
          </button>
        </motion.section>

        <aside className="create-side">
          <div className="glass side-panel">
            <div className="section-label mono">PIPELINE</div>
            <h3>故事编译链</h3>
            <div className="step-list">
              {STEPS.map((item, index) => (
                <div key={item} className={`step-row ${loading && index <= step ? "active" : ""}`}>
                  <span className="mono">{String(index + 1).padStart(2, "0")}</span>
                  <span>{item}</span>
                  {loading && index < step && <span className="step-check">✓</span>}
                </div>
              ))}
            </div>
          </div>

          <div className="glass side-panel">
            <div className="section-label mono">STYLE MEMORY</div>
            <h3>风格参考库</h3>
            <p className="muted small">
              已启用 {data.dataset.active_plugins || 0} 个数据集插件，共 {data.dataset.works || 0} 部作品样本。
              核心不内置第三方剧情、图片或音频，可在设置里安装外部插件包。
            </p>
            <div className="chip-cloud">
              <Tag tone="accent">命运石之门</Tag>
              <Tag tone="accent">CLANNAD</Tag>
              <Tag tone="accent">素晴日</Tag>
              <Tag tone="accent">沙耶之歌</Tag>
              <Tag tone="accent">千恋万花</Tag>
              <Tag tone="accent">白色相簿2</Tag>
            </div>
            <Link to="/settings" className="text-link small">
              查看数据集信息 <ArrowRight size={14} />
            </Link>
          </div>

          <div className="glass side-panel security-mini">
            <KeyRound size={20} />
            <div>
              <h3>本地密钥</h3>
              <p className="mono small muted">
                {data.secrets.has_api_key ? data.secrets.masked_key : "未配置"}
              </p>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

