# 부동산 썰방 자동화 지침서 (v3)

인스타그램 @real.estate_kr '부동산 썰방' (30~40대 대상)을 사람 손 없이 매일 만들고 예약 게시한다.
사용자는 확인·승인하지 않는다(애매한 게시물은 사용자가 올라간 뒤 직접 삭제). 그러니 **정확성은 이 작업이 책임진다.**

| 언제 | 무엇 | 만드는 작업 |
|---|---|---|
| 매일 21:00 | 1분 썰 쇼츠 (AI 여성 나레이션, '1분만' 스타일) | 매일 제작 작업 (클라우드, 10:47) |
| 격일 12:30 — **뉴스의 날** | 부동산 뉴스 카드뉴스 (정책·제도 변화) | 매일 제작 작업 (클라우드, 10:47) |
| 격일 12:30 — **경매의 날** | 추천 경매 매물 카드뉴스 | 경매 작업 (사용자 맥북, 10:41) |

**격일 규칙**: D = (오늘 날짜 − 2026-11-24) 일수. **D가 짝수면 경매의 날, 홀수면 뉴스의 날.**
(11/24 화 경매, 11/25 수 뉴스, 11/26 목 경매, 11/27 금 뉴스 … 요일과 상관없이 계속 번갈아 감)
확인: `python3 -c "import datetime;d=(datetime.date.today()-datetime.date(2026,11,24)).days;print('경매' if d%2==0 else '뉴스')"` (날짜는 Asia/Seoul 기준. 컨테이너가 UTC면 `TZ=Asia/Seoul`을 앞에 붙임)

## 0. 고정 정보
- 저장소: https://github.com/kimut69-a11y/real.estate-cards (공개, main). push 전 항상 `git pull --rebase`.
- 이미지: `https://raw.githubusercontent.com/kimut69-a11y/real.estate-cards/main/cards/<파일>.jpg`
- 영상: `https://raw.githubusercontent.com/kimut69-a11y/real.estate-cards/main/reels/<파일>.mp4`
- 게시: Windsor.ai for Social Media `execute_action`, connector=`instagram`, account=`17841435414933916`
  - 카드뉴스: action=`create_carousel_post` (image_urls 6개, caption)
  - 쇼츠: action=`create_video_post` (video_url, cover_url, share_to_feed=true, caption). cover_url = `.../reels/S<YYYYMMDD>.jpg` (한글 제목 썸네일). jpg가 없을 때만 cover_url 대신 thumb_offset=1500
- 파일 이름 (날짜 = 게시일, YYYYMMDD):
  - 뉴스 카드: `posts/daily/YYYY-MM-DD.json` 의 type=info, id=YYYYMMDD, prefix="N" → `cards/NYYYYMMDD-1~6.jpg`
  - 쇼츠: 같은 파일의 type=short, id=YYYYMMDD → `reels/SYYYYMMDD.mp4` + 썸네일 `reels/SYYYYMMDD.jpg` (shorts.py가 함께 만듦. **둘 다 commit**, 받은 사진 `assets/photos/` 도 commit)
  - 썸네일: 무슨 이야기인지 한눈에 알게 한글 제목을 크게. 기본은 title을 첫 쉼표에서 나눠 '윗줄 + 노란 띠 질문'(예: "소음 숨기고 판 아파트, 계약 무를 수 있을까?"). 그래서 title은 '상황, 질문?' 꼴로 짧게. 필요하면 "cover": {"text", "q", "emoji"}로 직접 지정. 렌더 후 jpg를 직접 열어 글자가 잘리거나 넘치지 않는지 확인. 썸네일만 다시: `python3 tools/shorts.py --cover posts/daily/<날짜>.json`
  - 실제 사진: 쇼츠마다 장면 3~5개를 photo 장면으로(집·아파트·계약서·법원·공사장 등 사람이 주인공이 아닌 장면). Pixabay(기본, 환경 변수 PIXABAY_API_KEY) 또는 Pexels에서 자동으로 받음(`tools/photos.py`, 3번 렌더링 참고). 뉴스·방송 캡처, 다른 계정 사진은 절대 쓰지 않음
  - 경매 카드: `posts/auction/YYYY-MM-DD.json` 의 type=auction, id=YYYYMMDD, prefix="A" → `cards/AYYYYMMDD-1~8.jpg` (입지 페이지가 없으면 1~7)
- 도구: `tools/cards.py`(카드), `tools/shorts.py`(쇼츠), `tools/setup_tts.sh`(음성 도구 설치, 매 실행 처음에 1회)

## 1. 준비 (매 실행)
1. `git clone https://github.com/kimut69-a11y/real.estate-cards` (인증 실패 시 Claude_Code_Remote `add_repo` owner=kimut69-a11y repo=real.estate-cards access=push)
2. `/usr/bin/google-chrome`, `ffmpeg`, `python3 -c "import playwright"` 확인. 패키지 설치는 시도하지 않음
3. 쇼츠를 만들 때: `bash tools/setup_tts.sh` (GitHub에서 Supertonic 3 음성·음성인식 모델을 받음, 1~2분)
4. 오늘 파일이 이미 있으면 새로 만들지 말고 빠진 단계(렌더링·push·예약)만 이어서 함
5. 시작할 때 Windsor `get_connectors`로 instagram 연결과 필요한 action 확인. 안 되면 제작·push만 하고 예약은 만들지 말고 보고 맨 위에 적음

## 2. 부동산 뉴스 카드 (뉴스의 날 12:30)
- 주제: 최근 1~2주 안에 발표·시행·확정된 부동산 정책·제도·세금·대출·청약·전월세·공급 관련 변화 1건. 시행일이 다가오는 제도, 그 주 일정(종부세 납부, 청약 일정 등)도 좋음
- 이전 `posts/**/*.json` 의 type=info `title`과 겹치지 않게
- **사실 확인 필수**: 정부(korea.kr, 국토교통부, 금융위원회, 국세청, 기획재정부), 국가법령정보센터, 주요 언론으로 교차 확인. 숫자·날짜·요건은 출처와 정확히 일치. 확인 안 되는 내용은 쓰지 않음. 발표만 되고 시행 전이면 "시행 예정", 국회 통과 전이면 "추진 중"이라고 분명히 씀
- 정치적 평가·찬반 의견 금지. 무엇이 바뀌는지, 누구에게 영향이 있는지만
- 형식(type=info, `posts/week01.json`의 101~107 예시 참고): tag(예: "이번 주 부동산 뉴스"), hook/sub(각 2줄 `<br>`, 줄당 한글 약 9자/8자), items 4개 `{"t":"제목 2줄","b":"설명 약 55자","tip":"선택"}`, sum_points 3개, sum_note(선택), asof("2026년 11월 24일 기준" 등), src(기관·매체명)
- 캡션('캡션 공통 스타일' 적용): 훅 한 줄 → 핵심 변화 짧은 문단 3~5개 → 저장·공유 유도 / 빈 줄 / `⚠️ 일반 정보이며 개별 상황은 전문가 확인` / 빈 줄 / `#부동산썰방 #부동산뉴스` + 주제 태그 4개

## 3. 1분 썰 쇼츠 (매일 21:00)
### 사례 고르기
- **실제 판결만.** 부동산 분쟁(층간소음·누수·전세·매매·경매·상가·재건축 등). WebSearch/WebFetch로 사건번호·법원·금액·결론을 확인. 출처와 정확히 일치. 확인 안 되면 다른 사건
- 이전 `posts/**/*.json`의 `src`와 같은 판결은 다시 쓰지 않음. `posts/week01.json`의 사례들(2~14번)은 이미 검증된 판결이니 쇼츠 대본으로 다시 써서 써도 됨(같은 판결로 쇼츠는 한 번만). 단 6번(인천지법 2020가단207528, 층간소음 보복)은 2026-11-23에 쇼츠 S900으로 이미 게시됨 — 다시 쓰지 않음
- 주제가 한쪽으로 몰리지 않게 직전 6일과 다른 분야 우선
### 대본 쓰기 (`posts/proto.json` 이 기준 예시 — 사용자가 승인한 속도감)
- **목표 45~55초, 16~20문장.** 친구한테 썰 풀듯 빠르고 친근한 반말. 첫 문장은 짧은 훅("들어봐."), 둘째 문장에 갈등, 셋째에 "근데 반전" 류의 꺾기, 중간에 "법원은 얼마를 물어주라고 했을까?" 같은 질문, 끝은 한 줄 교훈
- 판결 원문·기사에서 확인한 사실만 쓴다(증거, 쟁점, 법원이 인정한 사실 등으로 문장 수를 채움). 지어낸 디테일 금지
- `say`(읽을 문장): 숫자는 한글로 풀어 씀(1,960만 → 천구백육십만). 어려운 한자어·약어는 쉬운 말로. 문장당 한글 45자 이내로 짧게
- `sub`(자막): 숫자 표기 가능. `|`로 2~3개 덩어리, 덩어리당 15~20자
- `scene`: **자막 덩어리 수만큼 장면을 리스트로** 넣어 1.5~2.5초마다 화면이 바뀌게 함(덩어리가 1개면 장면 1개). 같은 장면 종류가 3번 연속되지 않게. 종류: title, big(화면 꽉 찬 이모지+한 단어), emoji, char(face: normal/happy/shock/angry/sad/smug/think), vs, money, compare, court, end, **photo(실제 사진)**
- `photo` 장면: `{"type":"photo","q":"영어 검색어","label":"짧은 한글 라벨","emoji":"🏠"}`. 대본 전체에 3~5개, 연속 2개 이하. q는 구체적이고 사람 얼굴이 주인공이 아닌 것. 한국 아파트는 `korean apartment complex`·`seoul apartment buildings`처럼 'korean/seoul'을 붙이고(그냥 apartment는 외국 고층 빌딩이 나옴), 설비는 `boiler room pipes`·`industrial pump machinery`처럼 실내 기계실 느낌으로(그냥 water pump는 마당 손펌프가 나옴). 예: `signing contract paper`, `courthouse`, `judge gavel`, `moving boxes`, `store interior`, `water leak ceiling`. 간판·상호·로고가 크게 보이는 사진은 바꿈(Pixabay 라이선스상 상표가 보이는 상업 이용 금지), 한국 이야기에 유럽풍 건물처럼 어색한 사진도 바꿈. 사진은 분위기 자료이므로 라벨은 사실(사건)만 쓰고 '실제 현장'처럼 보이게 쓰지 않음
- `pop`: 문장 2개 중 1개꼴로 스티커 1~2개. 반전·충격 지점엔 밈 문구(`{"t":"실화냐?"}`, 헐, 소름, 킹받네, 빼박, 대박, 어이없네 — 2~4글자. ㄷㄷ·ㅋㅋ처럼 자음만 쓴 문구는 굵은 폰트에서 영문 CC처럼 보이므로 금지), 감정 지점엔 이모지(Microsoft Fluent 3D 이미지로 자동 변환, tools/emoji.py)(`{"e":"😱"}` 🤯 😤 😭 👀 💥 🚨 🙄 🤑). `at`(0~1)은 그 문장에서 해당 단어가 나오는 위치, `pos`는 자막·주요 그림을 가리지 않게 tl/tr 위주
- 마지막 문장은 scene type=end (교훈 + "팔로우하면 매일 1분 판례")
- voice는 보통 넣지 않음(기본: 여성 sid 0, 1.15배속 합성 + 재생 1.16배). 길이가 45초보다 짧으면 `"voice": {"tempo": 1.1}`
- 효과음(장면 전환 '휙', 스티커 '뿅', 금액·제목 '쿵')은 자동으로 들어감
### 렌더링·검수
0. 실제 사진(GitHub이 자동으로 받음 — 클라우드 작업 환경은 pixabay.com 접속이 막혀 있으므로 photos.py를 직접 돌리지 않음):
   대본(photo 장면에 q 포함)과 caption을 다 쓴 JSON을 `git rm -q --ignore-unmatch assets/photos/status/SYYYYMMDD.txt` 와 함께 commit → `git pull --rebase` → push
   → GitHub Actions(shorts-photos)가 Pixabay 사진을 `assets/photos/auto/`에 받고 JSON의 photo 장면을 채워 다시 push함
   → `bash tools/wait_photos.sh YYYYMMDD` 로 기다림(최대 7분). `OK`면 사진 완료. `PHOTO … 실패`나 `TIMEOUT`이면 그 장면은 이모지로 대체되니 그대로 진행하고 보고에 한 줄 적음
   → 장면 확인(3번)에서 사진이 내용과 어울리는지 보고, 어색하면 그 장면의 q를 바꾸고 photo·credit을 지운 뒤 위 과정을 한 번 더(최대 1번)
1. `python3 tools/shorts.py posts/daily/YYYY-MM-DD.json` → `reels/SYYYYMMDD.mp4`
2. 출력의 `PRONUNCIATION` 경고: 그 문장의 `say`에서 잘못 들린 단어를 더 쉬운 말로 바꿔 다시 렌더링(최대 3번, 일치율 0.75 이상이고 뜻이 같게 들리면 통과). `OVERFLOW`는 글자·이모지 크기(size, esize)를 줄임. 종료 코드 0이어야 함
3. 장면 확인: `ffmpeg -i reels/SYYYYMMDD.mp4 -vf "select='not(mod(n\,150))',scale=270:480,tile=6x2" -frames:v 1 /tmp/x.png` 후 Read로 보고 글자 잘림·겹침 확인
4. 사실 재확인: 금액·결론·법원명·사건번호를 출처와 다시 대조
- 캡션('캡션 공통 스타일' 적용): 훅 한 줄 → 사건 요약 짧은 문단 3~4개(결론은 숨김) → "끝까지 보면 판결 공개" 류 + 댓글·팔로우 유도 / 빈 줄 / `⚠️ 실제 판결 기반 각색 · 법률 자문 아님 · 개별 사안은 전문가 상담` / 빈 줄 / `#부동산썰방 #부동산판례 #1분판례` + 주제 태그 3개 / 영상에 AI 음성을 썼으므로 캡션 맨 끝 줄에 `🎙️ AI 음성` 표기

## 캡션(피드 본문) 공통 스타일 — 뉴스·쇼츠·경매 전부 (사용자 지정)
기업 공식 계정 소식글처럼 깔끔하고 전문적으로. 참고 형식(GS건설 자이 공식 계정 글):
```
목동 신시가지 첫 번째 '자이' 😍

'목동12단지' 재건축 사업의 시공사로
GS건설이 최종 선정되었습니다! 🎉

목동 신시가지 14개 단지 재건축에서
처음으로 선보이는 자이 브랜드 💫
```
- 첫 줄: 핵심을 담은 한 줄 훅 + 이모지 1개
- 본문: **2줄 이하의 짧은 문단 4~6개**, 문단 사이 빈 줄. 한 줄은 25자 안팎에서 의미 단위로 줄바꿈
- 이모지는 문단 끝에 0~1개(전체 5~7개), 내용과 맞는 것만(📍🏠✅📉💰🌳⚖️📌👉💬 등). 남발 금지
- 문체는 '~습니다/~입니다'로 통일(반말·'~요' 섞지 않음). 맞춤법·띄어쓰기 검수 필수: 금액은 '1억 2,950만 원'(숫자와 '원' 띄움), 날짜는 '11월 26일(목)', 따옴표는 ' ' 통일, 물결은 '1억 3,270만~4,540만 원'
- 마지막 문단: 행동 유도(넘겨 보기/끝까지 보기/팔로우·댓글·DM)
- 그다음 빈 줄 → ⚠️ 고지문 한 문단 → 빈 줄 → 해시태그 한 줄 (쇼츠는 맨 끝 줄에 `🎙️ AI 음성`)
- 작성 후 스스로 한 번 더 읽고 오탈자·띄어쓰기·사실(숫자) 대조

## 4. 추천 경매 매물 (경매의 날 12:30) — 맥북 작업
**원칙: 무조건 정확하게. 조금이라도 애매하면 올리지 않는다.**
- 후보: ① 사용자 맥북 `/Users/kimut/Desktop/01_김유탁/01_경매/모의입찰` 의 최신 `경매물건_YYYYMMDD.xlsx` 목록 물건, `분석_<사건번호>.xlsx`가 있으면 그 분석 우선 ② 법원경매정보(courtauction.go.kr)에서 전국 아파트 중 조회수 상위 물건
- **매각물건명세서가 열람 가능한 물건만** (보통 매각기일 1주 전부터). 매각기일이 게시일 다음 날 이후여야 함. 이전에 올린 사건번호(`posts/auction/*.json`의 case_no)는 다시 올리지 않음
- 분석 방법은 `auction-case-analysis` 스킬 절차 그대로 (내장 브라우저로 사건내역·문건송달내역·매각물건명세서·현황조사서 확인, 시세·거래량·세대수·낙찰가율 조사)
- 매각물건명세서는 이미지라 판독 오류가 날 수 있으므로 **말소기준권리 일자·임차인 전입일·확정일자·배당요구 여부·인수 권리·비고란을 두 번 따로 판독해 일치할 때만** 사용
- 올리지 않는 경우(다음 후보로 넘어감): 대항력 있는 임차인 / 배당요구 안 한 선순위 임차인 / 인수 권리 있음 / 지분·대지권 미등기·유치권·법정지상권·선순위 가처분·가등기·재매각 / 명세서 비고란에 특이사항 / 판독이 두 번 일치하지 않음 / 시세 근거가 3개월 거래 2건 미만
- 후보를 3건까지 봐도 조건을 만족하는 물건이 없으면 **그날은 게시하지 않고** 사유를 보고
- 12:20까지 분석·업로드가 끝나지 않으면 늦게 올리지 말고 그 회차는 건너뛰고 보고(다음 날 뉴스와 겹치지 않게)
- 예상 입찰가: 최근 3개월 동일평형 실거래 평균, 지역 아파트 낙찰가율, 취득세·비용, 목표수익률 10%를 근거로 범위로 제시(스킬의 엑셀 계산과 일치해야 함). 근거를 5번 카드에 적음
- 형식(type=auction, prefix="A"): case_no("OO지방법원 2026타경12345"), hook(감정가·최저가 2줄), 표지 배지는 '추천 경매 매물', sub(지역·단지·평형·유찰·매각일), overview 5줄 `[["항목","값"],...]`, rights 4줄(말소기준권리/임차인/인수 권리/특수사항), rights_verdict(한 줄 결론), doc_date(명세서 열람일), market 4줄, market_note, bid("1억 9,300만 ~ 9,800만"), bid_basis, bid_rows 2줄, checklist 4개, src
- **표지 배경 사진**: 법원경매정보 물건상세 페이지의 '전경도'·'관련사진'(이미지는 data URI) 중 단지 외관이 잘 보이고 사람 얼굴·차량번호·현관 호수·내부가 보이지 않는 사진 1장을 고른다. 브라우저에서 그 이미지를 화면 좌상단에 원본 크기로 띄운 뒤 computer zoom으로 캡처하면 결과 이미지가 작업 환경의 /tmp/claude-tool-results/ 아래에 저장되니, 그 파일을 `cards/bg/AYYYYMMDD.jpg`로 복사하고 JSON에 `"bg_image": "cards/bg/AYYYYMMDD.jpg"`를 넣는다(출처 '사진: 법원경매정보 현황조사서'가 자동 표기됨). 마땅한 사진이 없으면 bg_image 없이 기본 파란 배경
- **카드 구성(8장)**: 표지 → **입지 포인트(지도)** → 물건 개요 → 권리분석 → 시세 → 예상 입찰가 → 입찰 전 체크·경고 → **팔로우 안내**(마지막 장 문구 "계속해서 매력적인 경매 매물을 받아보고 싶으면 팔로우! 부탁드려요 / 궁금하신 사항 있으면 DM 혹은 댓글 부탁드립니다"는 cards.py가 자동으로 넣음)
- **입지 포인트(`location`)**: 매수자 눈길을 끄는 강점 3개(역세권·초품아/학교 거리·대형마트·공원/산책로·IC·직장(산단) 등 확인된 것만). 거리는 OpenStreetMap 좌표로 계산한 **직선거리**로 적고 "약 360m"처럼 반올림. 학교·역 이름은 학교알리미/오늘학교 등으로 실제 존재 확인. 확인 못 한 강점은 넣지 않음(과장 금지, "학군 최고" 같은 평가 문구 금지)
  - 좌표: 내장 브라우저로 openstreetmap.org 를 열고(허용됨) 페이지에서 `fetch('https://nominatim.openstreetmap.org/search?format=json&countrycodes=kr&limit=15&q=<검색어>&viewbox=<서,북,동,남>&bounded=1')` 로 학교·IC·역 좌표를 얻는다(요청 사이 1.1초 간격). 단지는 지도에서 이름 라벨 위치로 잡는다
  - 지도 배경: `https://www.openstreetmap.org/export/embed.html?bbox=<서>,<남>,<동>,<북>&layer=mapnik` (가로 약 1.8km) 를 열고 3초 대기 → `.leaflet-control-zoom` 제거 → computer zoom으로 지도 영역(세로로 긴 부분, 하단 저작권 줄 제외)을 캡처 → /tmp/claude-tool-results/ 의 파일을 PIL로 4:5 크롭 후 1080×1350 리사이즈·GaussianBlur(1.0)·채도 0.8 → `cards/bg/AYYYYMMDD-map.jpg`
  - JSON: `"location": {"map_image": "...", "shift": 0~250(핀들이 위쪽 60% 안에 오도록 지도를 위로 올리는 픽셀), "headline": "초·중학교가 단지 바로 옆"(가장 강한 강점 한 줄), "pins": [{"x":..,"y":..,"label":"단지명","e":"🏠","main":true}, {"x":..,"y":..,"label":"OO초","e":"🏫"}, ...최대 3~4개], "points": [["🏫","제목","세부(거리 등)"], ×3], "note": "거리는 단지 기준 직선거리"}` — 핀 x,y는 1080×1350 지도 이미지 기준 픽셀(핀 끝이 그 지점을 가리킴). 렌더 후 반드시 2번 카드를 Read로 보고 핀이 실제 위치를 가리키는지, 제목·하단 패널과 겹치지 않는지 확인
  - 지도 캡처가 안 되면 location 없이 7장으로 게시(입지 강점은 캡션에만)
- 캡션에도 마지막에 `계속해서 매력적인 경매 매물들을 받아보고 싶으면 팔로우! 부탁드리고, 궁금하신 사항 있으면 DM 혹은 댓글 부탁드립니다 💬` 한 줄을 경고문 앞에 넣는다
- 캡션('캡션 공통 스타일' 적용): 훅 한 줄(단지·평형·최저가) → 사건번호·매각기일 / 유찰·최저가 / 권리관계 / 입지 강점 / 시세·예상 입찰가 문단 → 넘겨 보기 유도 → 팔로우·DM 문단 / 빈 줄 / `⚠️ 투자 판단과 책임은 본인에게 있습니다. 공개 자료 기반 개인 분석이며 법률·투자 자문이 아닙니다. 입찰 전 등기부등본·매각물건명세서 원문과 현장을 반드시 확인하세요.` / 빈 줄 / `#부동산썰방 #경매 #법원경매 #아파트경매 #경매물건 #지역명`
- 분석 엑셀(`분석_<사건번호>.xlsx`)은 모의입찰 폴더에도 저장

## 5. 업로드
- `git add cards reels posts && git commit -m "..." && git pull --rebase && git -c push.negotiate=true push`
- 확인: `curl -s https://api.github.com/repos/kimut69-a11y/real.estate-cards/contents/<경로>` 에 size가 있어야 함

## 6. 게시 예약
- **쇼츠는 고정 작업 '썰방 매일 21:00 쇼츠 게시'(매일 21:00)가 자동 게시**한다. 이 작업은 `posts/daily/YYYY-MM-DD.json` 의 type=short, id=YYYYMMDD 게시물의 `caption` 필드와 `reels/SYYYYMMDD.mp4` 를 읽는다. 그러므로 제작 작업은 쇼츠용 1회 예약을 만들지 않고, **JSON에 caption 필드를 꼭 넣어 21:00 전에 push**만 하면 된다. 같은 날 이름이 '썰방 쇼츠 MM/DD 21:00'인 1회 예약이 있으면 고정 작업은 건너뛴다(중복 방지).
- (이유: 자동 실행 중에는 예약 작업을 새로 만들 때 사용자 승인이 필요해 막힘. 2026-11-24 확인)
- **카드뉴스는 고정 작업 '썰방 매일 12:30 카드뉴스 게시 (뉴스/경매)'(매일 12:30)가 자동 게시**한다. 뉴스의 날엔 `posts/daily/YYYY-MM-DD.json` type=info + `cards/NYYYYMMDD-1~6.jpg`, 경매의 날엔 `posts/auction/YYYY-MM-DD.json` type=auction + `cards/AYYYYMMDD-1~8.jpg`(또는 1~7)를 읽고 `caption` 필드를 그대로 쓴다. 파일이 없으면 게시하지 않는다. 그러므로 뉴스·경매 작업도 1회 예약을 만들지 말고 **caption 필드를 넣어 12:20까지 push**만 한다. 12:20까지 못 끝내면 push하지 않는다. 같은 날 '썰방 뉴스/경매 MM/DD 12:30' 1회 예약이 있으면 고정 작업은 건너뛴다.
- 아래 1회 예약 방식과 프롬프트는 고정 작업이 멈췄을 때 사용자가 직접 요청하는 경우에만 쓴다.
- 1회 예약 (Claude_Code_Remote create_trigger) name: `썰방 뉴스 MM/DD 12:30` / `썰방 쇼츠 MM/DD 21:00` / `썰방 경매 MM/DD 12:30`. 같은 이름이 이미 있으면 만들지 않음(list_triggers로 확인)
- run_once_at: `YYYY-MM-DDTHH:MM:00[Asia/Seoul]`, initiation `human_schedule`, notifications `{"push": false}` (사용자는 매번 알림을 원하지 않음; 실패해도 다음 제작 작업이 보고)
- 게시 시각이 이미 지났으면(제작이 늦어진 경우) 예약 대신 지금 바로 게시하지 말고 다음 날 같은 시각으로 예약

카드뉴스 게시 프롬프트:
```
인스타그램 @real.estate_kr에 '부동산 썰방' 카드뉴스 <파일접두사>를 게시하세요. 사용자가 미리 요청한 자동 게시이며, 이 작업은 이 게시물 하나만 올립니다.
1. Windsor.ai for Social Media 커넥터의 execute_action 도구를 사용하세요(지연 로드 상태면 ToolSearch로 먼저 불러오세요). connector="instagram", account="17841435414933916", action="create_carousel_post".
2. params의 image_urls는 아래 주소 전부를 이 순서 그대로, caption은 아래 <<< >>> 사이 원문 그대로 넣으세요.
3. 실패하면 오류를 확인하고 한 번만 다시 시도하세요. 첫 시도가 실제로 게시됐는지 불확실하면 중복 게시를 막기 위해 재시도하지 말고 보고만 하세요.
4. 결과(성공 시 media id, 실패 시 오류 내용)를 한 줄로 보고하세요. 다른 게시물이나 댓글은 올리지 마세요.
image_urls:
(카드 장수만큼, 뉴스 6줄 · 경매 8줄)
caption:
<<<
(캡션)
>>>
```
쇼츠 게시 프롬프트:
```
인스타그램 @real.estate_kr에 '부동산 썰방' 1분 쇼츠 S<YYYYMMDD>를 릴스로 게시하세요. 사용자가 미리 요청한 자동 게시이며, 이 작업은 이 영상 하나만 올립니다.
1. Windsor.ai for Social Media 커넥터의 execute_action 도구를 사용하세요(지연 로드 상태면 ToolSearch로 먼저 불러오세요). connector="instagram", account="17841435414933916", action="create_video_post".
2. params: video_url="(주소)", cover_url="(썸네일 jpg 주소)", share_to_feed=true, caption=아래 <<< >>> 사이 원문 그대로.
3. 실패하면 오류를 확인하고 한 번만 다시 시도하세요. 첫 시도가 실제로 게시됐는지 불확실하면 중복 게시를 막기 위해 재시도하지 말고 보고만 하세요. 영상 처리 대기 안내가 나오면 안내대로 상태를 확인하세요.
4. 결과(성공 시 media id, 실패 시 오류 문구 그대로)를 한 줄로 보고하세요. Instagram이 영상 주소를 가져오지 못한다는 오류라면 "영상 호스팅 문제"라고 맨 앞에 적으세요. 다른 게시물이나 댓글은 올리지 마세요.
caption:
<<<
(캡션)
>>>
```

## 7. 보고
- 매일 제작 작업: 문제가 있을 때만 푸시 알림이 의미 있음. 마지막 응답에 오늘 뉴스 제목·쇼츠 제목·예약 시각, 그리고 list_triggers(include_completed=true)로 본 **어제 게시 작업의 실패 여부**(실패 시 맨 위, "영상 호스팅 문제"면 특히 강조)
- 경매 작업: 고른 물건(또는 게시 안 한 사유), 판정 근거 3줄. 뉴스의 날에는 아무것도 하지 않고 한 줄만 남기고 끝냄

## 반응 기반 우선 주제
(반응 분석 후 추가)
