import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Bookmark,
  ChevronRight,
  Images,
  Loader2,
  RotateCcw,
  Settings,
  Volume2,
} from "lucide-react";
import { api, backgroundUrl, cgUrl, spriteUrl } from "../api";
import { useApp } from "../app-context";
import type { GalleryEntry, SessionPayload } from "../types";
import GalleryGrid from "../components/GalleryGrid";
import Modal from "../components/Modal";

function positionClass(position?: string) {
  if (position === "left") return "pos-left";
  if (position === "right") return "pos-right";
  return "pos-center";
}

export default function Player() {
  const { storyId = "" } = useParams();
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();
  const { data, refresh } = useApp();
  const [payload, setPayload] = useState<SessionPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [displayed, setDisplayed] = useState("");
  const [textDone, setTextDone] = useState(false);
  const [showSave, setShowSave] = useState(false);
  const [showGallery, setShowGallery] = useState(false);
  const [saveName, setSaveName] = useState("手动存档");
  const [saves, setSaves] = useState<Array<Record<string, unknown>>>([]);
  const [gallery, setGallery] = useState<GalleryEntry[]>([]);
  const [busy, setBusy] = useState(false);
  const stageRef = useRef<HTMLDivElement>(null);

  const node = payload?.node;
  const story = payload?.story;
  const session = payload?.session;
  const fullText = node?.text || "";

  const loadStory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const sessionId = params.get("session");
      const next = sessionId
        ? await api.session(sessionId)
        : await api.createSession(storyId);
      setPayload(next);
      if (!sessionId) {
        setParams({ session: next.session.id }, { replace: true });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "无法载入故事");
    } finally {
      setLoading(false);
    }
  }, [params, setParams, storyId]);

  useEffect(() => {
    void loadStory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [storyId]);

  useEffect(() => {
    if (!node) return;
    setDisplayed("");
    setTextDone(false);
    let index = 0;
    const timer = window.setInterval(() => {
      index += 1;
      setDisplayed(fullText.slice(0, index));
      if (index >= fullText.length) {
        window.clearInterval(timer);
        setTextDone(true);
      }
    }, 22);
    return () => window.clearInterval(timer);
  }, [node?.id, fullText]);

  const characterMap = useMemo(() => {
    const map = new Map<string, NonNullable<SessionPayload["story"]["package"]>["characters"][number]>();
    story?.package?.characters.forEach((character) => map.set(character.id, character));
    return map;
  }, [story]);

  async function advance() {
    if (!node || !session) return;
    if (!textDone) {
      setDisplayed(fullText);
      setTextDone(true);
      return;
    }
    if (node.choices?.length) return;
    if (node.ending) return;
    setBusy(true);
    try {
      const next = await api.next(session.id);
      setPayload(next);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "推进失败");
    } finally {
      setBusy(false);
    }
  }

  async function choose(index: number) {
    if (!session) return;
    setBusy(true);
    try {
      const next = await api.choose(session.id, index);
      setPayload(next);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "选择失败");
    } finally {
      setBusy(false);
    }
  }

  async function openSave() {
    setShowSave(true);
    if (story) {
      setSaves(await api.saves(story.id));
    }
  }

  async function saveGame() {
    if (!session) return;
    setBusy(true);
    try {
      await api.save(session.id, saveName || "手动存档");
      setSaves(await api.saves(story!.id));
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function loadGame(saveId: string) {
    setBusy(true);
    try {
      const next = await api.load(saveId);
      setPayload(next);
      setParams({ session: next.session.id }, { replace: true });
      setShowSave(false);
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function openGallery() {
    if (!story) return;
    setShowGallery(true);
    setGallery(await api.gallery(story.id));
  }

  async function speak() {
    if (!node) return;
    const text = `${node.narration || ""} ${node.text || ""}`;
    try {
      const result = await api.tts(text);
      if (result.audio_base64) {
        const audio = new Audio(`data:${result.mime || "audio/wav"};base64,${result.audio_base64}`);
        await audio.play();
        return;
      }
    } catch {
      // Fall through to browser speech synthesis.
    }
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "zh-CN";
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
  }

  if (loading) {
    return (
      <div className="player-loading">
        <Loader2 className="spin" size={28} />
        <span className="mono">LOADING STORY PACKAGE...</span>
      </div>
    );
  }

  if (error || !payload || !node || !story || !session) {
    return (
      <div className="player-loading">
        <div className="inline-error">{error || "故事包为空"}</div>
        <button className="btn btn-ghost" onClick={() => void loadStory()}>
          重试
        </button>
        <Link className="text-link" to="/library">返回故事库</Link>
      </div>
    );
  }

  const scene = node.scene;
  const isCG = scene.visual_mode === "cg";
  const showSprites = scene.visual_mode === "background_sprites";
  const ending = node.ending;

  return (
    <div className="vn-stage" ref={stageRef}>
      <div
        className={`vn-bg ${isCG ? "is-cg" : ""}`}
        data-filter={scene.filter || "cool"}
        style={{
          backgroundImage: `url(${isCG ? cgUrl(scene.cg) : backgroundUrl(scene.background)})`,
        }}
      />
      <div className="vn-vignette" />
      <div className="vn-scanlines" />
      <div className="vn-particles" />

      {showSprites &&
        (scene.cast || []).map((cast, index) => {
          const character = characterMap.get(cast.character);
          if (!character) return null;
          return (
            <motion.img
              key={`${cast.character}-${index}`}
              initial={{ opacity: 0, y: 30, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.55, delay: index * 0.1 }}
              className={`vn-sprite ${positionClass(cast.position)}`}
              style={{ zIndex: cast.layer || 10, animationDelay: `${index * 0.2}s` }}
              src={spriteUrl(character.sprite, cast.expression || "calm")}
              alt={character.name}
            />
          );
        })}

      <div className="vn-hud">
        <Link className="icon-btn" to="/library" aria-label="返回故事库">
          <ArrowLeft size={18} />
        </Link>
        <div className="vn-title">
          <span className="mono">{story.title}</span>
          <strong>{node.title}</strong>
        </div>
        <div className="vn-controls">
          <button className="icon-btn" onClick={() => void openSave()} title="存档 / 读档">
            <Bookmark size={17} />
          </button>
          <button className="icon-btn" onClick={() => void openGallery()} title="回廊">
            <Images size={17} />
          </button>
          <button className="icon-btn" onClick={speak} title="朗读">
            <Volume2 size={17} />
          </button>
          <Link className="icon-btn" to="/settings" title="设置">
            <Settings size={17} />
          </Link>
        </div>
      </div>

      <div className="vn-chapter mono">
        <span>CHAPTER</span>
        <strong>{String(session.visited.length).padStart(2, "0")}</strong>
        <span>/ {story.package?.nodes.length || 0}</span>
      </div>

      <motion.div
        key={node.id}
        initial={false}
        animate={{ opacity: 1, y: 0 }}
        className="dialogue-wrap"
      >
        {textDone && node.choices?.length ? (
          <div className="choice-stack">
            {node.choices.map((choice, index) => (
              <motion.button
                key={`${choice.to}-${index}`}
                initial={false}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.08 }}
                className="choice-btn"
                onClick={() => void choose(index)}
                disabled={busy}
              >
                <span className="choice-index mono">0{index + 1}</span>
                <span>
                  <strong>{choice.text}</strong>
                  {choice.hint && <em>{choice.hint}</em>}
                </span>
                <ChevronRight size={17} />
              </motion.button>
            ))}
          </div>
        ) : null}

        <div className="dialogue glass" onClick={() => void advance()}>
          <div className="dialogue-head">
            <span className="speaker" style={{ color: characterMap.get(node.speaker)?.color }}>
              {node.speaker || "旁白"}
            </span>
            <span className="mono dialogue-hint">
              {busy ? "SYNCING..." : textDone ? (node.choices ? "CHOOSE A ROUTE" : "CLICK TO CONTINUE") : "TRANSMITTING"}
            </span>
          </div>
          {node.narration && <p className="narration">{node.narration}</p>}
          <p className="dialogue-text">
            {displayed}
            {!textDone && <span className="caret" />}
          </p>
          {textDone && !node.choices?.length && !ending && (
            <button className="continue-btn" onClick={() => void advance()} disabled={busy}>
              继续 <ChevronRight size={16} />
            </button>
          )}
        </div>
      </motion.div>

      {textDone && ending && (
        <motion.div
          initial={false}
          animate={{ opacity: 1, scale: 1 }}
          className="ending-overlay glass"
        >
          <div className="section-label mono">ENDING UNLOCKED</div>
          <h2>{ending.title}</h2>
          <p>{ending.description}</p>
          <div className="ending-actions">
            <button className="btn btn-primary" onClick={() => void openGallery()}>
              <Images size={16} /> 查看回廊
            </button>
            <button className="btn btn-ghost" onClick={() => navigate(`/play/${story.id}`)}>
              <RotateCcw size={16} /> 重新开始
            </button>
            <Link className="btn btn-ghost" to="/library">返回故事库</Link>
          </div>
        </motion.div>
      )}

      <Modal
        open={showSave}
        onClose={() => setShowSave(false)}
        title="存档 / 读档"
        subtitle="本地 SQLite 存档，包含当前节点、分支和历史。"
      >
        <div className="save-create">
          <input
            value={saveName}
            onChange={(event) => setSaveName(event.target.value)}
            placeholder="存档名称"
          />
          <button className="btn btn-primary" onClick={() => void saveGame()} disabled={busy}>
            <Bookmark size={15} /> 保存当前进度
          </button>
        </div>
        <div className="save-list">
          {saves.length === 0 && <p className="muted">还没有存档。</p>}
          {saves.map((save) => (
            <button
              key={String(save.id)}
              className="save-row"
              onClick={() => void loadGame(String(save.id))}
              disabled={busy}
            >
              <div>
                <strong>{String(save.save_name)}</strong>
                <span className="mono">{String(save.current_node_id)}</span>
              </div>
              <span className="mono">{new Date(String(save.created_at)).toLocaleString("zh-CN")}</span>
            </button>
          ))}
        </div>
      </Modal>

      <Modal
        open={showGallery}
        onClose={() => setShowGallery(false)}
        title="故事回廊"
        subtitle="CG、场景、立绘差分和结局都从这里回看。"
        wide
      >
        <GalleryGrid entries={gallery} />
        <div className="modal-foot">
          <Link className="btn btn-ghost small" to={`/gallery/${story.id}`} onClick={() => setShowGallery(false)}>
            打开完整回廊 <ChevronRight size={14} />
          </Link>
        </div>
      </Modal>
    </div>
  );
}

