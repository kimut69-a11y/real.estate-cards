#!/usr/bin/env python3
"""부동산 썰방 카드 렌더러.
사용법: python3 tools/cards.py posts/weekNN.json [게시물번호 ...]
posts JSON의 각 게시물을 cards/PNN-1.jpg ~ PNN-6.jpg (1080x1350 JPEG)로 렌더링한다.
필드 설명은 PLAYBOOK.md 참고."""
import json, sys, os, re, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLUE, LIME, INK = "#2E4BFF", "#E3FF5C", "#111111"
import re as _re
def vis_len(line):
    t = _re.sub(r"<[^>]+>", "", line)
    w = 0
    for ch in t:
        if ch == " ": w += 0.33
        elif ch.isascii(): w += 0.58
        elif ch in "“”‘’·,…": w += 0.5
        else: w += 1.0
    return w
def fit(text, base, width):
    lines = text.split("<br>")
    m = max(vis_len(l) for l in lines)
    return int(min(base, width / (m * 0.97)))

def page(title, bg, color, body, num, foot_right, pill_dark=False):
    pill = (f'<span style="background: {INK}; color: {LIME}; font-weight: 900; font-size: 30px; padding: 12px 26px; border-radius: 999px">부동산 썰방</span>'
            if pill_dark else
            f'<span style="background: {LIME}; color: {INK}; font-weight: 900; font-size: 30px; padding: 12px 26px; border-radius: 999px">부동산 썰방</span>')
    handle_op = "" if pill_dark else "; opacity: 0.85"
    footer = foot_right if foot_right is not None else ""
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&amp;family=Noto+Sans+KR:wght@400;700;900&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
</style>
</helmet>
<div style="width: 1080px; height: 1350px; background: {bg}; box-sizing: border-box; padding: 88px 96px; display: flex; flex-direction: column; justify-content: space-between; font-family: 'Noto Sans KR', sans-serif; word-break: keep-all; color: {color}">
<div style="display: flex; justify-content: space-between; align-items: center">
{pill}
<span style="font-size: 30px; font-weight: 700">{num} / 6</span>
</div>
{body}
{footer}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1080,"height":1350}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''

def foot(right, dark=False):
    op = "" if dark else "; opacity: 0.85"
    return f'''<div style="display: flex; justify-content: space-between; align-items: center; font-size: 32px; font-weight: 700">
<span style="{op.strip('; ')}">@real.estate_kr</span>
<span>{right}</span>
</div>'''

def cards(n, p):
    out = {}
    out[1] = page(f"게시물 {n} 카드 1 훅", BLUE, "#FFFFFF", f'''<div style="display: flex; flex-direction: column; gap: 40px">
<span style="align-self: flex-start; border: 3px solid #FFFFFF; font-size: 32px; font-weight: 700; padding: 10px 24px; border-radius: 999px">{p["tag"]}</span>
<div style="font-family: 'Black Han Sans', sans-serif; font-size: {fit(p["hook"],116,888)}px; line-height: 1.12; color: {LIME}">{p["hook"]}</div>
<div style="font-family: 'Black Han Sans', sans-serif; font-size: {fit(p["sub"],76,888)}px; line-height: 1.2">{p["sub"]}</div>
</div>''', 1, foot("넘겨서 판결 확인 →"))
    out[2] = page(f"게시물 {n} 카드 2 사건", BLUE, "#FFFFFF", f'''<div style="display: flex; flex-direction: column; gap: 52px">
<div style="font-size: 40px; font-weight: 700; color: {LIME}">사건 개요</div>
<div style="font-family: 'Black Han Sans', sans-serif; font-size: {fit(p["s_title"],96,888)}px; line-height: 1.15">{p["s_title"]}</div>
<div style="background: #FFFFFF; color: {INK}; font-size: 46px; font-weight: 700; line-height: 1.55; padding: 44px 48px; border-radius: 36px">{p["s_body"]}</div>
</div>''', 2, foot("→"))
    out[3] = page(f"게시물 {n} 카드 3 쟁점", INK, "#FFFFFF", f'''<div style="display: flex; flex-direction: column; gap: 48px">
<div style="font-size: 40px; font-weight: 700; color: #C8C8C8">{p["t_intro"]}</div>
<div style="font-family: 'Black Han Sans', sans-serif; font-size: {fit(p["t_big"],100,888)}px; line-height: 1.15; color: {LIME}">{p["t_big"]}</div>
<div style="display: flex; flex-direction: column; gap: 18px">
<span style="font-size: 32px; font-weight: 700; color: #C8C8C8">{p["t_label"]}</span>
<div style="background: {BLUE}; font-size: 42px; font-weight: 700; line-height: 1.55; padding: 40px 44px; border-radius: 36px">{p["t_quote"]}</div>
</div>
</div>''', 3, foot("→"))
    ask = f'\n<div style="font-size: 48px; font-weight: 900">{p["q_ask"]}</div>' if p["q_ask"] else ""
    big = 104 if len(p["opts"]) == 3 else 120
    opt_html = "\n".join(f'''<div style="display: flex; align-items: center; gap: 32px; background: #FFFFFF; border: 5px solid {INK}; border-radius: 32px; padding: {28 if len(p["opts"])==3 else 34}px 40px">
<span style="font-family: 'Black Han Sans', sans-serif; font-size: 80px; line-height: 1; color: {BLUE}">{k}</span>
<span style="font-size: 46px; font-weight: 900; line-height: 1.35">{v}</span>
</div>''' for k, v in p["opts"])
    q_title = p["q_title"].replace(" ", "<br>", 1)
    out[4] = page(f"게시물 {n} 카드 4 퀴즈", LIME, INK, f'''<div style="display: flex; flex-direction: column; gap: 40px">
<div style="font-family: 'Black Han Sans', sans-serif; font-size: {big}px; line-height: 1.1">{q_title}</div>{ask}
<div style="display: flex; flex-direction: column; gap: 22px">
{opt_html}
</div>
<div style="font-size: 40px; font-weight: 700">댓글로 정답 남기고 넘기기!</div>
</div>''', 4, f'''<div style="display: flex; justify-content: space-between; align-items: center; font-size: 32px; font-weight: 700">
<span>@real.estate_kr</span>
<span>정답 공개 →</span>
</div>''', pill_dark=True)
    pts = "\n".join(f'<div style="background: #FFFFFF; color: {INK}; border-radius: 28px; padding: 30px 36px; font-size: 40px; font-weight: 700; line-height: 1.45">{x}</div>' for x in p["v_points"])
    pts_block = f'\n<div style="display: flex; flex-direction: column; gap: 20px">\n{pts}\n</div>' if pts else ""
    vfoot = f'\n<div style="font-size: 38px; font-weight: 700; color: {LIME}; line-height: 1.45">{p["v_foot"]}</div>' if p["v_foot"] else ""
    out[5] = page(f"게시물 {n} 카드 5 판결", BLUE, "#FFFFFF", f'''<div style="display: flex; flex-direction: column; gap: 44px">
<div style="font-size: 40px; font-weight: 700">{p["v_title"]}</div>
<div style="display: flex; align-items: center; gap: 36px">
<span style="flex: none; width: 180px; height: 180px; border-radius: 50%; background: {LIME}; color: {BLUE}; font-family: 'Black Han Sans', sans-serif; font-size: 130px; line-height: 180px; text-align: center">{p["v_letter"]}</span>
<span style="font-family: 'Black Han Sans', sans-serif; font-size: {fit(p["v_head"],80,672)}px; line-height: 1.15">{p["v_head"]}</span>
</div>
<div style="font-size: 42px; font-weight: 700; line-height: 1.5">{p["v_exp"]}</div>{pts_block}{vfoot}
</div>''', 5, foot("→"))
    line = f'\n<div style="font-size: 46px; font-weight: 900; line-height: 1.45">{p["l_line"]}</div>' if p["l_line"] else ""
    out[6] = page(f"게시물 {n} 카드 6 교훈", INK, "#FFFFFF", f'''<div style="display: flex; flex-direction: column; gap: 48px">
<div style="font-size: 40px; font-weight: 700; color: #C8C8C8">오늘의 한 줄</div>
<div style="font-family: 'Black Han Sans', sans-serif; font-size: {fit(p["l_big"],92,888)}px; line-height: 1.2">{p["l_big"]}</div>{line}
<div style="display: flex; align-items: center; gap: 24px; background: {BLUE}; border-radius: 32px; padding: 34px 40px">
<svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="#E3FF5C" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h12v18l-6-4-6 4z"></path></svg>
<span style="font-size: 42px; font-weight: 700; line-height: 1.4">저장해두면 언젠가 써먹는 판례</span>
</div>
</div>''', 6, f'''<div style="display: flex; flex-direction: column; gap: 16px">
<div style="font-size: 26px; color: #C8C8C8; line-height: 1.5">실제 판결 기반 각색 · 법률 자문 아님 · 개별 사안은 전문가 상담<br>출처: {p["src"]}</div>
<span style="font-size: 32px; font-weight: 700; opacity: 0.85">@real.estate_kr</span>
</div>''')
    return out



def info_cards(n, p):
    """정보·정책 카드뉴스 6장: 표지 → 핵심 4개 → 3줄 요약."""
    out = {}
    out[1] = page(f"게시물 {n} 정보 1 표지", BLUE, "#FFFFFF", f"""<div style="display: flex; flex-direction: column; gap: 40px">
<span style="align-self: flex-start; background: #FFFFFF; color: {BLUE}; font-size: 32px; font-weight: 900; padding: 12px 26px; border-radius: 999px">{p["tag"]}</span>
<div style="font-family: 'Black Han Sans', sans-serif; font-size: {fit(p["hook"],116,888)}px; line-height: 1.12; color: {LIME}">{p["hook"]}</div>
<div style="font-family: 'Black Han Sans', sans-serif; font-size: {fit(p["sub"],76,888)}px; line-height: 1.2">{p["sub"]}</div>
</div>""", 1, foot("넘겨서 확인 →"))
    looks = [(BLUE, "#FFFFFF", LIME, "#FFFFFF", INK, False), (INK, "#FFFFFF", LIME, BLUE, "#FFFFFF", False),
             (LIME, INK, BLUE, "#FFFFFF", INK, True), (BLUE, "#FFFFFF", LIME, "#FFFFFF", INK, False)]
    for i, it in enumerate(p["items"][:4]):
        bg, fg, num_c, box_bg, box_fg, dark = looks[i]
        tip = f'\n<div style="font-size: 36px; font-weight: 700; line-height: 1.45; opacity: 0.9">💡 {it["tip"]}</div>' if it.get("tip") else ""
        out[i + 2] = page(f"게시물 {n} 정보 {i+2}", bg, fg, f"""<div style="display: flex; flex-direction: column; gap: 44px">
<div style="font-family: 'Black Han Sans', sans-serif; font-size: 120px; line-height: 1; color: {num_c}">0{i+1}</div>
<div style="font-family: 'Black Han Sans', sans-serif; font-size: {fit(it["t"],100,888)}px; line-height: 1.15">{it["t"]}</div>
<div style="background: {box_bg}; color: {box_fg}; font-size: 44px; font-weight: 700; line-height: 1.55; padding: 44px 48px; border-radius: 36px">{it["b"]}</div>{tip}
</div>""", i + 2, f"""<div style="display: flex; justify-content: space-between; align-items: center; font-size: 32px; font-weight: 700">
<span>@real.estate_kr</span><span>→</span></div>""", pill_dark=dark)
    rows = "\n".join(f"""<div style="display: flex; align-items: flex-start; gap: 26px; background: #FFFFFF; color: {INK}; border-radius: 30px; padding: 32px 38px">
<span style="flex: none; width: 56px; height: 56px; border-radius: 50%; background: {LIME}; font-family: 'Black Han Sans', sans-serif; font-size: 36px; line-height: 56px; text-align: center">✓</span>
<span style="font-size: 42px; font-weight: 900; line-height: 1.4">{x}</span></div>""" for x in p["sum_points"])
    note = f'\n<div style="font-size: 36px; font-weight: 700; color: {LIME}; line-height: 1.45">{p["sum_note"]}</div>' if p.get("sum_note") else ""
    out[6] = page(f"게시물 {n} 정보 6 요약", INK, "#FFFFFF", f"""<div style="display: flex; flex-direction: column; gap: 40px">
<div style="font-family: 'Black Han Sans', sans-serif; font-size: 96px; line-height: 1.15">저장 각!<br><span style="color: {LIME}">3줄 요약</span></div>
<div style="display: flex; flex-direction: column; gap: 20px">
{rows}
</div>{note}
</div>""", 6, f"""<div style="display: flex; flex-direction: column; gap: 16px">
<div style="font-size: 26px; color: #C8C8C8; line-height: 1.5">{p.get("asof", "")} · 일반 정보이며 개별 상황은 전문가 확인<br>출처: {p["src"]}</div>
<span style="font-size: 32px; font-weight: 700; opacity: 0.85">@real.estate_kr</span>
</div>""")
    return out


def auction_cards(n, p):
    """이번 주 추천 경매 매물 6장: 표지 → 물건 개요 → 권리분석 → 시세 → 예상 입찰가 → 체크리스트·경고."""
    out = {}
    def rows(items, light=True):
        bg, fg = ("#FFFFFF", INK) if light else ("rgba(255,255,255,0.12)", "#FFFFFF")
        return "\n".join(f"""<div style="display: flex; justify-content: space-between; align-items: center; gap: 24px; background: {bg}; color: {fg}; border-radius: 26px; padding: 26px 34px">
<span style="font-size: 36px; font-weight: 700; opacity: 0.75; flex: none">{k}</span>
<span style="font-size: 40px; font-weight: 900; text-align: right">{v}</span></div>""" for k, v in items)
    cover_bg, credit = BLUE, ""
    if p.get("bg_image"):  # 법원경매정보 현황조사서 전경 사진 (사람·차량번호·호수 안 보이는 것)
        cover_bg = (f"linear-gradient(180deg, rgba(17,17,17,0.12) 0%, rgba(17,17,17,0.38) 38%, rgba(46,75,255,0.88) 72%, rgba(46,75,255,0.97) 100%), "
                    f"url('file://{ROOT}/{p['bg_image']}') center/cover no-repeat")
        credit = f'<div style="font-size: 24px; opacity: 0.75">사진: {p.get("bg_credit", "법원경매정보 현황조사서")}</div>'
    out[1] = page(f"경매 {n} 1 표지", cover_bg, "#FFFFFF", f"""<div style="display: flex; flex-direction: column; gap: 34px; margin-top: auto">
<span style="align-self: flex-start; background: {LIME}; color: {INK}; font-size: 34px; font-weight: 900; padding: 12px 28px; border-radius: 999px">추천 경매 매물</span>
<div style="font-size: 44px; font-weight: 900; opacity: 0.9">{p["case_no"]}</div>
<div style="font-family: 'Black Han Sans', sans-serif; font-size: {fit(p["hook"],108,888)}px; line-height: 1.12; color: {LIME}">{p["hook"]}</div>
<div style="font-size: 46px; font-weight: 700; line-height: 1.45">{p["sub"]}</div>
{credit}
</div>""", 1, foot("넘겨서 분석 보기 →"))
    out[2] = page(f"경매 {n} 2 개요", "#FFFFFF", INK, f"""<div style="display: flex; flex-direction: column; gap: 22px">
<div style="font-family: 'Black Han Sans', sans-serif; font-size: 84px; line-height: 1.1">물건 개요</div>
{rows(p["overview"])}
</div>""", 2, """<div style="display: flex; justify-content: space-between; font-size: 32px; font-weight: 700"><span>@real.estate_kr</span><span>→</span></div>""", pill_dark=True)
    risk = p.get("rights_verdict", "")
    out[3] = page(f"경매 {n} 3 권리", INK, "#FFFFFF", f"""<div style="display: flex; flex-direction: column; gap: 22px">
<div style="font-family: 'Black Han Sans', sans-serif; font-size: 84px; line-height: 1.1">권리분석</div>
{rows(p["rights"], light=False)}
<div style="background: {LIME}; color: {INK}; border-radius: 26px; padding: 28px 34px; font-size: 42px; font-weight: 900; line-height: 1.4">{risk}</div>
</div>""", 3, f"""<div style="display: flex; flex-direction: column; gap: 12px"><div style="font-size: 26px; color: #C8C8C8">매각물건명세서·현황조사서 기준 ({p.get("doc_date","")}) · 원문 확인 필수</div>
<span style="font-size: 32px; font-weight: 700; opacity: 0.85">@real.estate_kr</span></div>""")
    out[4] = page(f"경매 {n} 4 시세", LIME, INK, f"""<div style="display: flex; flex-direction: column; gap: 22px">
<div style="font-family: 'Black Han Sans', sans-serif; font-size: 84px; line-height: 1.1">시세 비교</div>
{rows(p["market"])}
<div style="font-size: 36px; font-weight: 700; line-height: 1.45">{p.get("market_note","")}</div>
</div>""", 4, """<div style="display: flex; justify-content: space-between; font-size: 32px; font-weight: 700"><span>@real.estate_kr</span><span>→</span></div>""", pill_dark=True)
    out[5] = page(f"경매 {n} 5 입찰가", BLUE, "#FFFFFF", f"""<div style="display: flex; flex-direction: column; gap: 30px">
<div style="font-size: 42px; font-weight: 700">썰방 예상 입찰가</div>
<div style="font-family: 'Black Han Sans', sans-serif; font-size: {fit(p["bid"],120,888)}px; line-height: 1.1; color: {LIME}">{p["bid"]}</div>
<div style="font-size: 40px; font-weight: 700; line-height: 1.5">{p["bid_basis"]}</div>
{rows(p.get("bid_rows", []))}
</div>""", 5, foot("→"))
    checks = "\n".join(f"""<div style="display: flex; gap: 22px; align-items: flex-start; font-size: 40px; font-weight: 700; line-height: 1.4"><span style="color: {LIME}">✓</span><span>{c}</span></div>""" for c in p["checklist"])
    out[6] = page(f"경매 {n} 6 체크", INK, "#FFFFFF", f"""<div style="display: flex; flex-direction: column; gap: 30px">
<div style="font-family: 'Black Han Sans', sans-serif; font-size: 84px; line-height: 1.1">입찰 전 체크</div>
<div style="display: flex; flex-direction: column; gap: 18px">{checks}</div>
<div style="border: 4px solid #FF5A5A; border-radius: 26px; padding: 26px 32px; font-size: 34px; font-weight: 700; line-height: 1.5; color: #FFD0D0">⚠ 투자 판단과 책임은 본인에게 있습니다. 공개 자료를 바탕으로 한 개인 분석이며 법률·투자 자문이 아닙니다. 입찰 전 등기부등본·매각물건명세서 원문과 현장을 반드시 직접 확인하세요.</div>
</div>""", 6, f"""<div style="display: flex; flex-direction: column; gap: 12px"><div style="font-size: 26px; color: #C8C8C8">출처: {p["src"]}</div>
<span style="font-size: 32px; font-weight: 700; opacity: 0.85">@real.estate_kr</span></div>""")
    return out

FONT_CSS = """<style>
@font-face{font-family:'Black Han Sans';src:url('file://%(r)s/fonts/BlackHanSans-Regular.ttf')}
@font-face{font-family:'Noto Sans KR';src:url('file://%(r)s/fonts/NotoSansKR[wght].ttf');font-weight:100 900}
body{margin:0}</style>""" % {"r": ROOT}

def plain(s):
    inner = re.search(r"<x-dc>(.*)</x-dc>", s, re.S).group(1)
    inner = re.sub(r"<helmet>.*?</helmet>", "", inner, flags=re.S)
    return '<!doctype html><html lang="ko"><head><meta charset="utf-8">' + FONT_CSS + '</head><body>' + inner + '</body></html>'

def main():
    data = json.load(open(sys.argv[1]))
    only = {int(x) for x in sys.argv[2:]}
    from playwright.sync_api import sync_playwright
    out_dir = os.path.join(ROOT, "cards"); os.makedirs(out_dir, exist_ok=True)
    problems = []
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = br.new_page(viewport={"width": 1080, "height": 1350})
        for post in data["posts"]:
            n = int(post["id"])
            if only and n not in only: continue
            maker = {"info": info_cards, "auction": auction_cards}.get(post.get("type"), cards)
            if post.get("type") in ("reel", "short") and not post.get("also_cards"): continue
            for k, s in maker(n, post).items():
                tmp = os.path.join("/tmp", f"X{n}-{k}.html")
                open(tmp, "w").write(plain(s))
                pg.goto("file://" + tmp)
                pg.evaluate("document.fonts.ready")
                pg.wait_for_timeout(200)
                fonts_ok = pg.evaluate("document.fonts.check(\"40px 'Black Han Sans'\") && document.fonts.check(\"40px 'Noto Sans KR'\")")
                ov = pg.evaluate("(()=>{const r=document.body.firstElementChild; return [r.scrollWidth, r.scrollHeight]})()")
                path = os.path.join(out_dir, f"{post.get('prefix', 'P')}{n:02d}-{k}.jpg")
                pg.screenshot(path=path, type="jpeg", quality=90, clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
                if ov[0] > 1080 or ov[1] > 1350: problems.append(f"OVERFLOW P{n:02d}-{k} {ov}")
                if not fonts_ok: problems.append(f"FONT P{n:02d}-{k}")
                print("rendered", path)
        br.close()
    for x in problems: print(x)
    sys.exit(1 if problems else 0)

if __name__ == "__main__":
    main()
