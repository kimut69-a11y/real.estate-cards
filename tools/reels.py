#!/usr/bin/env python3
"""부동산 썰방 분쟁 릴스 렌더러 (9:16, 1080x1920 MP4).
사용법: python3 tools/reels.py posts/weekNN.json [게시물번호 ...]
posts JSON의 type이 "reel"(또는 type 없음)인 게시물을 reels/RNN.mp4 로 만든다.
카드뉴스와 같은 필드(hook, s_title, t_big, opts, v_head ...)를 사용한다.
장면: 훅 → 사건 → 반전 → 퀴즈(카운트다운) → 판결 → 교훈. 장면마다 2단계로 글자가 나타나고 천천히 확대된다.
인스타그램 UI에 가리지 않도록 위 250px, 아래 420px은 비워 둔다."""
import json, os, re, subprocess, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from cards import fit  # noqa: E402

BLUE, LIME, INK, WHITE = "#2E4BFF", "#E3FF5C", "#111111", "#FFFFFF"
W, H = 1080, 1920
FPS = 30

CSS = """<style>
@font-face{font-family:'Black Han Sans';src:url('file://%(r)s/fonts/BlackHanSans-Regular.ttf')}
@font-face{font-family:'Noto Sans KR';src:url('file://%(r)s/fonts/NotoSansKR[wght].ttf');font-weight:100 900}
body{margin:0}
.f{width:1080px;height:1920px;box-sizing:border-box;padding:250px 90px 420px;display:flex;flex-direction:column;justify-content:center;gap:56px;font-family:'Noto Sans KR',sans-serif;word-break:keep-all;position:relative;overflow:hidden}
.top{position:absolute;top:120px;left:90px;right:90px;display:flex;justify-content:space-between;align-items:center}
.pill{font-weight:900;font-size:34px;padding:14px 30px;border-radius:999px}
.h{font-family:'Black Han Sans',sans-serif;line-height:1.15}
.box{border-radius:40px;padding:48px 52px;font-size:50px;font-weight:700;line-height:1.55}
.hide{visibility:hidden}
.bar{position:absolute;bottom:330px;left:90px;right:90px;height:12px;border-radius:6px;background:rgba(255,255,255,.25)}
.bar i{display:block;height:100%%;border-radius:6px}
</style>""" % {"r": ROOT}


def frame(bg, color, body, step, total, pill_dark=False):
    pill_bg, pill_fg = (INK, LIME) if pill_dark else (LIME, INK)
    prog = int(100 * step / total)
    bar_fg = INK if pill_dark else LIME
    return f'''<div class="f" style="background:{bg};color:{color}">
<div class="top"><span class="pill" style="background:{pill_bg};color:{pill_fg}">부동산 썰방</span>
<span style="font-size:32px;font-weight:700">@real.estate_kr</span></div>
{body}
<div class="bar" style="background:{'rgba(0,0,0,.15)' if pill_dark else 'rgba(255,255,255,.25)'}"><i style="width:{prog}%;background:{bar_fg}"></i></div>
</div>'''


def scenes(p):
    """[(html, seconds), ...] 순서대로. 각 장면은 2단계(A: 제목만, B: 전체)."""
    out = []
    n_sc = 6

    def two(bg, color, a_body, b_body, sa, sb, idx, dark=False):
        out.append((frame(bg, color, a_body, idx - 0.5, n_sc, dark), sa))
        out.append((frame(bg, color, b_body, idx, n_sc, dark), sb))

    # 1 훅
    tag = f'<span style="align-self:flex-start;border:4px solid #fff;font-size:38px;font-weight:700;padding:12px 30px;border-radius:999px">{p["tag"]}</span>'
    hook = f'<div class="h" style="font-size:{fit(p["hook"],136,900)}px;color:{LIME}">{p["hook"]}</div>'
    sub = f'<div class="h" style="font-size:{fit(p["sub"],92,900)}px">{p["sub"]}</div>'
    two(BLUE, WHITE, tag + hook + f'<div class="h hide" style="font-size:{fit(p["sub"],92,900)}px">{p["sub"]}</div>', tag + hook + sub, 1.3, 2.0, 1)
    # 2 사건
    t = f'<div style="font-size:44px;font-weight:700;color:{LIME}">사건 개요</div><div class="h" style="font-size:{fit(p["s_title"],112,900)}px">{p["s_title"]}</div>'
    box = f'<div class="box" style="background:#fff;color:{INK}">{p["s_body"]}</div>'
    two(BLUE, WHITE, t + box.replace('class="box"', 'class="box hide"'), t + box, 1.2, 3.8, 2)
    # 3 반전
    t = f'<div style="font-size:44px;font-weight:700;color:#C8C8C8">{p["t_intro"]}</div><div class="h" style="font-size:{fit(p["t_big"],116,900)}px;color:{LIME}">{p["t_big"]}</div>'
    q = f'<div style="display:flex;flex-direction:column;gap:20px"><span style="font-size:36px;font-weight:700;color:#C8C8C8">{p["t_label"]}</span><div class="box" style="background:{BLUE};color:#fff">{p["t_quote"]}</div></div>'
    two(INK, WHITE, t + q.replace('display:flex', 'visibility:hidden;display:flex'), t + q, 1.4, 3.8, 3)
    # 4 퀴즈 + 카운트다운
    opts = "".join(f'<div style="display:flex;align-items:center;gap:34px;background:#fff;border:6px solid {INK};border-radius:36px;padding:34px 44px"><span class="h" style="font-size:90px;line-height:1;color:{BLUE}">{k}</span><span style="font-size:52px;font-weight:900;line-height:1.35">{v}</span></div>' for k, v in p["opts"])
    ask = f'<div style="font-size:56px;font-weight:900">{p["q_ask"]}</div>' if p.get("q_ask") else ""
    head = f'<div class="h" style="font-size:128px;line-height:1.1">당신의<br>판결은?</div>{ask}'
    for i, c in enumerate(["3", "2", "1"]):
        cd = f'<div style="display:flex;justify-content:space-between;align-items:center"><span style="font-size:46px;font-weight:700">댓글로 예상 남기기!</span><span class="h" style="font-size:110px;line-height:1">{c}</span></div>'
        out.append((frame(LIME, INK, head + f'<div style="display:flex;flex-direction:column;gap:26px">{opts}</div>' + cd, 3.5 + i * 0.25, n_sc, True), 1.6 if i == 0 else 1.0))
    # 5 판결
    pts = "".join(f'<div style="background:#fff;color:{INK};border-radius:32px;padding:32px 40px;font-size:44px;font-weight:700;line-height:1.45">{x}</div>' for x in p["v_points"])
    vf = f'<div style="font-size:42px;font-weight:700;color:{LIME};line-height:1.45">{p["v_foot"]}</div>' if p.get("v_foot") else ""
    top = f'''<div style="font-size:46px;font-weight:700">{p["v_title"]}</div>
<div style="display:flex;align-items:center;gap:40px"><span style="flex:none;width:210px;height:210px;border-radius:50%;background:{LIME};color:{BLUE};font-family:'Black Han Sans';font-size:150px;line-height:210px;text-align:center">{p["v_letter"]}</span>
<span class="h" style="font-size:{fit(p["v_head"],96,690)}px">{p["v_head"]}</span></div>'''
    rest = f'<div style="font-size:46px;font-weight:700;line-height:1.5">{p["v_exp"]}</div>' + (f'<div style="display:flex;flex-direction:column;gap:22px">{pts}</div>' if pts else "") + vf
    two(BLUE, WHITE, top + f'<div style="visibility:hidden;display:flex;flex-direction:column;gap:56px">{rest}</div>', top + f'<div style="display:flex;flex-direction:column;gap:40px">{rest}</div>', 1.6, 4.4, 5)
    # 6 교훈 + CTA
    line = f'<div style="font-size:52px;font-weight:900;line-height:1.45">{p["l_line"]}</div>' if p.get("l_line") else ""
    t = f'<div style="font-size:44px;font-weight:700;color:#C8C8C8">오늘의 한 줄</div><div class="h" style="font-size:{fit(p["l_big"],104,900)}px;line-height:1.2">{p["l_big"]}</div>{line}'
    cta = f'''<div style="display:flex;align-items:center;gap:26px;background:{BLUE};border-radius:36px;padding:38px 44px"><span style="font-size:48px;font-weight:900;line-height:1.4">팔로우하면 매일 판례 한 편</span></div>
<div style="font-size:30px;color:#C8C8C8;line-height:1.5">실제 판결 기반 각색 · 법률 자문 아님<br>출처: {p["src"]}</div>'''
    two(INK, WHITE, t + f'<div style="visibility:hidden">{cta}</div>', t + cta, 1.2, 3.6, 6)
    return out


def render(p, n, tmpdir, pg):
    shots = []
    for i, (html_body, sec) in enumerate(scenes(p)):
        f = os.path.join(tmpdir, f"s{i:02d}.html")
        open(f, "w").write('<!doctype html><html lang="ko"><head><meta charset="utf-8">' + CSS + '</head><body>' + html_body + '</body></html>')
        pg.goto("file://" + f)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(150)
        ov = pg.evaluate("(()=>{const r=document.querySelector('.f');return [r.scrollWidth,r.scrollHeight]})()")
        png = os.path.join(tmpdir, f"s{i:02d}.png")
        pg.screenshot(path=png, clip={"x": 0, "y": 0, "width": W, "height": H})
        shots.append((png, sec, ov))
    return shots


def encode(shots, out_path, tmpdir):
    # 장면별 천천히 확대(1.00→1.04) 클립을 만든 뒤 0.25초 크로스페이드로 잇는다.
    clips = []
    for i, (png, sec, _) in enumerate(shots):
        c = os.path.join(tmpdir, f"c{i:02d}.mp4")
        frames = int(round(sec * FPS))
        vf = (f"scale={W*2}:{H*2},zoompan=z='min(1+0.04*on/{frames},1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":d={frames}:s={W}x{H}:fps={FPS},format=yuv420p")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", png, "-vf", vf, "-frames:v", str(frames),
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", c], check=True)
        clips.append((c, sec))
    # xfade 체인
    inputs, filt, last, offset = [], [], "[0:v]", 0.0
    for c, _ in clips:
        inputs += ["-i", c]
    xf = 0.25
    for i in range(1, len(clips)):
        offset += clips[i - 1][1] - xf
        lab = f"[v{i}]"
        filt.append(f"{last}[{i}:v]xfade=transition=fade:duration={xf}:offset={offset:.3f}{lab}")
        last = lab
    total = sum(s for _, s in clips) - xf * (len(clips) - 1)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=44100:cl=stereo",
           "-filter_complex", ";".join(filt), "-map", last, "-map", f"{len(clips)}:a",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "96k", "-shortest", "-movflags", "+faststart", out_path]
    subprocess.run(cmd, check=True)
    return total


def main():
    data = json.load(open(sys.argv[1]))
    only = {int(x) for x in sys.argv[2:]}
    from playwright.sync_api import sync_playwright
    out_dir = os.path.join(ROOT, "reels"); os.makedirs(out_dir, exist_ok=True)
    problems = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = br.new_page(viewport={"width": W, "height": H})
        for p in data["posts"]:
            n = int(p["id"])
            if p.get("type", "reel") != "reel" or (only and n not in only):
                continue
            tmp = f"/tmp/reel{n:02d}"; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
            shots = render(p, n, tmp, pg)
            for png, _, ov in shots:
                if ov[0] > W or ov[1] > H:
                    problems.append(f"OVERFLOW R{n:02d} {os.path.basename(png)} {ov}")
            out = os.path.join(out_dir, f"R{n:02d}.mp4")
            sec = encode(shots, out, tmp)
            print(f"rendered {out} {sec:.1f}s {os.path.getsize(out)//1024}KB")
        br.close()
    for x in problems:
        print(x)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
