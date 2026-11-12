from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BG = ROOT / "web" / "public" / "assets" / "backgrounds"
SPR = ROOT / "web" / "public" / "assets" / "sprites"
CG = ROOT / "web" / "public" / "assets" / "cg"


def rain_lines(count: int = 90, width: int = 1600, height: int = 900) -> str:
    out = []
    for i in range(count):
        x = (i * 173 + 37) % width
        y = (i * 97 + 11) % height
        length = 26 + (i % 7) * 9
        opacity = 0.08 + (i % 5) * 0.035
        out.append(
            f'<line x1="{x}" y1="{y}" x2="{x - 14}" y2="{y + length}" '
            f'stroke="#dff6ff" stroke-width="{1 + i % 2}" opacity="{opacity:.2f}"/>'
        )
    return "".join(out)


def stars(count: int = 70, width: int = 1600, height: int = 900) -> str:
    out = []
    for i in range(count):
        x = (i * 211 + 53) % width
        y = (i * 131 + 29) % height
        r = 0.6 + (i % 4) * 0.7
        opacity = 0.18 + (i % 6) * 0.08
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#dff6ff" opacity="{opacity:.2f}"/>')
    return "".join(out)


def svg_background(key: str) -> str:
    palettes = {
        "rain_classroom": ("#050b1d", "#0b2442", "#1e3a5f", "#67e8f9"),
        "school_corridor": ("#070b16", "#162033", "#2a2445", "#c4b5fd"),
        "old_port": ("#040b12", "#0d2c35", "#2a1f16", "#fbbf24"),
        "dorm_night": ("#050711", "#14152b", "#2a1a33", "#a78bfa"),
        "rooftop_rain": ("#030713", "#0b1e3d", "#1e1b4b", "#7dd3fc"),
        "void": ("#020205", "#0a0a18", "#1b0b2e", "#f472b6"),
        "library": ("#120b08", "#2a1810", "#3b2416", "#f59e0b"),
        "station": ("#050710", "#0b1b2e", "#112a3a", "#22d3ee"),
    }
    c0, c1, c2, accent = palettes.get(key, palettes["rain_classroom"])
    extra = ""
    if key in {"rain_classroom", "school_corridor", "old_port", "rooftop_rain"}:
        extra += rain_lines()
    if key in {"void", "station", "dorm_night"}:
        extra += stars()
    if key == "rain_classroom":
        extra += """
        <rect x="120" y="120" width="620" height="430" rx="12" fill="#071a32" opacity="0.72"/>
        <rect x="150" y="150" width="560" height="370" rx="8" fill="none" stroke="#67e8f9" stroke-width="2" opacity="0.35"/>
        <line x1="430" y1="150" x2="430" y2="520" stroke="#67e8f9" stroke-width="2" opacity="0.22"/>
        <line x1="150" y1="335" x2="710" y2="335" stroke="#67e8f9" stroke-width="2" opacity="0.22"/>
        <path d="M70 760 L250 610 L540 760 Z" fill="#0a1220" opacity="0.88"/>
        <rect x="1040" y="620" width="380" height="160" rx="14" fill="#07101d" opacity="0.9"/>
        <rect x="1080" y="650" width="300" height="18" rx="9" fill="#67e8f9" opacity="0.18"/>
        <circle cx="1240" cy="470" r="95" fill="#67e8f9" opacity="0.08"/>
        """
    elif key == "school_corridor":
        extra += """
        <path d="M180 900 L620 420 L980 420 L1420 900 Z" fill="#080d18" opacity="0.9"/>
        <path d="M620 420 L720 900 M980 420 L880 900" stroke="#a78bfa" stroke-width="3" opacity="0.2"/>
        <rect x="700" y="300" width="200" height="160" rx="80" fill="#c4b5fd" opacity="0.08"/>
        <circle cx="800" cy="300" r="46" fill="#c4b5fd" opacity="0.35"/>
        <circle cx="800" cy="300" r="110" fill="none" stroke="#c4b5fd" stroke-width="2" opacity="0.16"/>
        """
    elif key == "old_port":
        extra += """
        <rect x="0" y="610" width="1600" height="290" fill="#02080d" opacity="0.92"/>
        <path d="M0 660 Q200 620 400 660 T800 660 T1200 660 T1600 660" stroke="#fbbf24" stroke-width="2" opacity="0.16" fill="none"/>
        <rect x="180" y="430" width="30" height="210" fill="#101820"/>
        <rect x="150" y="400" width="90" height="36" fill="#101820"/>
        <rect x="1230" y="480" width="180" height="120" fill="#0b1118"/>
        <rect x="1260" y="510" width="120" height="22" fill="#fbbf24" opacity="0.18"/>
        <circle cx="1380" cy="330" r="34" fill="#fbbf24" opacity="0.16"/>
        <path d="M1346 330 L1380 250 L1414 330 Z" fill="#fbbf24" opacity="0.1"/>
        """
    elif key == "dorm_night":
        extra += """
        <rect x="0" y="620" width="1600" height="280" fill="#05060d" opacity="0.95"/>
        <rect x="1130" y="120" width="300" height="360" rx="8" fill="#0b1024"/>
        <rect x="1160" y="150" width="240" height="300" fill="#111a3a" opacity="0.7"/>
        <circle cx="1280" cy="300" r="58" fill="#a78bfa" opacity="0.24"/>
        <rect x="200" y="580" width="420" height="34" rx="10" fill="#12102a" opacity="0.9"/>
        <rect x="260" y="614" width="24" height="120" fill="#12102a"/>
        <rect x="536" y="614" width="24" height="120" fill="#12102a"/>
        """
    elif key == "rooftop_rain":
        extra += """
        <path d="M0 650 L120 520 L240 560 L380 470 L520 540 L700 440 L900 520 L1080 450 L1280 530 L1450 460 L1600 540 L1600 900 L0 900 Z" fill="#050a16" opacity="0.9"/>
        <rect x="0" y="760" width="1600" height="140" fill="#03060e" opacity="0.95"/>
        <circle cx="1220" cy="260" r="90" fill="#7dd3fc" opacity="0.08"/>
        <circle cx="1220" cy="260" r="160" fill="none" stroke="#7dd3fc" stroke-width="2" opacity="0.1"/>
        """
    elif key == "void":
        extra += """
        <circle cx="800" cy="430" r="240" fill="none" stroke="#f472b6" stroke-width="2" opacity="0.18"/>
        <circle cx="800" cy="430" r="360" fill="none" stroke="#a78bfa" stroke-width="1" opacity="0.12"/>
        <path d="M800 180 L900 430 L800 680 L700 430 Z" fill="#f472b6" opacity="0.05"/>
        <path d="M560 430 L800 330 L1040 430 L800 530 Z" fill="#a78bfa" opacity="0.05"/>
        """
    elif key == "library":
        extra += """
        <rect x="80" y="120" width="1440" height="520" rx="16" fill="#170f0b" opacity="0.9"/>
        <g stroke="#f59e0b" stroke-width="2" opacity="0.15">
        <line x1="160" y1="180" x2="160" y2="580"/><line x1="360" y1="180" x2="360" y2="580"/>
        <line x1="560" y1="180" x2="560" y2="580"/><line x1="760" y1="180" x2="760" y2="580"/>
        <line x1="960" y1="180" x2="960" y2="580"/><line x1="1160" y1="180" x2="1160" y2="580"/>
        <line x1="1360" y1="180" x2="1360" y2="580"/>
        <line x1="80" y1="260" x2="1520" y2="260"/><line x1="80" y1="360" x2="1520" y2="360"/>
        <line x1="80" y1="460" x2="1520" y2="460"/>
        </g>
        <circle cx="800" cy="700" r="120" fill="#f59e0b" opacity="0.08"/>
        """
    elif key == "station":
        extra += """
        <rect x="0" y="600" width="1600" height="300" fill="#03050b" opacity="0.94"/>
        <path d="M0 640 L1600 640" stroke="#22d3ee" stroke-width="3" opacity="0.2"/>
        <path d="M0 720 L1600 720" stroke="#22d3ee" stroke-width="1" opacity="0.12"/>
        <rect x="1100" y="120" width="380" height="340" rx="16" fill="#071722" opacity="0.9"/>
        <rect x="1140" y="160" width="300" height="260" fill="#0b2530" opacity="0.7"/>
        <circle cx="1290" cy="290" r="70" fill="#22d3ee" opacity="0.1"/>
        <rect x="160" y="520" width="520" height="10" rx="5" fill="#22d3ee" opacity="0.18"/>
        <rect x="160" y="550" width="360" height="8" rx="4" fill="#22d3ee" opacity="0.1"/>
        """
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{c0}"/><stop offset="0.55" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/>
  </linearGradient>
  <radialGradient id="glow" cx="50%" cy="35%" r="70%">
    <stop offset="0" stop-color="{accent}" stop-opacity="0.22"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.55"/>
  </linearGradient>
</defs>
<rect width="1600" height="900" fill="url(#bg)"/>
<rect width="1600" height="900" fill="url(#glow)"/>
{extra}
<rect width="1600" height="900" fill="url(#fade)"/>
</svg>"""


CHARS = {
    "rin": {"hair": "#67e8f9", "coat": "#0e7490", "skin": "#f5d0c5", "accent": "#22d3ee"},
    "keeper": {"hair": "#fbbf24", "coat": "#1f2937", "skin": "#d6b28a", "accent": "#f59e0b"},
    "teacher": {"hair": "#a3e635", "coat": "#365314", "skin": "#f0c9a8", "accent": "#84cc16"},
    "you": {"hair": "#a78bfa", "coat": "#312e81", "skin": "#f2c9b8", "accent": "#8b5cf6"},
}


def _face(expression: str, color: str) -> str:
    def eyes_open(cx1: int, cx2: int, cy: int = 350, rx: int = 19, ry: int = 25) -> str:
        return f"""
        <ellipse cx="{cx1}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#f8fbff" opacity="0.94"/>
        <ellipse cx="{cx2}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#f8fbff" opacity="0.94"/>
        <ellipse cx="{cx1}" cy="{cy + 2}" rx="{max(8, rx // 2)}" ry="{max(11, ry // 2)}" fill="{color}"/>
        <ellipse cx="{cx2}" cy="{cy + 2}" rx="{max(8, rx // 2)}" ry="{max(11, ry // 2)}" fill="{color}"/>
        <circle cx="{cx1 + 4}" cy="{cy - 7}" r="4" fill="#fff"/>
        <circle cx="{cx2 + 4}" cy="{cy - 7}" r="4" fill="#fff"/>
        """

    if expression == "smile":
        return f"""
        <path d="M238 352 Q260 332 282 352" stroke="{color}" stroke-width="8" fill="none" stroke-linecap="round"/>
        <path d="M318 352 Q340 332 362 352" stroke="{color}" stroke-width="8" fill="none" stroke-linecap="round"/>
        <path d="M268 430 Q300 456 332 430" stroke="{color}" stroke-width="7" fill="none" stroke-linecap="round"/>
        <path d="M222 324 Q246 312 272 320" stroke="{color}" stroke-width="4" opacity="0.45" fill="none"/>
        <path d="M328 320 Q354 312 378 324" stroke="{color}" stroke-width="4" opacity="0.45" fill="none"/>
        """
    if expression == "sad":
        return f"""
        {eyes_open(260, 340, 354, 18, 24)}
        <path d="M228 326 Q254 314 276 326" stroke="{color}" stroke-width="5" fill="none" stroke-linecap="round"/>
        <path d="M324 326 Q346 314 372 326" stroke="{color}" stroke-width="5" fill="none" stroke-linecap="round"/>
        <path d="M270 438 Q300 420 330 438" stroke="{color}" stroke-width="6" fill="none" stroke-linecap="round"/>
        <path d="M286 448 Q300 456 314 448" stroke="{color}" stroke-width="3" opacity="0.5" fill="none"/>
        """
    if expression == "surprised":
        return f"""
        {eyes_open(260, 340, 348, 22, 29)}
        <path d="M226 318 Q252 306 278 316" stroke="{color}" stroke-width="5" fill="none" stroke-linecap="round"/>
        <path d="M322 316 Q348 306 374 318" stroke="{color}" stroke-width="5" fill="none" stroke-linecap="round"/>
        <ellipse cx="300" cy="438" rx="16" ry="22" fill="#120b14" stroke="{color}" stroke-width="5"/>
        """
    if expression == "grim":
        return f"""
        <path d="M238 352 L282 356" stroke="{color}" stroke-width="8" stroke-linecap="round"/>
        <path d="M318 356 L362 352" stroke="{color}" stroke-width="8" stroke-linecap="round"/>
        <path d="M224 322 L278 334" stroke="{color}" stroke-width="5" stroke-linecap="round"/>
        <path d="M376 322 L322 334" stroke="{color}" stroke-width="5" stroke-linecap="round"/>
        <path d="M272 440 L328 440" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
        """
    # calm: open eyes, small mouth
    return f"""
    {eyes_open(260, 340, 350, 18, 24)}
    <path d="M228 322 Q254 316 278 322" stroke="{color}" stroke-width="4" opacity="0.5" fill="none"/>
    <path d="M322 322 Q346 316 372 322" stroke="{color}" stroke-width="4" opacity="0.5" fill="none"/>
    <path d="M282 438 Q300 448 318 438" stroke="{color}" stroke-width="5" fill="none" stroke-linecap="round"/>
    <path d="M292 410 Q300 414 308 410" stroke="{color}" stroke-width="3" opacity="0.4" fill="none"/>
    """


def svg_sprite(character: str, expression: str) -> str:
    c = CHARS.get(character, CHARS["rin"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 900">
<defs>
  <linearGradient id="coat" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{c['coat']}"/><stop offset="1" stop-color="#070b14"/>
  </linearGradient>
  <linearGradient id="hair" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{c['hair']}"/><stop offset="1" stop-color="{c['coat']}"/>
  </linearGradient>
  <radialGradient id="halo" cx="50%" cy="35%" r="55%">
    <stop offset="0" stop-color="{c['accent']}" stop-opacity="0.24"/><stop offset="1" stop-color="{c['accent']}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="600" height="900" fill="url(#halo)"/>
<g opacity="0.65">
  <circle cx="300" cy="355" r="224" fill="none" stroke="{c['accent']}" stroke-width="1" opacity="0.16"/>
  <circle cx="300" cy="355" r="266" fill="none" stroke="{c['accent']}" stroke-width="1" opacity="0.07"/>
  <path d="M58 724 Q300 654 542 724" stroke="{c['accent']}" stroke-width="1.2" opacity="0.18" fill="none"/>
  <path d="M88 760 Q300 700 512 760" stroke="{c['accent']}" stroke-width="1" opacity="0.1" fill="none"/>
</g>
<g opacity="0.32">
  <path d="M250 510 Q300 545 350 510 L370 650 Q300 690 230 650 Z" fill="#050912"/>
  <path d="M130 900 Q150 620 300 590 Q450 620 470 900 Z" fill="url(#coat)"/>
  <path d="M238 620 L300 706 L362 620 L332 606 L300 650 L268 606 Z" fill="#0b1220" opacity="0.9"/>
  <path d="M190 690 Q300 744 410 690" stroke="{c['accent']}" stroke-width="1.5" opacity="0.16" fill="none"/>
</g>
<path d="M205 325 Q198 176 300 158 Q402 176 395 325 L420 570 Q300 618 180 570 Z" fill="url(#hair)"/>
<ellipse cx="300" cy="358" rx="94" ry="116" fill="{c['skin']}"/>
<path d="M205 325 Q218 196 300 184 Q382 196 395 325 Q365 278 334 286 Q316 250 300 286 Q284 250 266 286 Q235 278 205 325 Z" fill="url(#hair)"/>
<path d="M211 302 Q192 432 220 552 Q238 470 228 340 Z" fill="{c['hair']}" opacity="0.72"/>
<path d="M389 302 Q408 432 380 552 Q362 470 372 340 Z" fill="{c['hair']}" opacity="0.72"/>
<path d="M250 500 Q300 530 350 500 L360 604 Q300 640 240 604 Z" fill="{c['skin']}" opacity="0.95"/>
<path d="M236 618 L300 706 L364 618" stroke="{c['accent']}" stroke-width="2" opacity="0.4" fill="none"/>
{_face(expression, c['accent'])}
<g opacity="0.28">
  <rect x="120" y="100" width="360" height="1.6" fill="{c['accent']}"/>
  <rect x="160" y="840" width="280" height="1.6" fill="{c['accent']}"/>
  <rect x="82" y="250" width="1.2" height="260" fill="{c['accent']}"/>
  <rect x="516" y="250" width="1.2" height="260" fill="{c['accent']}"/>
</g>
<g opacity="0.18" font-family="ui-monospace, monospace" font-size="8" fill="{c['accent']}">
  <text x="30" y="150">ID:{character.upper()}</text>
  <text x="430" y="790">SYNC / {expression.upper()}</text>
</g>
</svg>"""


CG_MAP = {
    "cg_letter": ("#061226", "#0e7490", "LETTER / 1999"),
    "cg_truth": ("#1a0b12", "#f59e0b", "THE TRUTH"),
    "cg_rain": ("#03050b", "#a78bfa", "RAIN / VOID"),
}


def svg_cg(key: str) -> str:
    c0, accent, label = CG_MAP.get(key, CG_MAP["cg_letter"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900">
<defs>
  <radialGradient id="g" cx="50%" cy="45%" r="65%">
    <stop offset="0" stop-color="{accent}" stop-opacity="0.28"/>
    <stop offset="0.55" stop-color="{c0}" stop-opacity="0.95"/>
    <stop offset="1" stop-color="#02040a"/>
  </radialGradient>
  <linearGradient id="f" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{accent}" stop-opacity="0.7"/><stop offset="1" stop-color="#fff" stop-opacity="0.05"/>
  </linearGradient>
</defs>
<rect width="1600" height="900" fill="url(#g)"/>
{rain_lines(130)}
<g transform="translate(800 450)">
  <ellipse cx="0" cy="30" rx="360" ry="120" fill="{accent}" opacity="0.08"/>
  <path d="M-260 120 L-110 -150 L40 -20 L190 -190 L290 140 Z" fill="#05070d" opacity="0.86"/>
  <path d="M-220 130 Q0 40 240 130" stroke="{accent}" stroke-width="2" opacity="0.25" fill="none"/>
  <circle cx="0" cy="-140" r="90" fill="{accent}" opacity="0.08"/>
  <text x="0" y="230" text-anchor="middle" fill="#dff6ff" font-family="ui-monospace, monospace" font-size="26" letter-spacing="12" opacity="0.55">{label}</text>
</g>
<rect x="80" y="80" width="1440" height="740" fill="none" stroke="{accent}" stroke-width="1" opacity="0.18"/>
<rect width="1600" height="900" fill="url(#f)" opacity="0.06"/>
</svg>"""


def main() -> None:
    BG.mkdir(parents=True, exist_ok=True)
    SPR.mkdir(parents=True, exist_ok=True)
    CG.mkdir(parents=True, exist_ok=True)
    for key in [
        "rain_classroom",
        "school_corridor",
        "old_port",
        "dorm_night",
        "rooftop_rain",
        "void",
        "library",
        "station",
    ]:
        (BG / f"{key}.svg").write_text(svg_background(key), encoding="utf-8")
    for char, expressions in {
        "rin": ["calm", "smile", "sad", "surprised"],
        "keeper": ["calm", "grim", "sad"],
        "teacher": ["calm", "sad"],
        "you": ["calm", "surprised"],
    }.items():
        for expression in expressions:
            (SPR / f"{char}_{expression}.svg").write_text(svg_sprite(char, expression), encoding="utf-8")
    for key in CG_MAP:
        (CG / f"{key}.svg").write_text(svg_cg(key), encoding="utf-8")
    print(f"generated {len(list(BG.glob('*.svg')))} backgrounds, {len(list(SPR.glob('*.svg')))} sprites, {len(list(CG.glob('*.svg')))} CGs")


if __name__ == "__main__":
    main()

