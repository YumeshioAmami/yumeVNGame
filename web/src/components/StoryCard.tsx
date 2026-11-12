import { Link } from "react-router-dom";
import { ArrowUpRight, GitBranch, Sparkles, Users } from "lucide-react";
import type { StoryRecord } from "../types";
import { backgroundUrl } from "../api";
import Tag from "./Tag";

export default function StoryCard({
  story,
  index = 0,
  compact = false,
}: {
  story: StoryRecord;
  index?: number;
  compact?: boolean;
}) {
  return (
    <Link
      to={`/play/${story.id}`}
      className={`story-card ${compact ? "compact" : ""}`}
      style={{ animationDelay: `${index * 70}ms` }}
    >
      <div
        className="story-cover"
        style={{ backgroundImage: `url(${backgroundUrl(story.cover)})` }}
      >
        <div className="story-cover-shade" />
        <div className="story-source mono">
          {story.source === "ai" ? "AI COMPILED" : "DEMO PACKAGE"}
        </div>
        <div className="story-open">
          <ArrowUpRight size={16} />
        </div>
      </div>
      <div className="story-body">
        <div className="story-meta mono">
          <span>{story.theme || "UNTITLED"}</span>
          <span>{story.node_count} NODES</span>
        </div>
        <h3>{story.title}</h3>
        <p>{story.logline || story.synopsis}</p>
        <div className="story-tags">
          {(story.genre || []).slice(0, 3).map((genre) => (
            <Tag key={genre} tone="accent">
              {genre}
            </Tag>
          ))}
          <Tag>{story.tone}</Tag>
        </div>
        <div className="story-stats">
          <span><GitBranch size={14} /> {story.ending_count} endings</span>
          <span><Users size={14} /> {story.character_count} cast</span>
          <span><Sparkles size={14} /> {story.status}</span>
        </div>
      </div>
    </Link>
  );
}

