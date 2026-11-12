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
            AI-NATIVE NARRATIVE ENGINE / V1.0
          </div>
          <h1>
            把世界写成一封
            <span className="gradient-text">会呼吸的信</span>
          </h1>
          <p className="hero-lead">
            不是陪你聊天的 AI，而是会先想清楚整个故事，再把它编译成一部可玩的视觉小说。
            分支、记忆、CG、场景回看，全部从第一天就属于故事本身。
          </p>
          <div className="hero-actions">
            <Link to="/library" className="btn btn-primary">
              进入故事库 <ArrowRight size={17} />
            </Link>
            <Link to="/create" className="btn btn-ghost">
              <Wand2 size={17} /> 编译一个新故事
            </Link>
          </div>
          <div className="hero-tags">
            <Tag tone="accent">持久世界</Tag>
            <Tag tone="warm">分支叙事</Tag>
            <Tag>本地优先</Tag>
            <Tag>模型无关</Tag>
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
            <div className="orbit-core-label mono">STORY CORE</div>
            <div className="orbit-core-num">{data.stories.length.toString().padStart(2, "0")}</div>
            <div className="orbit-core-sub">compiled worlds</div>
          </div>
          <div className="orbit-node node-a">
            <BrainCircuit size={17} />
            <span>DIRECTOR</span>
          </div>
          <div className="orbit-node node-b">
            <GitBranch size={17} />
            <span>ROUTE GRAPH</span>
          </div>
          <div className="orbit-node node-c">
            <Images size={17} />
            <span>VISUAL LEDGER</span>
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
          { label: "故事档案", value: data.stats.stories, icon: BookOpen },
          { label: "回廊解锁", value: data.stats.gallery_unlocks, icon: Images },
          { label: "本地存档", value: data.stats.saves, icon: GitBranch },
          { label: "风格样本", value: data.dataset.works || 0, icon: Sparkles },
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
            <h2>最近的故事</h2>
          </div>
          <Link to="/library" className="text-link">
            查看全部 <ArrowRight size={15} />
          </Link>
        </div>
        <div className="story-grid">
          {featured.map((story, index) => (
            <StoryCard key={story.id} story={story} index={index} />
          ))}
          <Link to="/create" className="story-card create-card">
            <div className="create-card-inner">
              <div className="create-glyph">+</div>
              <h3>编译新世界</h3>
              <p>给出一个前提，剩下的交给导演、场景作家和视觉账本。</p>
              <span className="mono">AI STORY COMPILER</span>
            </div>
          </Link>
        </div>
      </section>

      <section className="pipeline-grid">
        {[
          {
            step: "01",
            title: "故事编译",
            text: "先设计完整故事图、结局和伏笔，再生成正文。不是边写边编。",
            icon: BrainCircuit,
          },
          {
            step: "02",
            title: "视觉解析",
            text: "每个节点必须有背景或 CG；同地点复用，时段只换滤镜；立绘和差分按场景出场。",
            icon: Images,
          },
          {
            step: "03",
            title: "记忆回廊",
            text: "存档、分支、CG、场景回看和立绘差分查看，都是故事包的正式组成。",
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
          <h3>API Key 只存在于你的用户数据目录</h3>
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

