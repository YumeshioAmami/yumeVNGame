import { useMemo, useState } from "react";
import { Search, SlidersHorizontal } from "lucide-react";
import { useApp } from "../app-context";
import StoryCard from "../components/StoryCard";
import Tag from "../components/Tag";

export default function Library() {
  const { data } = useApp();
  const [query, setQuery] = useState("");
  const [genre, setGenre] = useState("全部");

  const genres = useMemo(() => {
    const set = new Set<string>();
    data.stories.forEach((story) => story.genre?.forEach((item) => set.add(item)));
    return ["全部", ...Array.from(set)];
  }, [data.stories]);

  const stories = useMemo(() => {
    return data.stories.filter((story) => {
      const matchesQuery =
        !query ||
        `${story.title} ${story.logline} ${story.synopsis}`.toLowerCase().includes(query.toLowerCase());
      const matchesGenre = genre === "全部" || story.genre?.includes(genre);
      return matchesQuery && matchesGenre;
    });
  }, [data.stories, genre, query]);

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <div className="eyebrow mono"><span className="pulse-dot" /> STORY ARCHIVE</div>
          <h1>故事库</h1>
          <p className="page-lead">
            已编译的完整故事包。每个故事都带有自己的角色、视觉账本、分支和回廊数据。
          </p>
        </div>
        <div className="head-badge glass">
          <span className="mono">TOTAL</span>
          <strong>{data.stories.length.toString().padStart(2, "0")}</strong>
        </div>
      </header>

      <div className="library-toolbar glass">
        <div className="search-box">
          <Search size={17} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="搜索标题、前提、氛围..."
          />
        </div>
        <div className="genre-row">
          <SlidersHorizontal size={16} className="muted" />
          {genres.map((item) => (
            <button
              key={item}
              className={`filter-chip ${genre === item ? "active" : ""}`}
              onClick={() => setGenre(item)}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      {stories.length === 0 ? (
        <div className="empty-state glass">
          <div className="empty-glyph">∅</div>
          <h3>没有匹配的故事</h3>
          <p>换一个关键词，或者去创作页编译一个新世界。</p>
        </div>
      ) : (
        <div className="story-grid library-grid">
          {stories.map((story, index) => (
            <StoryCard key={story.id} story={story} index={index} />
          ))}
        </div>
      )}

      <div className="library-foot mono">
        <Tag tone="accent">LOCAL SQLITE</Tag>
        <span>所有故事包保存在本机 data/yumevn.db</span>
      </div>
    </div>
  );
}

