# 부동산 썰방 자동화 지침서 (v3)

인스타그램 @real.estate_kr '부동산 썰방' (30~40대 대상)을 사람 손 없이 매일 만들고 예약 게시한다.
사용자는 확인·승인하지 않는다(애매한 게시물은 사용자가 올라간 뒤 직접 삭제). 그러니 **정확성은 이 작업이 책임진다.**

| 언제 | 무엇 | 만드는 작업 |
|---|---|---|
| 매일 12:30 | 부동산 뉴스 카드뉴스 (정책·제도 변화) | 매일 제작 작업 (클라우드) |
| 매일 21:00 | 1분 썰 쇼츠 (AI 여성 나레이션, '1분만' 스타일) | 매일 제작 작업 (클라우드) |
| 매주 수 19:00 | 이번 주 추천 경매 매물 카드뉴스 | 주간 경매 작업 (사용자 맥북 필요) |

## 0. 고정 정보
- 저장소: https://github.com/kimut69-a11y/real.estate-cards (공개, main). push 전 항상 `git pull --rebase`.
- 이미지: `https://raw.githubusercontent.com/kimut69-a11y/real.estate-cards/main/cards/<파일>.jpg`
- 영상: `https://raw.githubusercontent.com/kimut69-a11y/real.estate-cards/main/reels/<파일>.mp4`
- 게시: Windsor.ai for Social Media `execute_action`, connector=`instagram`, account=`17841435414933916`
  - 카드뉴스: action=`create_carousel_post` (image_urls 6개, caption)
  - 쇼츠: action=`create_video_post` (video_url, thumb_offset=1500, share_to_feed=true, caption)
- 파일 이름 (날짜 = 게시일, YYYYMMDD):
  - 뉴스 카드: `posts/daily/YYYY-MM-DD.json` 의 type=info, id=YYYYMMDD, prefix="N" → `cards/NYYYYMMDD-1~6.jpg`
  - 쇼츠: 같은 파일의 type=short, id=YYYYMMDD → `reels/SYYYYMMDD.mp4`
  - 경매 카드: `posts/auction/YYYY-MM-DD.json` 의 type=auction, id=YYYYMMDD, prefix="A" → `cards/AYYYYMMDD-1~6.jpg`
- 도구: `tools/cards.py`(카드), `tools/shorts.py`(쇼츠), `tools/setup_tts.sh`(음성 도구 설치, 매 실행 처음에 1회)

## 1. 준비 (매 실행)
1. `git clone https://github.com/kimut69-a11y/real.estate-cards` (인증 실패 시 Claude_Code_Remote `add_repo` owner=kimut69-a11y repo=real.estate-cards access=push)
2. `/usr/bin/google-chrome`, `ffmpeg`, `python3 -c "import playwright"` 확인. 패키지 설치는 시도하지 않음
3. 쇼츠를 만들 때: `bash tools/setup_tts.sh` (GitHub에서 Supertonic 3 음성·음성인식 모델을 받음, 1~2분)
4. 오늘 파일이 이미 있으면 새로 만들지 말고 빠진 단계(렌더링·push·예약)만 이어서 함
5. 시작할 때 Windsor `get_connectors`로 instagram 연결과 필요한 action 확인. 안 되면 제작·push만 하고 예약은 만들지 말고 보고 맨 위에 적음

## 2. 부동산 뉴스 카드 (매일 12:30)
- 주제: 최근 1~2주 안에 발표·시행·확정된 부동산 정책·제도·세금·대출·청약·전월세·공급 관련 변화 1건. 시행일이 다가오는 제도, 그 주 일정(종부세 납부, 청약 일정 등)도 좋음
- 이전 `posts/**/*.json` 의 type=info `title`과 겹치지 않게
- **사실 확인 필수**: 정부(korea.kr, 국토교통부, 금융위원회, 국세청, 기획재정부), 국가법령정보센터, 주요 언론으로 교차 확인. 숫자·날짜·요건은 출처와 정확히 일치. 확인 안 되는 내용은 쓰지 않음. 발표만 되고 시행 전이면 "시행 예정", 국회 통과 전이면 "추진 중"이라고 분명히 씀
- 정치적 평가·찬반 의견 금지. 무엇이 바뀌는지, 누구에게 영향이 있는지만
- 형식(type=info, `posts/week01.json`의 101~107 예시 참고): tag(예: "이번 주 부동산 뉴스"), hook/sub(각 2줄 `<br>`, 줄당 한글 약 9자/8자), items 4개 `{"t":"제목 2줄","b":"설명 약 55자","tip":"선택"}`, sum_points 3개, sum_note(선택), asof("2026년 11월 24일 기준" 등), src(기관·매체명)
- 캡션: 훅 1~2문장 + 저장·공유 유도 / 빈 줄 / `일반 정보이며 개별 상황은 전문가 확인` / 빈 줄 / `#부동산썰방 #부동산뉴스` + 주제 태그 4개

## 3. 1분 썰 쇼츠 (매일 21:00)
### 사례 고르기
- **실제 판결만.** 부동산 분쟁(층간소음·누수·전세·매매·경매·상가·재건축 등). WebSearch/WebFetch로 사건번호·법원·금액·결론을 확인. 출처와 정확히 일치. 확인 안 되면 다른 사건
- 이전 `posts/**/*.json`의 `src`와 같은 판결은 다시 쓰지 않음. `posts/week01.json`의 사례들(2~14번)과 `posts/proto.json`(900번)은 이미 검증된 판결이니 쇼츠 대본으로 다시 써서 써도 됨(같은 판결로 쇼츠는 한 번만)
- 주제가 한쪽으로 몰리지 않게 직전 6일과 다른 분야 우선
### 대본 쓰기 (`posts/proto.json` 이 기준 예시)
- 45~60초, 11~14문장. 친구한테 썰 풀듯 빠르고 친근한 반말. 첫 문장은 짧은 훅("들어봐." 등), 둘째 문장에 갈등의 핵심, 중간에 "법원은 어떻게 봤을까?" 같은 질문, 끝은 한 줄 교훈
- `say`(읽을 문장): 숫자는 한글로 풀어 씀(1,960만 → 천구백육십만). 어려운 한자어·약어는 쉬운 말로. 문장당 한글 60자 이내
- `sub`(자막): 숫자 표기 가능. 길면 `|`로 2~3개 덩어리. 덩어리당 20자 안팎
- `hl`: 자막에서 노란색으로 강조할 핵심어 1~2개 (sub 안에 그대로 있는 문자열)
- `scene`: 문장마다 장면. 같은 장면 종류가 3번 연속되지 않게. 종류: title, emoji, char(face: normal/happy/shock/angry/sad/smug/think), vs, money, compare, court, end. 자세한 필드는 `tools/shorts.py` 맨 위 설명
- 마지막 문장은 scene type=end (교훈 + "팔로우하면 매일 1분 판례")
- voice는 넣지 않음(기본: 여성 sid 0, 1.15배속 — 사용자가 고른 목소리)
### 렌더링·검수
1. `python3 tools/shorts.py posts/daily/YYYY-MM-DD.json` → `reels/SYYYYMMDD.mp4`
2. 출력의 `PRONUNCIATION` 경고: 그 문장의 `say`에서 잘못 들린 단어를 더 쉬운 말로 바꿔 다시 렌더링(최대 3번). `OVERFLOW`는 글자를 줄임. 종료 코드 0이어야 함
3. 장면 확인: `ffmpeg -i reels/SYYYYMMDD.mp4 -vf "select='not(mod(n\,150))',scale=270:480,tile=6x2" -frames:v 1 /tmp/x.png` 후 Read로 보고 글자 잘림·겹침 확인
4. 사실 재확인: 금액·결론·법원명·사건번호를 출처와 다시 대조
- 캡션: 훅 + "끝까지 보면 판결 공개" 류 + 댓글 유도 / 빈 줄 / `실제 판결 기반 각색 · 법률 자문 아님 · 개별 사안은 전문가 상담` / 빈 줄 / `#부동산썰방 #부동산판례 #1분판례` + 주제 태그 3개 / 영상에 AI 음성을 썼으므로 캡션 맨 끝 줄에 `🎙️ AI 음성` 표기

## 4. 이번 주 추천 경매 매물 (매주 수 19:00) — 맥북 작업
**원칙: 무조건 정확하게. 조금이라도 애매하면 올리지 않는다.**
- 후보: ① 사용자 맥북 `/Users/kimut/Desktop/01_김유탁/01_경매/모의입찰` 의 최신 `경매물건_YYYYMMDD.xlsx` 목록 물건, `분석_<사건번호>.xlsx`가 있으면 그 분석 우선 ② 법원경매정보(courtauction.go.kr)에서 전국 아파트 중 조회수 상위 물건
- **매각물건명세서가 열람 가능한 물건만** (보통 매각기일 1주 전부터). 매각기일이 게시일(수) 이후여야 함 — 목·금 이후 매각 물건
- 분석 방법은 `auction-case-analysis` 스킬 절차 그대로 (내장 브라우저로 사건내역·문건송달내역·매각물건명세서·현황조사서 확인, 시세·거래량·세대수·낙찰가율 조사)
- 매각물건명세서는 이미지라 판독 오류가 날 수 있으므로 **말소기준권리 일자·임차인 전입일·확정일자·배당요구 여부·인수 권리·비고란을 두 번 따로 판독해 일치할 때만** 사용
- 올리지 않는 경우(다음 후보로 넘어감): 대항력 있는 임차인 / 배당요구 안 한 선순위 임차인 / 인수 권리 있음 / 지분·대지권 미등기·유치권·법정지상권·선순위 가처분·가등기·재매각 / 명세서 비고란에 특이사항 / 판독이 두 번 일치하지 않음 / 시세 근거가 3개월 거래 2건 미만
- 후보를 3건까지 봐도 조건을 만족하는 물건이 없으면 **그 주는 게시하지 않고** 사유를 보고
- 예상 입찰가: 최근 3개월 동일평형 실거래 평균, 지역 아파트 낙찰가율, 취득세·비용, 목표수익률 10%를 근거로 범위로 제시(스킬의 엑셀 계산과 일치해야 함). 근거를 5번 카드에 적음
- 형식(type=auction, prefix="A"): case_no("OO지방법원 2026타경12345"), hook(감정가·최저가 2줄), sub(지역·단지·평형·유찰·매각일), overview 5줄 `[["항목","값"],...]`, rights 4줄(말소기준권리/임차인/인수 권리/특수사항), rights_verdict(한 줄 결론), doc_date(명세서 열람일), market 4줄, market_note, bid("1억 9,300만 ~ 9,800만"), bid_basis, bid_rows 2줄, checklist 4개, src
- 캡션: 사건번호·매각기일·한 줄 요약 / 빈 줄 / `⚠ 투자 판단과 책임은 본인에게 있습니다. 공개 자료 기반 개인 분석이며 법률·투자 자문이 아닙니다. 입찰 전 등기부등본·매각물건명세서 원문과 현장을 반드시 확인하세요.` / 빈 줄 / `#부동산썰방 #경매 #법원경매 #아파트경매 #경매물건 #지역명`
- 분석 엑셀(`분석_<사건번호>.xlsx`)은 모의입찰 폴더에도 저장

## 5. 업로드
- `git add cards reels posts && git commit -m "..." && git pull --rebase && git -c push.negotiate=true push`
- 확인: `curl -s https://api.github.com/repos/kimut69-a11y/real.estate-cards/contents/<경로>` 에 size가 있어야 함

## 6. 게시 예약 (Claude_Code_Remote create_trigger, 1회 실행)
- name: `썰방 뉴스 MM/DD 12:30` / `썰방 쇼츠 MM/DD 21:00` / `썰방 경매 MM/DD 19:00`. 같은 이름이 이미 있으면 만들지 않음(list_triggers로 확인)
- run_once_at: `YYYY-MM-DDTHH:MM:00[Asia/Seoul]`, initiation `human_schedule`, notifications `{"push": false}` (사용자는 매번 알림을 원하지 않음; 실패해도 다음 제작 작업이 보고)
- 게시 시각이 이미 지났으면(제작이 늦어진 경우) 예약 대신 지금 바로 게시하지 말고 다음 날 같은 시각으로 예약

카드뉴스 게시 프롬프트:
```
인스타그램 @real.estate_kr에 '부동산 썰방' 카드뉴스 <파일접두사>를 게시하세요. 사용자가 미리 요청한 자동 게시이며, 이 작업은 이 게시물 하나만 올립니다.
1. Windsor.ai for Social Media 커넥터의 execute_action 도구를 사용하세요(지연 로드 상태면 ToolSearch로 먼저 불러오세요). connector="instagram", account="17841435414933916", action="create_carousel_post".
2. params의 image_urls는 아래 6개 주소를 이 순서 그대로, caption은 아래 <<< >>> 사이 원문 그대로 넣으세요.
3. 실패하면 오류를 확인하고 한 번만 다시 시도하세요. 첫 시도가 실제로 게시됐는지 불확실하면 중복 게시를 막기 위해 재시도하지 말고 보고만 하세요.
4. 결과(성공 시 media id, 실패 시 오류 내용)를 한 줄로 보고하세요. 다른 게시물이나 댓글은 올리지 마세요.
image_urls:
(6줄)
caption:
<<<
(캡션)
>>>
```
쇼츠 게시 프롬프트:
```
인스타그램 @real.estate_kr에 '부동산 썰방' 1분 쇼츠 S<YYYYMMDD>를 릴스로 게시하세요. 사용자가 미리 요청한 자동 게시이며, 이 작업은 이 영상 하나만 올립니다.
1. Windsor.ai for Social Media 커넥터의 execute_action 도구를 사용하세요(지연 로드 상태면 ToolSearch로 먼저 불러오세요). connector="instagram", account="17841435414933916", action="create_video_post".
2. params: video_url="(주소)", thumb_offset=1500, share_to_feed=true, caption=아래 <<< >>> 사이 원문 그대로.
3. 실패하면 오류를 확인하고 한 번만 다시 시도하세요. 첫 시도가 실제로 게시됐는지 불확실하면 중복 게시를 막기 위해 재시도하지 말고 보고만 하세요. 영상 처리 대기 안내가 나오면 안내대로 상태를 확인하세요.
4. 결과(성공 시 media id, 실패 시 오류 문구 그대로)를 한 줄로 보고하세요. Instagram이 영상 주소를 가져오지 못한다는 오류라면 "영상 호스팅 문제"라고 맨 앞에 적으세요. 다른 게시물이나 댓글은 올리지 마세요.
caption:
<<<
(캡션)
>>>
```

## 7. 보고
- 매일 제작 작업: 문제가 있을 때만 푸시 알림이 의미 있음. 마지막 응답에 오늘 뉴스 제목·쇼츠 제목·예약 시각, 그리고 list_triggers(include_completed=true)로 본 **어제 게시 작업의 실패 여부**(실패 시 맨 위, "영상 호스팅 문제"면 특히 강조)
- 주간 경매 작업: 고른 물건(또는 게시 안 한 사유), 판정 근거 3줄

## 반응 기반 우선 주제
(반응 분석 후 추가)
