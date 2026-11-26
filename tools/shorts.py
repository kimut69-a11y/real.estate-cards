#!/usr/bin/env python3
"""부동산 썰방 '1분 썰' 쇼츠 제작기 (9:16, 1080x1920, AI 나레이션).

사용법: python3 tools/shorts.py posts/weekNN.json [id ...]
- posts JSON에서 type == "short" 인 게시물을 reels/S{id}.mp4 로 만든다.
- 먼저 tools/setup_tts.sh 로 음성 합성 도구를 설치해야 한다 (~/tts).

스타일: 빠르고 친근한 반말 나레이션 + 3~5초마다 바뀌는 장면(낙서 캐릭터·이모지·큰 글자)
+ 하단 큰 자막(핵심어 노란색) + 오른쪽 위 카운트다운 + 왼쪽 위 '부동산 썰방' 로고.

게시물 형식 (type=short):
{
  "id": 211, "type": "short", "title": "...", "slot": "...", "caption": "...", "src": "인천지법 2020가단207528",
  "voice": {"sid": 0, "speed": 1.15},           # 선택. 기본 sid 0(여성, 발음 정확도 최고), speed 1.15
  "lines": [
    {"say": "읽을 문장(숫자는 한글로)", "sub": "자막(숫자 표기 가능, | 로 자막 덩어리 나눔)",
     "hl": ["노란색 강조어"],
     "scene": {...} 또는 [{...}, {...}],   # 리스트면 자막 덩어리마다 장면이 바뀜(빠른 전환)
     "pop": [{"e": "😱", "at": 0.3, "pos": "tr"}, {"t": "헐", "at": 0.6, "pos": "tl"}]},  # 튀어나오는 스티커(선택)
    ...
  ]
}
장면(scene) 종류:
  title   {"text": "들어봐", "bg": "#111"}                      검은 화면 큰 글자
  emoji   {"emoji": "🚓🏠", "label": "경찰 신고", "bg": "#..."}   큰 이모지 + 라벨
  char    {"face": "shock", "say": "말풍선", "prop": "📦", "label": "위층 부부", "bg": "#..."}
          face: normal | happy | shock | angry | sad | smug | think
  vs      {"left": {"face":"sad","label":"위층"}, "right": {"face":"angry","label":"아래층"}, "mid": "⚡"}
  money   {"label": "합계", "amount": "2,960만 원", "emoji": "💸"}
  compare {"a": ["보통 위자료", "100~500만 원", 25], "b": ["이번 판결", "2,960만 원", 100]}
  court   {"text": "법원의 판단은?", "emoji": "⚖️"}
  end     {"text": "보복 소음은<br>더 큰 돈으로", "sub": "팔로우하면 매일 1분 판례"}
  big     {"emoji": "🤯", "text": "반전", "bg": "#FFD23F"}         화면 꽉 찬 이모지 + 한 단어
  photo   {"q": "apartment building", "label": "전주 아파트", "emoji": "🏠"}  실제 사진 전체 화면 + 라벨
          q(영어 검색어)를 넣고 먼저 python3 tools/photos.py 를 돌리면 Pexels 사진을 받아 "photo"를 채운다.
          사진은 assets/photos/<태그>*.jpg 에서 고름(같은 태그가 여러 장이면 게시물 id로 돌아가며 선택).
          그 태그 사진이 없으면 자동으로 emoji 장면(emoji·label)으로 바뀌므로 렌더링이 멈추지 않음.
          사용 가능한 태그: ls assets/photos  (저작권: 상업 이용 가능한 사진만, 출처는 assets/photos/LICENSES.md)
스티커(pop): e=이모지 또는 t=밈 문구(헐/실화냐?/ㄹㅇ?/소름/킹받네/ㅋㅋㅋ 등 짧게), at=문장 안 위치(0~1),
  pos=tl|tr|bl|br|c, dur=초(기본 0.9). 통통 튀며 나타나고 '뿅' 효과음이 붙는다.
장면이 바뀔 때마다 화면이 살짝 튀어 들어오고 '휙' 효과음, money/title/big 장면은 '쿵' 효과음.

썸네일(커버): 영상과 함께 reels/S{id}.jpg 를 만든다. 무슨 이야기인지 한눈에 알 수 있게 한글 제목을 크게 넣는다.
  기본: title 을 첫 쉼표에서 나눠 윗줄(흰 큰 글자) + 아랫줄(노란 띠 질문), 이모지는 첫 big/emoji 장면에서.
  직접 지정(선택): "cover": {"text": "소음 숨기고 판<br>아파트", "q": "계약 무를 수 있을까?", "emoji": "🏠"}
  제목 글자는 프로필 격자(3:4)에서 잘리지 않게 가운데(위·아래 240px 바깥은 비움)에만 둔다.
  썸네일만 다시 만들기: python3 tools/shorts.py --cover posts/daily/<날짜>.json [id]
"""
import json, os, re, subprocess, sys, shutil, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emoji import emoji_html  # noqa: E402  Microsoft Fluent Emoji 3D (MIT)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTS = os.environ.get("TTS_DIR", os.path.expanduser("~/tts"))
BIN = f"{TTS}/sherpa-onnx-v1.13.8-linux-x64-shared"
ST = f"{TTS}/sherpa-onnx-supertonic-3-tts-int8-2026-05-11"
ASR = f"{TTS}/sherpa-onnx-zipformer-korean-2024-06-24"
W, H, FPS = 1080, 1920, 30
BLUE, LIME, INK, YEL = "#2E4BFF", "#E3FF5C", "#111111", "#FFE14D"
GAP = 0.07  # 문장 사이 쉼(초)
TEMPO = 1.16  # 1.15배속 합성 후 재생 속도(음높이 유지) — 발음 정확도와 속도의 최적 조합

CSS = """<style>
@font-face{font-family:'BHS';src:url('file://%(r)s/fonts/BlackHanSans-Regular.ttf')}
@font-face{font-family:'NSK';src:url('file://%(r)s/fonts/NotoSansKR[wght].ttf');font-weight:100 900}
@font-face{font-family:'EMJ';src:url('file://%(r)s/fonts/NotoColorEmoji.ttf')}
html,body{margin:0;background:transparent}
*{box-sizing:border-box}
.cv{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:'NSK','EMJ',sans-serif;word-break:keep-all}
.stage{position:absolute;left:0;right:0;top:300px;height:1020px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:40px;text-align:center}
.em{font-family:'EMJ';line-height:1}
.h{font-family:'BHS','EMJ';line-height:1.15}
.pill{display:inline-block;background:#fff;color:#111;border:6px solid #111;border-radius:999px;padding:14px 40px;font-weight:900;font-size:54px}
.bub{position:relative;background:#fff;border:6px solid #111;border-radius:48px;padding:26px 44px;font-weight:900;font-size:58px;color:#111;max-width:900px}
.bub:after{content:'';position:absolute;left:50%%;bottom:-38px;margin-left:-20px;border:20px solid transparent;border-top:20px solid #111}
.sub{position:absolute;left:60px;right:60px;top:1360px;text-align:center;font-family:'NSK','EMJ';font-weight:900;font-size:66px;line-height:1.32;color:#fff;
  -webkit-text-stroke:14px #000;paint-order:stroke fill;letter-spacing:-1px}
.sub b{color:%(y)s}
</style>""" % {"r": ROOT, "y": YEL}


# ---------- 낙서 캐릭터 (오리지널 디자인: 흰 몸통 + 검은 외곽선) ----------
def doodle(face="normal", size=520):
    eyes = {
        "normal": '<circle cx="80" cy="95" r="9"/><circle cx="140" cy="95" r="9"/>',
        "happy": '<path d="M68 98 q12 -16 24 0" fill="none" stroke="#111" stroke-width="7" stroke-linecap="round"/><path d="M128 98 q12 -16 24 0" fill="none" stroke="#111" stroke-width="7" stroke-linecap="round"/>',
        "shock": '<circle cx="80" cy="92" r="16" fill="#fff" stroke="#111" stroke-width="6"/><circle cx="80" cy="92" r="5"/><circle cx="140" cy="92" r="16" fill="#fff" stroke="#111" stroke-width="6"/><circle cx="140" cy="92" r="5"/>',
        "angry": '<circle cx="82" cy="100" r="9"/><circle cx="138" cy="100" r="9"/><path d="M62 74 L98 88 M158 74 L122 88" stroke="#111" stroke-width="8" stroke-linecap="round"/>',
        "sad": '<circle cx="80" cy="98" r="9"/><circle cx="140" cy="98" r="9"/><path d="M62 82 L96 74 M158 82 L124 74" stroke="#111" stroke-width="7" stroke-linecap="round"/><path d="M78 110 q-6 18 0 26 q6 -8 0 -26z" fill="#5AB4FF"/>',
        "smug": '<path d="M66 96 h28 M126 96 h28" stroke="#111" stroke-width="8" stroke-linecap="round"/><path d="M64 80 L96 86 M156 80 L124 86" stroke="#111" stroke-width="6" stroke-linecap="round"/>',
        "think": '<circle cx="84" cy="92" r="9"/><circle cx="144" cy="92" r="9"/><path d="M66 74 L98 80" stroke="#111" stroke-width="6" stroke-linecap="round"/>',
    }[face]
    mouth = {
        "normal": '<path d="M92 132 q18 12 36 0" fill="none" stroke="#111" stroke-width="7" stroke-linecap="round"/>',
        "happy": '<path d="M86 124 q24 34 48 0 z" fill="#111"/>',
        "shock": '<ellipse cx="110" cy="140" rx="16" ry="22" fill="#111"/>',
        "angry": '<path d="M88 144 q22 -18 44 0" fill="none" stroke="#111" stroke-width="8" stroke-linecap="round"/>',
        "sad": '<path d="M90 146 q20 -16 40 0" fill="none" stroke="#111" stroke-width="7" stroke-linecap="round"/>',
        "smug": '<path d="M90 134 q26 10 44 -8" fill="none" stroke="#111" stroke-width="7" stroke-linecap="round"/>',
        "think": '<path d="M96 138 h28" stroke="#111" stroke-width="7" stroke-linecap="round"/>',
    }[face]
    extra = ""
    if face == "shock":
        extra = '<path d="M186 40 q10 18 0 30 q-10 -12 0 -30z" fill="#5AB4FF" stroke="#111" stroke-width="3"/>'
    if face == "angry":
        extra = '<path d="M176 30 l14 -14 M182 44 l20 -4 M170 22 l2 -18" stroke="#E33" stroke-width="7" stroke-linecap="round"/>'
    if face == "think":
        extra = '<text x="178" y="52" font-size="56" font-family="BHS" fill="#111">?</text>'
    arms = {"happy": '<path d="M42 210 L8 150 M178 210 L212 150" />', "shock": '<path d="M42 210 L4 168 M178 210 L216 168" />',
            "angry": '<path d="M42 215 L20 260 M178 215 L200 260" />', "sad": '<path d="M44 215 L30 275 M176 215 L190 275" />'}.get(face, '<path d="M42 215 L14 262 M178 215 L206 262" />')
    return f'''<svg width="{size}" height="{int(size*1.3)}" viewBox="-10 -10 240 300" xmlns="http://www.w3.org/2000/svg">
<g stroke="#111" stroke-width="7" stroke-linecap="round" fill="none">{arms}<path d="M84 276 L80 290 M136 276 L140 290"/></g>
<path d="M110 10 C40 10 26 60 30 120 C34 170 30 230 44 262 C60 286 160 286 176 262 C190 230 186 170 190 120 C194 60 180 10 110 10 Z" fill="#fff" stroke="#111" stroke-width="7"/>
<g fill="#111">{eyes}</g>{mouth}{extra}
</svg>'''


def esc(s):
    return s  # 작성자가 넣는 HTML(<br>, <b>) 허용


PHOTOS = os.path.join(ROOT, "assets", "photos")


def find_photo(tag, seed=0):
    import glob
    for e in (".jpg", ".jpeg", ".png"):
        if os.path.exists(os.path.join(PHOTOS, tag + e)):
            return os.path.join(PHOTOS, tag + e)
    fs = sorted(glob.glob(os.path.join(PHOTOS, f"{tag}*.jpg")) + glob.glob(os.path.join(PHOTOS, f"{tag}*.jpeg")) + glob.glob(os.path.join(PHOTOS, f"{tag}*.png")))
    return fs[seed % len(fs)] if fs else None


def scene_html(sc, seed=0):
    t = sc.get("type", "emoji")
    if t == "photo":
        f = find_photo(sc.get("photo", ""), seed)
        if not f:
            sc = {"type": "emoji", "emoji": sc.get("emoji", "🏠"), "label": sc.get("label"), "bg": sc.get("bg")}
            t = "emoji"
        else:
            lab = f'<div class="pill" style="font-size:60px">{esc(sc["label"])}</div>' if sc.get("label") else ""
            em = f'<div style="position:absolute;right:70px;top:330px">{emoji_html(sc["emoji"], 170)}</div>' if sc.get("emoji") else ""
            pos = sc.get("pos", "center")
            return (f'<div class="cv" style="background:#000">'
                    f'<div style="position:absolute;inset:0;background:url(\'file://{f}\') {pos}/cover no-repeat"></div>'
                    f'<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 22%,rgba(0,0,0,0) 55%,rgba(0,0,0,.75) 100%)"></div>'
                    f'{em}<div style="position:absolute;left:0;right:0;top:1150px;text-align:center">{lab}</div></div>')
    bg = sc.get("bg") or {"title": "#111", "money": "#14213D", "court": "#2B2D42", "end": INK, "compare": "#1D3557", "big": "#FFD23F"}.get(t, "#F4E9D8")
    dark = bg.lower() in ("#111", "#111111", "#14213d", "#2b2d42", "#1d3557", "#000", "#222") or sc.get("dark")
    fg = "#fff" if dark else "#111"
    if t == "title":
        body = f'<div class="h" style="font-size:{sc.get("size",190)}px;color:{sc.get("color","#fff")}">{esc(sc["text"])}</div>'
    elif t == "emoji":
        lab = f'<div class="pill">{esc(sc["label"])}</div>' if sc.get("label") else ""
        body = f'<div style="display:flex;gap:30px;justify-content:center">{emoji_html(sc["emoji"], sc.get("size",300))}</div>{lab}'
    elif t == "char":
        bub = f'<div class="bub">{esc(sc["say"])}</div>' if sc.get("say") else ""
        prop = f'<div style="position:absolute;right:110px;bottom:110px">{emoji_html(sc["prop"], 220)}</div>' if sc.get("prop") else ""
        lab = f'<div class="pill">{esc(sc["label"])}</div>' if sc.get("label") else ""
        body = f'{bub}<div>{doodle(sc.get("face","normal"), sc.get("size",460))}</div>{lab}{prop}'
    elif t == "vs":
        L, R = sc["left"], sc["right"]
        body = f'''<div style="display:flex;align-items:flex-end;justify-content:center;gap:10px">
<div style="display:flex;flex-direction:column;align-items:center;gap:20px">{doodle(L.get("face","normal"),360)}<div class="pill">{esc(L["label"])}</div></div>
<div style="margin-bottom:220px">{emoji_html(sc.get("mid","⚡"), 160)}</div>
<div style="display:flex;flex-direction:column;align-items:center;gap:20px">{doodle(R.get("face","angry"),360)}<div class="pill">{esc(R["label"])}</div></div></div>'''
    elif t == "money":
        body = f'''<div style="font-size:64px;font-weight:900;color:#fff">{esc(sc.get("label",""))}</div>
<div class="h" style="font-size:{sc.get("size",170)}px;color:{YEL}">{esc(sc["amount"])}</div>
<div>{emoji_html(sc.get("emoji","💸"), 230)}</div>'''
    elif t == "compare":
        def bar(x, c):
            return f'''<div style="display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:700px;gap:18px">
<div class="h" style="font-size:66px;color:{c}">{esc(x[1])}</div>
<div style="width:250px;height:{int(5.2*x[2])}px;background:{c};border:6px solid #000;border-radius:24px 24px 0 0"></div>
<div style="font-size:52px;font-weight:900;color:#fff">{esc(x[0])}</div></div>'''
        body = f'<div style="display:flex;gap:120px;align-items:flex-end">{bar(sc["a"],"#9AA5B1")}{bar(sc["b"],YEL)}</div>'
    elif t == "court":
        body = f'''<div>{emoji_html(sc.get("emoji","⚖️"), 360)}</div>
<div class="h" style="font-size:{sc.get("size",120)}px;color:#fff">{esc(sc["text"])}</div>'''
    elif t == "end":
        body = f'''<div class="h" style="font-size:{sc.get("size",130)}px;color:#fff">{esc(sc["text"])}</div>
<div style="background:{BLUE};color:#fff;border-radius:40px;padding:34px 50px;font-size:58px;font-weight:900">{esc(sc.get("sub","팔로우하면 매일 1분 판례"))}</div>'''
    elif t == "big":
        txt = f'<div class="h" style="font-size:{sc.get("size",150)}px;color:{sc.get("color","#111")};-webkit-text-stroke:0">{esc(sc["text"])}</div>' if sc.get("text") else ""
        body = f'<div style="display:flex;gap:20px;justify-content:center">{emoji_html(sc["emoji"], sc.get("esize",520))}</div>{txt}'
    else:
        raise ValueError(t)
    return f'<div class="cv" style="background:{bg};color:{fg}"><div class="stage">{body}</div></div>'


def overlay_html():
    return f'''<div class="cv" style="background:transparent">
<div style="position:absolute;left:60px;top:150px;background:{LIME};color:{INK};font-weight:900;font-size:46px;padding:14px 32px;border-radius:999px;border:5px solid {INK}">부동산 썰방</div>
</div>'''


def cover_parts(p):
    c = p.get("cover") or {}
    title = p.get("title", "")
    if "," in title:
        a, b = title.split(",", 1)
    else:
        a, b = title, ""
    text, q = c.get("text", a.strip()), c.get("q", b.strip())
    emo = c.get("emoji")
    if not emo:
        for ln in p.get("lines", []):
            for sc in (ln["scene"] if isinstance(ln["scene"], list) else [ln["scene"]]):
                if sc.get("type") in ("big", "emoji") and sc.get("emoji"):
                    emo = sc["emoji"]; break
            if emo:
                break
    return text, q, emo or "🏠"


def cover_html(p):
    text, q, emo = cover_parts(p)
    qd = (f'<div id="q" class="h" style="background:{YEL};color:{INK};border:8px solid {INK};border-radius:28px;padding:18px 40px;'
          f'font-size:110px;box-shadow:14px 14px 0 {INK};transform:rotate(-2deg);white-space:nowrap">{q}</div>') if q else ""
    return f'''<div class="cv" style="background:{BLUE}">
<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 42%,rgba(255,255,255,.18),transparent 60%)"></div>
<div style="position:absolute;left:0;right:0;top:250px;display:flex;justify-content:center;gap:24px">
 <div style="background:{LIME};color:{INK};font-weight:900;font-size:52px;padding:14px 36px;border-radius:999px;border:6px solid {INK}">부동산 썰방</div>
 <div style="background:#fff;color:{INK};font-weight:900;font-size:52px;padding:14px 36px;border-radius:999px;border:6px solid {INK}">1분 판례</div></div>
<div id="box" style="position:absolute;left:60px;right:60px;top:400px;height:1240px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:56px;text-align:center">
 <div>{emoji_html(emo, 300)}</div>
 <div id="t" class="h" style="font-size:190px;color:#fff;-webkit-text-stroke:16px {INK};paint-order:stroke fill;line-height:1.12">{text}</div>
 {qd}
</div></div>'''


def make_cover(p, pg):
    n = int(p["id"])
    tmp = f"/tmp/cover{n}"; os.makedirs(tmp, exist_ok=True)
    f = f"{tmp}/cover.html"
    open(f, "w").write('<!doctype html><html lang="ko"><head><meta charset="utf-8">' + CSS + '</head><body>' + cover_html(p) + '</body></html>')
    pg.goto("file://" + f); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(200)
    pg.evaluate("()=>{const b=document.getElementById('box'),t=document.getElementById('t'),q=document.getElementById('q');"
                "let s=parseInt(getComputedStyle(t).fontSize);while(s>90&&(t.scrollWidth>b.clientWidth||b.scrollHeight>b.clientHeight)){s-=6;t.style.fontSize=s+'px'}"
                "let k=q?parseInt(getComputedStyle(q).fontSize):0;while(q&&k>60&&(q.getBoundingClientRect().width>b.clientWidth||b.scrollHeight>b.clientHeight)){k-=4;q.style.fontSize=k+'px'}}")
    over = pg.evaluate("(()=>{const b=document.getElementById('box');return b.scrollHeight-b.clientHeight})()")
    png = f"{tmp}/cover.png"
    pg.screenshot(path=png, clip={"x": 0, "y": 0, "width": W, "height": H})
    out = os.path.join(ROOT, "reels", f"S{n}.jpg")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", png, "-q:v", "2", out])
    print(f"cover {out} {os.path.getsize(out)//1024}KB")
    return [f"COVER OVERFLOW S{n}"] if over > 4 else []


def sticker_html(pp):
    if pp.get("e"):
        inner = f'<div>{emoji_html(pp["e"], pp.get("size",260))}</div>'
    else:
        col = pp.get("color", "#FF3B3B")
        inner = (f'<div style="font-family:BHS;font-size:{pp.get("size",120)}px;color:#fff;background:{col};border:8px solid #111;'
                 f'border-radius:28px;padding:10px 36px;transform:rotate({pp.get("rot",-8)}deg);box-shadow:10px 10px 0 #111;white-space:nowrap">{pp["t"]}</div>')
    return ('<div style="width:600px;height:400px;display:flex;align-items:center;justify-content:center;background:transparent">' + inner + '</div>')


def sub_html(text, hl):
    t = text
    for w in sorted(hl or [], key=len, reverse=True):
        t = t.replace(w, f"\u0001{w}\u0002")
    t = t.replace("\u0001", "<b>").replace("\u0002", "</b>")
    return f'<div class="cv" style="background:transparent"><div class="sub">{t}</div></div>'


def _sfx_bank(sr=44100):
    import numpy as np
    rng = np.random.default_rng(7)
    def env(n, a, r):
        e = np.ones(n); a = max(1, int(a * n)); e[:a] = np.linspace(0, 1, a); e[a:] = np.exp(-np.linspace(0, r, n - a)); return e
    n = int(0.28 * sr); noise = rng.standard_normal(n)
    k = 40; sm = np.convolve(noise, np.ones(k) / k, mode="same")          # 부드러운 '휙'
    whoosh = (noise - sm) * 0.35 + sm * 1.2
    whoosh *= np.sin(np.linspace(0, np.pi, n)) ** 2
    n = int(0.11 * sr); tt = np.arange(n) / sr
    f = 520 + 1400 * tt / tt[-1]
    pop = np.sin(2 * np.pi * np.cumsum(f) / sr) * env(n, 0.05, 6)          # '뿅'
    n = int(0.45 * sr); tt = np.arange(n) / sr
    boom = (np.sin(2 * np.pi * (70 - 30 * tt / tt[-1]) * tt) + 0.3 * rng.standard_normal(n) * np.exp(-tt * 40)) * env(n, 0.01, 7)  # '쿵'
    norm_ = lambda x, g: g * x / (np.abs(x).max() + 1e-9)
    return {"whoosh": norm_(whoosh, 0.16), "pop": norm_(pop, 0.22), "boom": norm_(boom, 0.38)}


def mix_sfx(voice_wav, events, out):
    import numpy as np, wave
    w = wave.open(voice_wav); sr = w.getframerate(); ch = w.getnchannels()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32).reshape(-1, ch) / 32768.0
    bank = _sfx_bank(sr)
    for kind, t in events:
        s0 = int(t * sr); snd = bank[kind]; e = min(len(x), s0 + len(snd))
        if s0 < len(x):
            x[s0:e] += snd[: e - s0, None]
    x = np.clip(x, -1, 1)
    o = wave.open(out, "wb"); o.setnchannels(ch); o.setsampwidth(2); o.setframerate(sr)
    o.writeframes((x * 32767).astype(np.int16).tobytes()); o.close()


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def tts(text, out, sid, speed):
    env = dict(os.environ, LD_LIBRARY_PATH=f"{BIN}/lib")
    sh([f"{BIN}/bin/sherpa-onnx-offline-tts",
        f"--supertonic-duration-predictor={ST}/duration_predictor.int8.onnx", f"--supertonic-text-encoder={ST}/text_encoder.int8.onnx",
        f"--supertonic-vector-estimator={ST}/vector_estimator.int8.onnx", f"--supertonic-vocoder={ST}/vocoder.int8.onnx",
        f"--supertonic-tts-json={ST}/tts.json", f"--supertonic-unicode-indexer={ST}/unicode_indexer.bin",
        f"--supertonic-voice-style={ST}/voice.bin", "--lang=ko", f"--sid={sid}", f"--speed={speed}", "--num-steps=8",
        f"--output-filename={out}", text], env=env)


def dur(f):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).stdout.strip())


def asr(wavs):
    env = dict(os.environ, LD_LIBRARY_PATH=f"{BIN}/lib")
    r = subprocess.run([f"{BIN}/bin/sherpa-onnx-offline", f"--tokens={ASR}/tokens.txt", f"--encoder={ASR}/encoder-epoch-99-avg-1.int8.onnx",
                        f"--decoder={ASR}/decoder-epoch-99-avg-1.int8.onnx", f"--joiner={ASR}/joiner-epoch-99-avg-1.int8.onnx", *wavs],
                       capture_output=True, text=True, env=env)
    return re.findall(r'"text": "([^"]*)"', r.stdout + r.stderr)


def norm(s):
    return re.sub(r"[^가-힣0-9]", "", s)


def similarity(a, b):
    import difflib
    # 숫자는 음성 인식이 아라비아 숫자로 적으므로 숫자·수사(일이삼…만억)는 빼고 비교
    strip = lambda s: re.sub(r"[0-9일이삼사오육칠팔구십백천만억]", "", norm(s))
    return difflib.SequenceMatcher(None, strip(a), strip(b)).ratio()


def build(p, pg):
    n = int(p["id"])
    v = p.get("voice", {})
    sid, speed, tempo = v.get("sid", 0), v.get("speed", 1.15), v.get("tempo", TEMPO)
    tmp = f"/tmp/short{n}"; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)

    def shot(html_body, path):
        f = path + ".html"
        open(f, "w").write('<!doctype html><html lang="ko"><head><meta charset="utf-8">' + CSS + '</head><body>' + html_body + '</body></html>')
        pg.goto("file://" + f); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(120)
        pg.screenshot(path=path, clip={"x": 0, "y": 0, "width": W, "height": H}, omit_background=True)
        return pg.evaluate("(()=>{const s=document.querySelector('.stage')||document.querySelector('.sub');if(!s)return 0;return s.scrollHeight-s.clientHeight})()")

    problems, clips, wavs, raw, sfx = [], [], [], [], []
    t_line = 0.0
    shot(overlay_html(), f"{tmp}/overlay.png")
    for i, ln in enumerate(p["lines"]):
        w0 = f"{tmp}/l{i:02d}.wav"; tts(ln["say"], w0, sid, speed); raw.append(w0)
        w = f"{tmp}/p{i:02d}.wav"
        trim = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
        sh(["ffmpeg", "-y", "-loglevel", "error", "-i", w0, "-af", f"{trim},atempo={tempo},apad=pad_dur={GAP}", "-ar", "44100", "-ac", "2", w])
        d = dur(w); wavs.append(w)
        chunks = [c.strip() for c in ln.get("sub", ln["say"]).split("|") if c.strip()]
        scenes = ln["scene"] if isinstance(ln["scene"], list) else [ln["scene"]]
        tot = sum(len(norm(c)) or 1 for c in chunks)
        # 자막 덩어리 시간 배분
        bounds, t0 = [], 0.0
        for j, c in enumerate(chunks):
            t1 = d if j == len(chunks) - 1 else t0 + d * (len(norm(c)) or 1) / tot
            bounds.append((t0, t1)); t0 = t1
        # 장면 구간: 장면 수 = 덩어리 수(리스트) 또는 1개
        if len(scenes) == len(chunks):
            segs = [(scenes[j], bounds[j][0], bounds[j][1], [j]) for j in range(len(chunks))]
        elif len(scenes) == 1:
            segs = [(scenes[0], 0.0, d, list(range(len(chunks))))]
        else:  # 장면 수가 다르면 시간을 균등 분할
            segs = [(scenes[k], d * k / len(scenes), d * (k + 1) / len(scenes), [j for j in range(len(chunks)) if bounds[j][0] < d * (k + 1) / len(scenes) and bounds[j][1] > d * k / len(scenes)]) for k in range(len(scenes))]
        subpng = []
        for j, c in enumerate(chunks):
            sp = f"{tmp}/t{i:02d}_{j}.png"
            if shot(sub_html(c, ln.get("hl")), sp) > 4:
                problems.append(f"SUB OVERFLOW S{n} line {i}")
            subpng.append(sp)
        pops = []
        for q, pp in enumerate(ln.get("pop", [])):
            pp_png = f"{tmp}/k{i:02d}_{q}.png"
            f = pp_png + ".html"
            open(f, "w").write('<!doctype html><html lang="ko"><head><meta charset="utf-8">' + CSS + '</head><body style="margin:0">' + sticker_html(pp) + '</body></html>')
            pg.goto("file://" + f); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(80)
            pg.screenshot(path=pp_png, clip={"x": 0, "y": 0, "width": 600, "height": 400}, omit_background=True)
            pops.append((pp_png, float(pp.get("at", 0.5)) * d, float(pp.get("dur", 0.9)), pp.get("pos", "tr")))
            sfx.append(("pop", t_line + float(pp.get("at", 0.5)) * d))
        for k, (sc, a0, a1, js) in enumerate(segs):
            seg_d = max(a1 - a0, 1.0 / FPS)
            img = f"{tmp}/s{i:02d}_{k}.png"
            if shot(scene_html(sc, n + i + k), img) > 4:
                problems.append(f"SCENE OVERFLOW S{n} line {i}")
            frames = max(1, int(round(seg_d * FPS)))
            zdir = "1.0+0.04*(on-5)/%d" % frames if (i + k) % 2 == 0 else "1.04-0.04*(on-5)/%d" % frames
            z = f"if(lt(on,5),1.14-0.028*on,{zdir})"
            inputs = ["-loop", "1", "-i", img]
            filt = [f"[0:v]scale={W*2}:{H*2},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}[b0]"]
            last, idx = "b0", 1
            for j in js:
                ta, tb = max(bounds[j][0], a0) - a0, min(bounds[j][1], a1) - a0
                inputs += ["-i", subpng[j]]
                filt.append(f"[{last}][{idx}:v]overlay=0:0:enable='between(t,{ta:.3f},{tb:.3f})'[b{idx}]"); last = f"b{idx}"; idx += 1
            posxy = {"tr": (800, 470), "tl": (280, 470), "br": (800, 1150), "bl": (280, 1150), "c": (540, 800)}
            for (pp_png, at, pd, pos) in pops:
                if not (a0 <= at < a1):
                    continue
                la = at - a0; X, Y = posxy.get(pos, posxy["tr"])
                inputs += ["-loop", "1", "-t", f"{pd:.2f}", "-i", pp_png]
                filt.append(f"[{idx}:v]format=rgba,scale=w='trunc(iw*min(1\\,0.25+7*t)*(1+0.07*sin(22*t))/2)*2':h=-2:eval=frame,setpts=PTS+{la:.3f}/TB[p{idx}]")
                filt.append(f"[{last}][p{idx}]overlay=x='{X}-overlay_w/2':y='{Y}-overlay_h/2':eval=frame:eof_action=pass:enable='between(t,{la:.3f},{la+pd:.3f})'[b{idx}]")
                last = f"b{idx}"; idx += 1
            c = f"{tmp}/c{i:02d}_{k}.mp4"
            sh(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt), "-map", f"[{last}]",
                "-frames:v", str(frames), "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", c])
            clips.append(c)
            kind = sc.get("type")
            sfx.append(("boom" if kind in ("money", "title", "big") else "whoosh", t_line + a0))
        t_line += d
    # 이어 붙이기
    open(f"{tmp}/v.txt", "w").write("".join(f"file '{c}'\n" for c in clips))
    open(f"{tmp}/a.txt", "w").write("".join(f"file '{w}'\n" for w in wavs))
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/v.txt", "-c", "copy", f"{tmp}/v.mp4"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/a.txt", "-c:a", "pcm_s16le", f"{tmp}/a.wav"])
    mix_sfx(f"{tmp}/a.wav", sfx, f"{tmp}/am.wav")
    total = dur(f"{tmp}/am.wav")
    font = f"{ROOT}/fonts/BlackHanSans-Regular.ttf"
    timer = (f"drawtext=fontfile={font}:text='%{{eif\\:max(0\\,ceil({total:.2f}-t))\\:d}}':x=w-tw-70:y=135:fontsize=110:"
             f"fontcolor=white:borderw=10:bordercolor=black")
    out = os.path.join(ROOT, "reels", f"S{n}.mp4"); os.makedirs(os.path.dirname(out), exist_ok=True)
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{tmp}/v.mp4", "-i", f"{tmp}/overlay.png", "-i", f"{tmp}/am.wav",
        "-filter_complex", f"[0:v][1:v]overlay=0:0,{timer}[v]", "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out])
    # 발음 검수: 음성 인식 결과와 원문 비교
    r16 = []
    for w0 in raw:
        o = w0.replace(".wav", "_16k.wav"); sh(["ffmpeg", "-y", "-loglevel", "error", "-i", w0, "-ar", "16000", "-ac", "1", o]); r16.append(o)
    heard = asr(r16)
    for i, (ln, hrd) in enumerate(zip(p["lines"], heard)):
        s = similarity(ln["say"], hrd)
        if s < 0.8:
            problems.append(f"PRONUNCIATION S{n} line {i} ({s:.2f}): '{ln['say']}' -> '{hrd}'")
    print(f"rendered {out} {total:.1f}s {os.path.getsize(out)//1024}KB")
    problems += make_cover(p, pg)
    if total > 90:
        problems.append(f"TOO LONG S{n} {total:.1f}s (권장 45~60초)")
    return problems


def main():
    args = sys.argv[1:]
    cover_only = bool(args) and args[0] == "--cover"
    if cover_only:
        args = args[1:]
    elif not os.path.exists(f"{ST}/voice.bin"):
        sys.exit("음성 도구가 없습니다. 먼저 bash tools/setup_tts.sh 실행")
    data = json.load(open(args[0]))
    only = {int(x) for x in args[1:]}
    from playwright.sync_api import sync_playwright
    problems = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = br.new_page(viewport={"width": W, "height": H})
        for p in data["posts"]:
            if p.get("type") != "short" or (only and int(p["id"]) not in only):
                continue
            problems += make_cover(p, pg) if cover_only else build(p, pg)
        br.close()
    for x in problems:
        print(x)
    sys.exit(1 if any(not x.startswith("PRONUNCIATION") for x in problems) else 0)


if __name__ == "__main__":
    main()
