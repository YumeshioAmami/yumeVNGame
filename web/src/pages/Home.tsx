import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowRight,
  BookOpen,
  BrainCircuit,
  GitBranch,
  Images,
  KeyRound,
  Sparkles,
  Wand2,
} from "lucide-react";
import { useApp } from "../app-context";
import StoryCard from "../components/StoryCard";
import Tag from "../components/Tag";

export default function Home() {
  const { data } = useApp();
  const featured = data.stories.slice(0, 3);

  return (
    <div className="page home-page">
      <section className="hero">
        <motion.div
          initial={false}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.2, 0.8, 0.2, 1] }}
          className="hero-copy"
        >
          <div className="eyebrow mono">
            <span className="pulse-dot" />
            YUME STORY ROOM / 0.1.0
          </div>
          <h1>
            今晚，想走进
            <span className="gradient-text">谁的故事？</span>
          </h1>
          <p className="hero-lead">
            不是冷冰冰的生成器。先让故事完整地存在，再陪你一幕一幕走进去。
            分支、记忆、CG、回看，都留在故事里等你回来。
          </p>
          <div className="hero-actions">
            <Link to="/library" className="btn btn-primary">
              逛逛故事房间 <ArrowRight size={17} />
            </Link>
            <Link to="/create" className="btn btn-ghost">
              <Wand2 size={17} /> 写一个新故事
            </Link>
          </div>
          <div className="hero-tags">
            <Tag tone="accent">慢慢看</Tag>
            <Tag tone="warm">有分支</Tag>
            <Tag>会记住你</Tag>
            <Tag>只在本机</Tag>
          </div>
        </motion.div>

        <motion.div
          initial={false}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ duration: 0.8, delay: 0.12 }}
          className="hero-orbit glass"
        >
          <div className="orbit-ring ring-a" />
          <div className="orbit-ring ring-b" />
          <div className="orbit-core">
            <div className="orbit-core-label mono">STORY ROOM</div>
            <div className="orbit-core-num">{data.stories.length.toString().padStart(2, "0")}</div>
            <div className="orbit-core-sub">个故事房间</div>
          </div>
          <div className="orbit-node node-a">
            <BrainCircuit size={17} />
            <span>导演</span>
          </div>
          <div className="orbit-node node-b">
            <GitBranch size={17} />
            <span>故事路线</span>
          </div>
          <div className="orbit-node node-c">
            <Images size={17} />
            <span>画面账本</span>
          </div>
          <div className="orbit-data mono">
            <span>KEY {data.secrets.has_api_key ? "READY" : "MISSING"}</span>
            <span>STYLE {data.dataset.works || 0}</span>
            <span>SAVES {data.stats.saves}</span>
          </div>
        </motion.div>
      </section>

      <section className="stat-strip">
        {[
          { label: "故事房间", value: data.stats.stories, icon: BookOpen },
          { label: "回忆碎片", value: data.stats.gallery_unlocks, icon: Images },
          { label: "本地存档", value: data.stats.saves, icon: GitBranch },
          { label: "灵感样本", value: data.dataset.works || 0, icon: Sparkles },
        ].map((item, index) => {
          const Icon = item.icon;
          return (
            <motion.div
              key={item.label}
              initial={false}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.06 }}
              className="stat-card glass"
            >
              <div className="stat-icon"><Icon size={18} /></div>
              <div>
                <div className="stat-value">{item.value}</div>
                <div className="stat-label mono">{item.label}</div>
              </div>
            </motion.div>
          );
        })}
      </section>

      <section className="section-block">
        <div className="section-head">
          <div>
            <div className="section-label mono">COMPILED WORLDS</div>
            <h2>最近的故事房间</h2>
          </div>
          <Link to="/library" className="text-link">
            全部房间 <ArrowRight size={15} />
          </Link>
        </div>
        <div className="story-grid">
          {featured.map((story, index) => (
            <StoryCard key={story.id} story={story} index={index} />
          ))}
          <Link to="/create" className="story-card create-card">
            <div className="create-card-inner">
              <div className="create-glyph">+</div>
              <h3>写一个新故事</h3>
              <p>给出一个感觉，剩下的交给导演、场景和一点点魔法。</p>
              <span className="mono">START A NEW STORY</span>
            </div>
          </Link>
        </div>
      </section>

      <section className="pipeline-grid">
        {[
          {
            step: "01",
            title: "先想好故事",
            text: "先让整个故事完整地存在，再一幕一幕展开。不是边写边编。",
            icon: BrainCircuit,
          },
          {
            step: "02",
            title: "让画面出现",
            text: "每个场景都有背景或 CG；同地点复用，时段换滤镜；该出现的人会带着差分出现。",
            icon: Images,
          },
          {
            step: "03",
            title: "把回忆留下",
            text: "存档、分支、CG、场景回看和立绘差分查看，都是故事的一部分。",
            icon: GitBranch,
          },
        ].map((item, index) => {
          const Icon = item.icon;
          return (
            <motion.div
              key={item.step}
              initial={false}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ delay: index * 0.08 }}
              className="pipeline-card glass"
            >
              <div className="pipeline-top">
                <span className="mono pipeline-step">{item.step}</span>
                <Icon size={20} />
              </div>
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </motion.div>
          );
        })}
      </section>

      <section className="security-strip glass">
        <div className="security-icon"><KeyRound size={22} /></div>
        <div>
          <div className="section-label mono">LOCAL SECURITY</div>
          <h3>你的密钥只留在这台电脑上</h3>
          <p>
            Key 使用 Fernet 加密后写入本机 <span className="mono">%APPDATA%/yumeVNGame</span>，
            不进入仓库、不进入故事包、不随任何请求上传到第三方存储。
          </p>
        </div>
        <Link to="/settings" className="btn btn-ghost small">
          管理密钥 <ArrowRight size={14} />
        </Link>
      </section>
    </div>
  );
}

