import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowRight, Images, Lock, Sparkles } from "lucide-react";
import { api, spriteUrl } from "../api";
import { useApp } from "../app-context";
import type { GalleryEntry, StoryRecord } from "../types";
import GalleryGrid from "../components/GalleryGrid";
import Modal from "../components/Modal";
import Tag from "../components/Tag";

const TABS = [
  { id: "all", label: "全部" },
  { id: "cg", label: "CG 回看" },
  { id: "scene", label: "场景回看" },
  { id: "sprite_differential", label: "立绘差分" },
  { id: "ending", label: "结局收集" },
];

export default function Gallery() {
  const { storyId } = useParams();
  const { data } = useApp();
  const [activeId, setActiveId] = useState(storyId || data.stories[0]?.id || "");
  const [entries, setEntries] = useState<GalleryEntry[]>([]);
  const [story, setStory] = useState<StoryRecord | null>(null);
  const [tab, setTab] = useState("all");
  const [loading, setLoading] = useState(true);
  const [preview, setPreview] = useState<GalleryEntry | null>(null);
  const [expression, setExpression] = useState("calm");

  useEffect(() => {
    if (storyId) setActiveId(storyId);
  }, [storyId]);

  useEffect(() => {
    if (!activeId) return;
    setLoading(true);
    Promise.all([api.gallery(activeId), api.story(activeId)])
      .then(([gallery, record]) => {
        setEntries(gallery);
        setStory(record);
      })
      .finally(() => setLoading(false));
  }, [activeId]);

  const filtered = useMemo(
    () => (tab === "all" ? entries : entries.filter((entry) => entry.entry_type === tab)),
    [entries, tab],
  );

  const unlocked = entries.filter((entry) => entry.unlocked).length;
  const previewNode = preview?.node_id
    ? story?.package?.nodes.find((node) => node.id === preview.node_id)
    : undefined;

  return (
    <div className="page gallery-page">
      <header className="page-head">
        <div>
          <div className="eyebrow mono"><span className="pulse-dot" /> STORY MEMORIES</div>
          <h1>故事回廊</h1>
          <p className="page-lead">
            CG、场景、立绘差分和结局。解锁记录属于本地玩家，不随单个存档回退。
          </p>
        </div>
        <div className="head-badge glass">
          <span className="mono">UNLOCKED</span>
          <strong>{unlocked.toString().padStart(2, "0")}<small>/{entries.length}</small></strong>
        </div>
      </header>

      <div className="gallery-toolbar glass">
        <div className="story-picker">
          <Images size={17} />
          <select value={activeId} onChange={(event) => setActiveId(event.target.value)}>
            {data.stories.map((item) => (
              <option key={item.id} value={item.id}>{item.title}</option>
            ))}
          </select>
        </div>
        <div className="gallery-tabs">
          {TABS.map((item) => {
            const count = item.id === "all" ? entries.length : entries.filter((entry) => entry.entry_type === item.id).length;
            return (
              <button
                key={item.id}
                className={`filter-chip ${tab === item.id ? "active" : ""}`}
                onClick={() => setTab(item.id)}
              >
                {item.label}
                <span className="mono">{count}</span>
              </button>
            );
          })}
        </div>
      </div>

      {loading ? (
        <div className="empty-state glass"><Sparkles className="spin" /> 正在读取回廊...</div>
      ) : filtered.length === 0 ? (
        <div className="empty-state glass">
          <div className="empty-glyph"><Lock size={28} /></div>
          <h3>这个分类还没有条目</h3>
          <p>继续游玩故事，新的 CG、场景和差分会在经过时自动解锁。</p>
            <Link to={`/play/${activeId}`} className="btn btn-primary small">继续故事 <ArrowRight size={14} /></Link>
        </div>
      ) : (
        <GalleryGrid entries={filtered} onOpen={(entry) => { setPreview(entry); setExpression("calm"); }} />
      )}

      {story && (
        <div className="gallery-footnote glass">
          <div>
            <div className="section-label mono">CURRENT STORY</div>
            <h3>{story.title}</h3>
            <p>{story.logline}</p>
          </div>
          <div className="chip-cloud">
            {story.genre?.map((genre) => <Tag key={genre} tone="accent">{genre}</Tag>)}
          </div>
          <Link to={`/play/${story.id}`} className="btn btn-ghost small">
            继续游玩 <ArrowRight size={14} />
          </Link>
        </div>
      )}

      <Modal
        open={Boolean(preview)}
        onClose={() => setPreview(null)}
        title={preview?.title || ""}
        subtitle={preview ? `${preview.entry_type} · ${preview.entry_key}` : ""}
        wide
      >
        {preview && (
          <div className="preview-layout">
            <div className="preview-visual">
              {preview.entry_type === "sprite_differential" ? (
                <img
                  src={spriteUrl(
                    String(preview.payload.sprite || preview.payload.character_id || "rin"),
                    expression,
                  )}
                  alt={preview.title}
                />
              ) : (
                <div
                  className="preview-image"
                  style={{ backgroundImage: `url(${preview.image})` }}
                />
              )}
            </div>
            <div className="preview-side">
              <div className="section-label mono">REPLAY DATA</div>
              {previewNode ? (
                <>
                  <h3>{previewNode.title}</h3>
                  <p className="muted">{previewNode.narration}</p>
                  <blockquote>{previewNode.text}</blockquote>
                  <div className="preview-tags">
                    <Tag tone="accent">{previewNode.scene.visual_mode}</Tag>
                    {previewNode.scene.background && <Tag>{previewNode.scene.background}</Tag>}
                    {previewNode.scene.cg && <Tag tone="warm">{previewNode.scene.cg}</Tag>}
                  </div>
                </>
              ) : preview.entry_type === "sprite_differential" ? (
                <>
                  <h3>立绘差分查看</h3>
                  <p className="muted">同一个角色形态下的表情差分。</p>
                  <div className="expression-row">
                    {((preview.payload.expressions as string[]) || ["calm"]).map((item) => (
                      <button
                        key={item}
                        className={`filter-chip ${expression === item ? "active" : ""}`}
                        onClick={() => setExpression(item)}
                      >
                        {item}
                      </button>
                    ))}
                  </div>
                </>
              ) : (
                <>
                  <h3>{preview.title}</h3>
                  <p className="muted">这条回看记录已经永久加入你的本地回廊。</p>
                </>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

