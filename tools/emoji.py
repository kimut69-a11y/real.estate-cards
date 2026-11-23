#!/usr/bin/env python3
"""이모지 문자 → Microsoft Fluent Emoji 3D 이미지(MIT 라이선스).
assets/emoji/<코드포인트>.png 에 256px로 보관하고, 없으면 GitHub(microsoft/fluentui-emoji)에서 받아온다.
emoji_html(text, size) 은 문자열 속 이모지를 <img> 태그로 바꾼다(이모지가 아닌 글자는 그대로)."""
import json, os, re, subprocess, shutil, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET = os.path.join(ROOT, "assets", "emoji")
INDEX = json.load(open(os.path.join(ROOT, "tools", "fluent_index.json")))
CLONE = os.environ.get("FLUENT_DIR", os.path.expanduser("~/fluentui-emoji"))
ZWJ, VS16 = "‍", "️"


def split_graphemes(s):
    out, i = [], 0
    while i < len(s):
        g = s[i]; i += 1
        while i < len(s) and (s[i] in (VS16, "⃣") or 0x1F3FB <= ord(s[i]) <= 0x1F3FF or s[i] == ZWJ or (g.endswith(ZWJ))):
            g += s[i]; i += 1
        out.append(g)
    return out


def is_emoji(g):
    return any(ord(c) > 0x2100 for c in g) and g.strip() != ""


def key(g):
    return "-".join(f"{ord(c):x}" for c in g if c != VS16)


def _clone():
    if not os.path.isdir(os.path.join(CLONE, ".git")):
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--sparse",
                        "https://github.com/microsoft/fluentui-emoji", CLONE], check=True)
        subprocess.run(["git", "-C", CLONE, "sparse-checkout", "set", "--no-cone", "/LICENSE"], check=True)


def ensure(glyphs):
    """필요한 이모지 PNG를 assets/emoji 에 준비. 찾지 못한 이모지 목록을 돌려준다."""
    os.makedirs(ASSET, exist_ok=True)
    need = {}
    for g in glyphs:
        p = os.path.join(ASSET, key(g) + ".png")
        if os.path.exists(p):
            continue
        folder = INDEX.get(g) or INDEX.get(g.replace(VS16, "")) or INDEX.get(g + VS16)
        if folder:
            need[g] = folder
    missing = [g for g in glyphs if not os.path.exists(os.path.join(ASSET, key(g) + ".png")) and g not in need]
    if need:
        _clone()
        pats = []
        for f in need.values():
            pats += [f"/assets/{f}/3D/*", f"/assets/{f}/Default/3D/*"]
        subprocess.run(["git", "-C", CLONE, "sparse-checkout", "add", *pats], check=True)
        from PIL import Image
        for g, f in need.items():
            cand = glob.glob(os.path.join(CLONE, "assets", f, "3D", "*.png")) + glob.glob(os.path.join(CLONE, "assets", f, "Default", "3D", "*.png"))
            if not cand:
                missing.append(g); continue
            im = Image.open(cand[0]).convert("RGBA"); im.thumbnail((256, 256))
            im.save(os.path.join(ASSET, key(g) + ".png"), optimize=True)
    return missing


def emoji_html(text, size):
    gs = split_graphemes(text)
    ensure([g for g in gs if is_emoji(g)])
    parts = []
    for g in gs:
        p = os.path.join(ASSET, key(g) + ".png")
        if is_emoji(g) and os.path.exists(p):
            parts.append(f'<img src="file://{p}" style="width:{size}px;height:{size}px;vertical-align:middle;filter:drop-shadow(0 {max(4,size//28)}px {max(6,size//18)}px rgba(0,0,0,.25))">')
        else:
            parts.append(g)
    return "".join(parts)
