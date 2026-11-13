from __future__ import annotations

import json
import argparse
import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "datasets" / "local" / "text_vn"
RAW = OUT / "raw"
LEGACY_RAW = ROOT / "datasets" / "text_vn" / "raw"
API = "https://zh.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "yumeVNGame-dataset-builder/0.1 (local research)"}


WORKS = [
    {
        "id": "steins_gate",
        "title_zh": "命运石之门",
        "title_original": "STEINS;GATE",
        "wiki": "命运石之门",
        "developer": "5pb. / Nitroplus",
        "year": 2009,
        "genres": ["科幻", "悬疑", "时间旅行"],
        "themes": ["因果", "选择", "记忆", "世界线"],
        "tags": ["时间循环", "世界线", "中二病", "电话微波炉"],
        "narrative_devices": ["多世界线", "因果反噬", "慢热铺垫", "细节回收"],
        "pacing_notes": "前半用日常和玩笑埋线，后半连续反转；情绪重量来自前期的关系积累。",
        "character_notes": "中二外壳是保护色，真正的脆弱在壳裂开时才暴露。",
        "fallback_summary": "主角冈部伦太郎自称疯狂科学家，与伙伴在秋叶原开发出能向过去发送短信的装置。一次次改变过去带来更严重的后果，他必须在世界线收束与重要之人的命运之间做出选择。",
    },
    {
        "id": "clannad",
        "title_zh": "CLANNAD",
        "title_original": "CLANNAD",
        "wiki": "CLANNAD",
        "developer": "Key",
        "year": 2004,
        "genres": ["恋爱", "日常", "家庭"],
        "themes": ["家庭", "成长", "失去", "奇迹"],
        "tags": ["家族", "校园", "催泪", "光玉"],
        "narrative_devices": ["多路线", "日常积累", "家庭主题", "情绪回收"],
        "pacing_notes": "日常越长，后面的失去越重；奇迹必须建立在代价之上。",
        "character_notes": "人物不是等待被拯救，而是在关系里学会承担。",
        "fallback_summary": "不良少年冈崎朋也在校园里遇见古河渚，并逐渐走进她与周围人的生活。故事从校园恋爱延伸到家庭、工作与失去，讨论人如何在创伤之后继续生活。",
    },
    {
        "id": "subahibi",
        "title_zh": "素晴日",
        "title_original": "素晴らしき日々",
        "wiki": "素晴日",
        "developer": "KeroQ",
        "year": 2010,
        "genres": ["心理", "悬疑", "哲学"],
        "themes": ["认知", "疯狂", "救赎", "幸福"],
        "tags": ["不可靠叙述", "多视角", "哲学引用", "电波"],
        "narrative_devices": ["不可靠叙述", "多视角", "认知崩塌", "首尾呼应"],
        "pacing_notes": "先让读者相信一个版本，再用视角切换拆掉它；真相不是解释，而是重新理解。",
        "character_notes": "每个人都在用自己的方式解释世界，人物声音必须能区分。",
        "fallback_summary": "故事围绕一群少年少女的夏日与日常展开，通过多个视角逐步揭示认知、创伤与幸福之间的裂缝。叙事不断重写读者对事件的理解。",
    },
    {
        "id": "saya_no_uta",
        "title_zh": "沙耶之歌",
        "title_original": "沙耶の唄",
        "wiki": "沙耶之歌",
        "developer": "Nitroplus",
        "year": 2003,
        "genres": ["恐怖", "恋爱", "猎奇"],
        "themes": ["异化", "爱", "感知", "孤独"],
        "tags": ["感官错位", "极端恋爱", "短篇", "肉块"],
        "narrative_devices": ["感官错位", "短篇压缩", "极端亲密", "伦理结局"],
        "pacing_notes": "短篇要少人物、少地点、强概念；每个场景都推进伦理后果。",
        "character_notes": "恐怖与亲密并存，关键是让玩家理解主角为什么无法回头。",
        "fallback_summary": "车祸后，匂坂郁纪的世界变成由血肉与噪声构成的异样景象。唯一看起来正常的是少女沙耶。两人相互依存，但沙耶的真实身份逐渐浮出水面。",
    },
    {
        "id": "yosuga_no_sora",
        "title_zh": "缘之空",
        "title_original": "ヨスガノソラ",
        "wiki": "缘之空",
        "developer": "Sphere",
        "year": 2008,
        "genres": ["恋爱", "乡村", "禁忌"],
        "themes": ["孤独", "依恋", "禁忌", "归属"],
        "tags": ["多路线", "乡村", "禁忌关系", "双子"],
        "narrative_devices": ["多路线", "封闭空间", "季节描写", "关系压力"],
        "pacing_notes": "乡村的安静与重复放大孤独；禁忌关系的力量来自外部压力。",
        "character_notes": "每个角色都在寻找一个能容纳自己的地方。",
        "fallback_summary": "双胞胎春日野悠与穹因父母事故搬到乡下小镇。悠在与不同少女的相处中寻找新的生活，而穹与悠之间不可言说的依恋逐渐浮出水面。",
    },
    {
        "id": "senren_banka",
        "title_zh": "千恋＊万花",
        "title_original": "千恋＊万花",
        "wiki": "千恋万花",
        "developer": "Yuzusoft",
        "year": 2016,
        "genres": ["恋爱", "奇幻", "和风"],
        "themes": ["刀", "宿命", "日常", "守护"],
        "tags": ["和风", "萌系", "多路线", "神社"],
        "narrative_devices": ["和风日常", "路线分工", "小冲突", "轻喜剧"],
        "pacing_notes": "生活质感优先：祭典、食物、神社、雨、木廊；冲突可以小而具体。",
        "character_notes": "萌系不是没有性格，笑点要服务于人物关系。",
        "fallback_summary": "主人公造访以刀与神社闻名的温泉小镇，卷入拔刀与诅咒相关的事件。故事在和风日常、恋爱与守护小镇的冲突之间展开。",
    },
    {
        "id": "white_album_2",
        "title_zh": "白色相簿2",
        "title_original": "WHITE ALBUM2",
        "wiki": "白色相簿2",
        "developer": "Leaf",
        "year": 2010,
        "genres": ["恋爱", "音乐", "青春"],
        "themes": ["三角关系", "背叛", "成长", "遗憾"],
        "tags": ["三角恋", "音乐", "胃痛", "校园"],
        "narrative_devices": ["三角关系", "音乐场景", "道德重量", "不可逆选择"],
        "pacing_notes": "同一首歌在不同阶段有不同含义；冲突来自三个人都认为自己在做正确的事。",
        "character_notes": "不要写谁对谁错，要写每个人如何伤害别人又试图补偿。",
        "fallback_summary": "三名高中生在轻音乐同好会中相遇，彼此的才华、依恋与选择逐渐把关系推向无法回头的位置。故事从校园延伸到成年，讨论爱与伤害的长期后果。",
    },
    {
        "id": "fate_stay_night",
        "title_zh": "Fate/stay night",
        "title_original": "Fate/stay night",
        "wiki": "Fate/stay night",
        "developer": "Type-Moon",
        "year": 2004,
        "genres": ["奇幻", "战斗", "恋爱"],
        "themes": ["理想", "正义", "牺牲", "身份"],
        "tags": ["圣杯战争", "三路线", "英灵", "世界观"],
        "narrative_devices": ["多路线", "理念冲突", "设定密度", "战斗即论证"],
        "pacing_notes": "设定信息必须由人物冲突承载；多路线回答不同问题，而不是重复同一场战争。",
        "character_notes": "理想主义要被现实反复撞击，人物才会变化。",
        "fallback_summary": "少年卫宫士郎卷入争夺圣杯的魔术师战争，与从者 Saber 缔结契约。不同路线围绕理想、正义与拯救的意义展开。",
    },
    {
        "id": "higurashi",
        "title_zh": "寒蝉鸣泣之时",
        "title_original": "ひぐらしのなく頃に",
        "wiki": "寒蝉鸣泣之时",
        "developer": "07th Expansion",
        "year": 2002,
        "genres": ["恐怖", "悬疑", "轮回"],
        "themes": ["信任", "暴力", "轮回", "乡村"],
        "tags": ["轮回", "碎片", "乡村", "雏见泽"],
        "narrative_devices": ["轮回碎片", "信息差", "信任崩塌", "解谜篇"],
        "pacing_notes": "每一轮都必须提供新信息；恐怖来自信任崩塌，而不是单纯怪物。",
        "character_notes": "同一个角色在不同碎片里可以呈现完全不同的面貌。",
        "fallback_summary": "少年前原圭一搬到封闭村落雏见泽，与同伴度过日常。祭典前后，村庄的旧习俗与连续死亡事件让日常逐渐崩坏，故事以多个“碎片”反复重演。",
    },
    {
        "id": "tsukihime",
        "title_zh": "月姬",
        "title_original": "月姫",
        "wiki": "月姬",
        "developer": "Type-Moon",
        "year": 2000,
        "genres": ["吸血鬼", "悬疑", "恋爱"],
        "themes": ["死", "欲望", "身份", "孤独"],
        "tags": ["吸血鬼", "多路线", "直死之魔眼", "都市"],
        "narrative_devices": ["多路线", "感官细节", "能力代价", "恐怖恋爱"],
        "pacing_notes": "夜、血、铁锈、呼吸；能力必须有代价和限制。",
        "character_notes": "恋爱与恐怖互相加压，而不是互相削弱。",
        "fallback_summary": "远野志贵拥有能看见事物死线的眼睛，在夜晚遇见吸血鬼爱尔奎特。围绕连续杀人事件，他逐渐接触非人世界与自己身世的秘密。",
    },
    {
        "id": "ever17",
        "title_zh": "Ever17",
        "title_original": "Ever17 -the out of infinity-",
        "wiki": "Ever17",
        "developer": "KID",
        "year": 2002,
        "genres": ["科幻", "悬疑", "密室"],
        "themes": ["时间", "视角", "欺骗", "生存"],
        "tags": ["叙述性诡计", "密室", "多视角", "海底"],
        "narrative_devices": ["叙述性诡计", "视角限制", "密室结构", "真相回收"],
        "pacing_notes": "诡计必须建立在视角限制上；真相揭示后，前文必须仍然成立。",
        "character_notes": "不同视角要提供不同信息，而不是重复同一段剧情。",
        "fallback_summary": "七名男女被困在海底主题公园，事故与倒计时逼迫他们寻找逃生方法。不同视角的路线逐渐指向一个无法用常规时间线解释的真相。",
    },
    {
        "id": "428_shibuya",
        "title_zh": "428 被封锁的涩谷",
        "title_original": "428 〜封鎖された渋谷で〜",
        "wiki": "428 被封锁的涩谷",
        "developer": "Chunsoft",
        "year": 2008,
        "genres": ["悬疑", "群像", "现实"],
        "themes": ["命运交错", "选择", "城市", "因果"],
        "tags": ["多主角", "时间线", "真人演出", "涩谷"],
        "narrative_devices": ["多主角", "时间压力", "因果链", "选择连锁"],
        "pacing_notes": "一个人的小选择改变另一个人的命运；时间压力可以替代章节结构。",
        "character_notes": "多主角要有不同的语言节奏和信息渠道。",
        "fallback_summary": "涩谷发生绑架案，五名主角在一天内被卷入同一场危机。不同人物的选择互相影响，逐步拼出事件全貌。",
    },
    {
        "id": "air",
        "title_zh": "AIR",
        "title_original": "AIR",
        "wiki": "AIR (视觉小说)",
        "developer": "Key",
        "year": 2000,
        "genres": ["恋爱", "奇幻", "治愈"],
        "themes": ["宿命", "飞翔", "记忆", "告别"],
        "tags": ["夏日", "翼人", "催泪", "海边"],
        "narrative_devices": ["季节结构", "记忆回收", "宿命", "奇迹代价"],
        "pacing_notes": "夏天、海风、蝉鸣是情绪结构；奇迹必须与接受失去同时存在。",
        "character_notes": "人物不是等待拯救，而是在有限时间里完成告别。",
        "fallback_summary": "旅行艺人国崎往人来到海边小镇，遇见少女神尾观铃。故事从夏日日常逐渐揭开翼人、记忆与宿命的旧约。",
    },
    {
        "id": "kanon",
        "title_zh": "Kanon",
        "title_original": "Kanon",
        "wiki": "Kanon",
        "developer": "Key",
        "year": 1999,
        "genres": ["恋爱", "日常", "奇幻"],
        "themes": ["记忆", "约定", "冬天", "失去"],
        "tags": ["雪", "多路线", "催泪", "校园"],
        "narrative_devices": ["多路线", "记忆缺失", "约定", "季节意象"],
        "pacing_notes": "雪与冬天要参与叙事；记忆缺失不是谜题，而是情感代价。",
        "character_notes": "每个角色的口头禅和习惯要能成为记忆锚点。",
        "fallback_summary": "少年相泽祐一回到七年未见的北方小镇，与表妹和多名少女重逢。过去的约定与失去的记忆逐渐回到现在。",
    },
    {
        "id": "little_busters",
        "title_zh": "Little Busters!",
        "title_original": "リトルバスターズ!",
        "wiki": "Little Busters!",
        "developer": "Key",
        "year": 2007,
        "genres": ["青春", "友情", "成长"],
        "themes": ["友情", "告别", "世界", "创伤"],
        "tags": ["棒球", "友情", "轮回", "校园"],
        "narrative_devices": ["友情群像", "世界设定", "重复日常", "告别"],
        "pacing_notes": "日常喜剧必须真有趣；重复的世界要在重复中逐渐变化。",
        "character_notes": "群像要有一个核心关系网，而不是角色轮流登场。",
        "fallback_summary": "直枝理树与童年伙伴组成 Little Busters，在校园里度过热闹日常。随着新成员加入，隐藏在世界结构下的创伤与告别逐渐显现。",
    },
    {
        "id": "muv_luv_alt",
        "title_zh": "Muv-Luv Alternative",
        "title_original": "マブラヴ オルタネイティヴ",
        "wiki": "Muv-Luv Alternative",
        "developer": "âge",
        "year": 2006,
        "genres": ["科幻", "战争", "机甲"],
        "themes": ["战争", "牺牲", "平行世界", "绝望"],
        "tags": ["机甲", "平行世界", "绝望", "战术"],
        "narrative_devices": ["平行世界", "战争加码", "心理代价", "具体死亡"],
        "pacing_notes": "绝望要一层层加码，但每层都给人物一个选择；战争要有具体战术和具体死亡。",
        "character_notes": "机甲是人物关系的延伸，不是独立玩具展示。",
        "fallback_summary": "白银武从和平世界跳到被 BETA 侵略的平行世界，加入联合国军并驾驶战术机。他试图改变人类败亡的命运，却不断付出心理与关系代价。",
    },
    {
        "id": "grisaia",
        "title_zh": "灰色的果实",
        "title_original": "グリザイアの果実",
        "wiki": "灰色的果实",
        "developer": "Frontwing",
        "year": 2011,
        "genres": ["校园", "悬疑", "黑暗"],
        "themes": ["创伤", "救赎", "伪装", "孤独"],
        "tags": ["孤岛", "多路线", "黑暗过去", "美少女"],
        "narrative_devices": ["孤岛封闭", "多路线创伤", "伪装主角", "救赎"],
        "pacing_notes": "每个角色的黑暗过去要有不同形态：暴力、控制、羞耻、依赖。",
        "character_notes": "主角的万能必须有空洞，否则会失去张力。",
        "fallback_summary": "转学生风见雄二进入只有五名学生的美滨学园，与各有创伤的少女相处。看似平静的校园生活逐渐揭开每个人的过去与雄二自己的空洞。",
    },
]


def _get(params: dict) -> dict:
    last_error: Exception | None = None
    for attempt in range(4):
        response = requests.get(API, params={**params, "format": "json"}, headers=HEADERS, timeout=30)
        if response.status_code == 429:
            time.sleep(4 * (attempt + 1))
            last_error = requests.HTTPError(f"429 rate limited", response=response)
            continue
        response.raise_for_status()
        return response.json()
    raise last_error or RuntimeError("wiki request failed")


def resolve_title(title: str) -> str:
    data = _get(
        {
            "action": "query",
            "prop": "extracts",
            "explaintext": 1,
            "redirects": 1,
            "titles": title,
        }
    )
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    if page.get("missing") is not None or "extract" not in page:
        search = _get(
            {
                "action": "query",
                "list": "search",
                "srsearch": title,
                "srlimit": 1,
            }
        )
        hits = search.get("query", {}).get("search", [])
        if hits:
            return hits[0]["title"]
        return ""
    return page.get("title", title)


def fetch_extract(title: str) -> tuple[str, str, str]:
    resolved = resolve_title(title)
    if not resolved:
        return "", title, "missing"
    data = _get(
        {
            "action": "query",
            "prop": "extracts",
            "explaintext": 1,
            "redirects": 1,
            "titles": resolved,
        }
    )
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    extract = page.get("extract") or ""
    return extract, resolved, "ok" if extract else "missing"


def extract_plot(text: str) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    headings: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        if re.match(r"^==+.*==+$", line.strip()):
            headings.append((index, line.strip("= ").strip()))
    keywords = ("剧情", "故事", "情节", "概要", "内容", "Plot", "Synopsis", "Story")
    for position, (start, heading) in enumerate(headings):
        if any(keyword in heading for keyword in keywords):
            end = headings[position + 1][0] if position + 1 < len(headings) else min(len(lines), start + 140)
            section = "\n".join(lines[start + 1 : end]).strip()
            section = re.sub(r"\n{3,}", "\n\n", section)
            if len(section) > 80:
                return section[:3000]
    # fallback: first substantial paragraphs
    body = "\n".join(lines).strip()
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body[:2200]


def main(offline: bool = False) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    records = []
    for index, work in enumerate(WORKS, start=1):
        print(f"[{index}/{len(WORKS)}] {work['title_zh']}")
        if offline:
            legacy = LEGACY_RAW / f"{work['id']}.txt"
            current = RAW / f"{work['id']}.txt"
            source_path = current if current.exists() else legacy
            if source_path.exists():
                text = source_path.read_text(encoding="utf-8")
                resolved = work["wiki"]
                status = "offline_cache"
            else:
                text, resolved, status = "", work["wiki"], "offline_missing"
        else:
            try:
                text, resolved, status = fetch_extract(work["wiki"])
            except Exception as exc:
                text, resolved, status = "", work["wiki"], f"error: {exc}"
        if text:
            (RAW / f"{work['id']}.txt").write_text(text, encoding="utf-8")
        summary = extract_plot(text) if text else work["fallback_summary"]
        summary_source = (
            f"https://zh.wikipedia.org/wiki/{quote(resolved)}"
            if text
            else "editorial_fallback"
        )
        record = {
            "id": work["id"],
            "title_zh": work["title_zh"],
            "title_original": work["title_original"],
            "developer": work["developer"],
            "year": work["year"],
            "genres": work["genres"],
            "themes": work["themes"],
            "tags": work["tags"],
            "narrative_devices": work["narrative_devices"],
            "pacing_notes": work["pacing_notes"],
            "character_notes": work["character_notes"],
            "summary_zh": summary,
            "summary_source": summary_source,
            "source_urls": [f"https://zh.wikipedia.org/wiki/{quote(resolved)}"] if text else [],
            "license_note": "Plot summary source: Wikipedia (CC BY-SA). Metadata and structural notes: yumeVNGame editorial.",
            "fetch_status": status,
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        records.append(record)
        if not offline:
            time.sleep(1.2)

    with (OUT / "works.jsonl").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    manifest = {
        "name": "yumeVNGame Text VN Dataset",
        "version": "0.1.0",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "work_count": len(records),
        "source_policy": "Public encyclopedia plot summaries; no game binaries or full commercial scripts.",
        "fields": [
            "id",
            "title_zh",
            "title_original",
            "developer",
            "year",
            "genres",
            "themes",
            "tags",
            "narrative_devices",
            "pacing_notes",
            "character_notes",
            "summary_zh",
            "summary_source",
            "source_urls",
            "license_note",
            "fetch_status",
        ],
        "note": "Use for style/structure reference and few-shot/RAG; do not redistribute full copyrighted scripts.",
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    plugin = {
        "id": "text-vn-official",
        "name": "Official Text VN Style Pack",
        "version": "0.1.0",
        "type": "dataset",
        "description": "Optional research pack of visual novel plot summaries and editorial style notes. Built locally, not shipped with the core app.",
        "author": "yumeVNGame contributors / public encyclopedia sources",
        "license": "Plot summaries: CC BY-SA with source links; editorial metadata: see NOTICE.md",
        "enabled_by_default": False,
        "data_file": "works.jsonl",
        "context_file": "style_notes.md",
        "tags": ["dataset", "text", "style", "external"],
    }
    (OUT / "plugin.json").write_text(
        json.dumps(plugin, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    style_source = ROOT / "plugins" / "example-dataset" / "style_notes.md"
    if style_source.exists():
        shutil.copyfile(style_source, OUT / "style_notes.md")
    (OUT / "NOTICE.md").write_text(
        "# Dataset Notice\n\n"
        "Plot summaries are derived from public encyclopedia sources and keep source URLs in works.jsonl.\n"
        "Editorial metadata is original to this project. This pack is external and is not part of the core repository.\n"
        "Do not redistribute game binaries, full commercial scripts, or asset files.\n",
        encoding="utf-8",
    )
    print(f"wrote {len(records)} works to {OUT / 'works.jsonl'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="use cached raw text instead of fetching Wikipedia")
    args = parser.parse_args()
    main(offline=args.offline)

