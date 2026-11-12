import { Lock, Play, Sparkles } from "lucide-react";
import type { GalleryEntry } from "../types";

const LABELS: Record<string, string> = {
  cg: "CG",
  scene: "SCENE",
  sprite_differential: "SPRITE",
  ending: "ENDING",
  music: "MUSIC",
};

export default function GalleryGrid({
  entries,
  onOpen,
}: {
  entries: GalleryEntry[];
  onOpen?: (entry: GalleryEntry) => void;
}) {
  return (
    <div className="gallery-grid">
      {entries.map((entry, index) => (
        <button
          key={entry.id}
          className={`gallery-card ${entry.unlocked ? "unlocked" : "locked"}`}
          style={{ animationDelay: `${index * 40}ms` }}
          onClick={() => entry.unlocked && onOpen?.(entry)}
        >
          <div
            className="gallery-image"
            style={{ backgroundImage: `url(${entry.image})` }}
          >
            <div className="gallery-shade" />
            <span className="gallery-type mono">{LABELS[entry.entry_type] || entry.entry_type}</span>
            {entry.unlocked ? (
              <span className="gallery-open"><Play size={15} /></span>
            ) : (
              <span className="gallery-lock"><Lock size={18} /></span>
            )}
          </div>
          <div className="gallery-caption">
            <h4>{entry.unlocked ? entry.title : "未解锁"}</h4>
            <span className="mono">
              {entry.unlocked ? entry.entry_key : <><Sparkles size={12} /> 继续游玩以解锁</>}
            </span>
          </div>
        </button>
      ))}
    </div>
  );
}

