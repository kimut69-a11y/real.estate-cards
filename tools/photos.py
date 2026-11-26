#!/usr/bin/env python3
"""쇼츠 photo 장면에 들어갈 실제 사진을 Pixabay(기본) 또는 Pexels에서 자동으로 받아온다.

사용법: python3 tools/photos.py posts/daily/YYYY-MM-DD.json [id ...] [--status]
- 보통은 GitHub Actions(.github/workflows/photos.yml)가 posts/daily/*.json push 때 자동 실행한다
  (클라우드 작업 환경은 pixabay.com 접속이 막혀 있음). --status 를 주면 assets/photos/status/S<id>.txt 에 결과를 남긴다.
- type=short 게시물의 장면 중 {"type": "photo", "q": "영어 검색어", ...} 를 찾아
  Pexels에서 세로 사진을 검색하고 assets/photos/auto/S<id>-<번호>.jpg 로 저장한 뒤
  그 장면에 "photo": "auto/S<id>-<번호>" 를 채워 JSON을 다시 쓴다.
- 이미 쓴 사진(assets/photos/used.json)은 다시 고르지 않는다.
- Pexels 이용 조건에 따라 캡션의 '🎙️ AI 음성' 줄 바로 위에 사진 출처 줄을 자동으로 넣는다.
- 출처는 assets/photos/LICENSES.md 표에도 한 줄씩 남긴다.

인증: 환경 변수 PIXABAY_API_KEY 가 있으면 Pixabay(허용 도메인 pixabay.com, cdn.pixabay.com).
      Pixabay 사진은 출처 표기 의무가 없어 캡션은 건드리지 않고 LICENSES.md 에만 남긴다.
      없으면 Pexels(PEXELS_API_KEY 또는 네트워크 비밀이 Authorization 헤더를 붙임, 캡션에 출처 줄 필수).
사진을 못 받으면(키 없음·접속 차단·검색 결과 없음) 그 장면은 그대로 두고 경고만 출력한다.
shorts.py가 사진 없는 photo 장면을 이모지 장면으로 바꿔 렌더링하므로 제작은 멈추지 않는다.
"""
import json, os, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PH = os.path.join(ROOT, "assets", "photos")
AUTO = os.path.join(PH, "auto")
USED = os.path.join(PH, "used.json")
LIC = os.path.join(PH, "LICENSES.md")
CREDIT_MARK = "📷 Photos provided by Pexels"


def get(url, auth=True):
    h = {"User-Agent": "real.estate-cards/1.0"}
    key = os.environ.get("PEXELS_API_KEY")
    if auth and key:
        h["Authorization"] = key
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30) as r:
        return r.read()


def search(q, used):
    for page in (1, 2):
        u = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
            {"query": q, "orientation": "portrait", "size": "large", "per_page": 30, "page": page})
        data = json.loads(get(u))
        for ph in data.get("photos", []):
            if str(ph["id"]) not in used and ph.get("height", 0) >= 1600:
                return ph
    return None


def search_pixabay(q, used):
    for page in (1, 2):
        u = "https://pixabay.com/api/?" + urllib.parse.urlencode(
            {"key": os.environ["PIXABAY_API_KEY"], "q": q[:100], "image_type": "photo", "orientation": "vertical",
             "min_height": 1200, "safesearch": "true", "per_page": 50, "page": page})
        data = json.loads(get(u, auth=False))
        for h in data.get("hits", []):
            if f"pixabay-{h['id']}" not in used:
                return {"id": f"pixabay-{h['id']}", "photographer": h.get("user", ""), "url": h.get("pageURL", ""),
                        "img": h["largeImageURL"], "site": "Pixabay"}
    return None


def search_pexels(q, used):
    ph = search(q, used)
    if not ph:
        return None
    return {"id": str(ph["id"]), "photographer": ph.get("photographer", ""), "url": ph.get("url", ""),
            "img": ph["src"]["original"].split("?")[0] + "?auto=compress&cs=tinysrgb&fit=crop&w=1080&h=1920", "site": "Pexels"}


def fit(path):
    """세로 1080x1920 으로 채워 자르기 (Pillow, 없으면 ffmpeg)"""
    try:
        from PIL import Image, ImageOps
        im = ImageOps.fit(Image.open(path).convert("RGB"), (1080, 1920), Image.LANCZOS)
        im.save(path, "JPEG", quality=88)
        return
    except ImportError:
        pass
    import subprocess
    tmp = path + ".tmp.jpg"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-vf",
                    "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", "-q:v", "3", tmp], check=True)
    os.replace(tmp, path)


def scenes_of(p):
    for ln in p.get("lines", []):
        sc = ln.get("scene")
        for s in (sc if isinstance(sc, list) else [sc]):
            if isinstance(s, dict) and s.get("type") == "photo":
                yield s


def main():
    args = sys.argv[1:]
    status = "--status" in args
    args = [a for a in args if a != "--status"]
    path = args[0]
    only = {int(x) for x in args[1:]}
    done = []
    data = json.load(open(path))
    os.makedirs(AUTO, exist_ok=True)
    used = json.load(open(USED)) if os.path.exists(USED) else {}
    warn, changed = [], False
    for p in data["posts"]:
        if p.get("type") != "short" or (only and int(p["id"]) not in only):
            continue
        n = int(p["id"]); credits = []; k = 0; done.append(n)
        for s in scenes_of(p):
            k += 1
            if s.get("photo") and any(os.path.exists(os.path.join(PH, s["photo"] + e)) for e in (".jpg", ".jpeg", ".png")):
                if s.get("credit"):
                    credits.append(s["credit"])
                continue
            q = s.get("q")
            if not q:
                if not s.get("photo"):
                    warn.append(f"PHOTO S{n} 장면 {k}: q(영어 검색어) 없음 → 이모지 장면으로 대체됨")
                continue
            try:
                ph = (search_pixabay if os.environ.get("PIXABAY_API_KEY") else search_pexels)(q, used)
                if not ph:
                    warn.append(f"PHOTO S{n} 장면 {k}: '{q}' 검색 결과 없음 → 이모지 장면으로 대체됨"); continue
                name = f"S{n}-{k}"
                out = os.path.join(AUTO, name + ".jpg")
                open(out, "wb").write(get(ph["img"], auth=False))
                fit(out)
            except Exception as e:  # 키 없음(401), 접속 차단(403) 등
                warn.append(f"PHOTO S{n} 장면 {k}: 받기 실패 ({e}) → 이모지 장면으로 대체됨"); continue
            s["photo"] = f"auto/{name}"
            if ph["site"] == "Pexels":
                s["credit"] = ph["photographer"]
                credits.append(s["credit"])
            used[ph["id"]] = name
            with open(LIC, "a") as f:
                f.write(f"| auto/{name}.jpg | [{ph['photographer']} on {ph['site']}]({ph['url']}) | {ph['site']} License |\n")
            changed = True
            print(f"photo {name}.jpg ← '{q}' by {ph['photographer']} ({ph['site']})")
        # 캡션 출처 줄
        if credits and p.get("caption"):
            names = ", ".join(dict.fromkeys(c for c in credits if c))
            line = f"{CREDIT_MARK} · 사진: {names}" if names else CREDIT_MARK
            lines = [x for x in p["caption"].split("\n") if not x.startswith(CREDIT_MARK)]
            at = next((i for i in range(len(lines) - 1, -1, -1) if lines[i].startswith("🎙️")), len(lines))
            lines.insert(at, line)
            new = "\n".join(lines)
            if new != p["caption"]:
                p["caption"] = new; changed = True
    if changed:
        json.dump(used, open(USED, "w"), ensure_ascii=False, indent=1)
        json.dump(data, open(path, "w"), ensure_ascii=False, indent=1)
    for w in warn:
        print(w)
    if status:  # GitHub Actions: 끝났다는 표시(제작 작업이 tools/wait_photos.sh 로 기다림)
        sd = os.path.join(PH, "status"); os.makedirs(sd, exist_ok=True)
        for n in done:
            mine = [w for w in warn if f"S{n} " in w]
            open(os.path.join(sd, f"S{n}.txt"), "w").write("\n".join(mine) if mine else "OK\n")


if __name__ == "__main__":
    main()
