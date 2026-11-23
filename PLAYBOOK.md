# 부동산 썰방 주간 자동화 지침서 (v2: 정보 카드 + 분쟁 릴스)

인스타그램 @real.estate_kr '부동산 썰방' (30~40대 대상)을 매주 자동으로 만들고 예약 게시하기 위한 지침입니다.
주간 예약 작업은 이 문서를 그대로 따릅니다.

**매일 2개**
- 12:30 → **정책·정보 카드뉴스** (6장 캐러셀): 부동산 정책·세금·대출·청약·전월세·경매 기초 등 저장해 둘 정보
- 21:00 → **분쟁 릴스** (9:16 영상 약 25초): 실제 판결 기반 분쟁 썰 (훅 → 사건 → 반전 → 퀴즈 → 판결 → 교훈)

## 0. 고정 정보
- 저장소: https://github.com/kimut69-a11y/real.estate-cards (공개, 브랜치 main)
- 카드 이미지: `https://raw.githubusercontent.com/kimut69-a11y/real.estate-cards/main/cards/PNNN-k.jpg` (k=1~6)
- 릴스 영상: `https://raw.githubusercontent.com/kimut69-a11y/real.estate-cards/main/reels/RNNN.mp4`
- 게시: Windsor.ai for Social Media 커넥터 `execute_action`, connector=`instagram`, account=`17841435414933916`
  - 정보 카드: action=`create_carousel_post`, params `image_urls`(6개 순서대로), `caption`
  - 릴스: action=`create_video_post`, params `video_url`, `thumb_offset`=2500, `share_to_feed`=true, `caption`
- 게시물 번호(id): N주차 정보 카드 = N×100+1 ~ N×100+7, 분쟁 릴스 = N×100+11 ~ N×100+17
  - 예: 2주차 정보 201~207 (P201-1.jpg…), 릴스 211~217 (R211.mp4…)
- 주차: 1주차 = 2026-11-24(화)~11-30(일). 2주차부터 월~일 (2주차 = 12/1~12/7). N주차 시작일 = 2026-12-01 + 7×(N-2)일
- 파일: `posts/weekNN.json` (주차 2자리)

## 1. 준비
1. `git clone https://github.com/kimut69-a11y/real.estate-cards` (실패하면 Claude_Code_Remote `add_repo`로 owner=kimut69-a11y, repo=real.estate-cards, access=push 붙인 뒤 안내대로 clone)
2. `/usr/bin/google-chrome`, `ffmpeg`, `python3 -c "import playwright"` 확인. 없으면 설치 시도하지 말고 중단·보고.
3. 글꼴은 `fonts/` 안에 있음.
4. 다음 주차 = `posts/` 안의 가장 큰 weekNN + 1. 이미 그 주차 파일이 있으면 빠진 단계(렌더링·push·예약)만 이어서 함.

## 2. 주제 고르기
### 정보 카드 7개 (12:30)
- 범위: 대출 규제(LTV·DSR), 부동산 세금(취득세·양도세·보유세·종부세), 청약, 전월세 제도(계약갱신·전월세신고·보증보험), 정부 지원 대출·제도, 경매 기초 시리즈(권리분석·배당·명도·입찰 절차), 계약·등기 기초
- 그 주에 시의성 있는 것 1~2개 우선 (예: 12월 종부세, 새 대책 발표, 청약 일정)
- 이전 posts/*.json의 type=info `title`과 겹치지 않게. 경매 기초는 "경매 입문 N편" 시리즈로 이어감 (1편 = 말소기준권리)
- **최신 사실 확인 필수**: 정부(korea.kr, 국토교통부, 금융위원회, 국세청), 법령(국가법령정보센터), 주요 언론으로 확인. 숫자·날짜·요건은 출처와 정확히 일치. 확인 안 되면 쓰지 않음. 바뀔 수 있는 규제는 `asof`에 기준 시점을 적음
- 정치적 평가·찬반 의견 금지. 사실만 정리

### 분쟁 릴스 7개 (21:00)
- 주제 비율(권장): 층간소음·누수 등 이웃 분쟁 2 / 전세·임대차 2 / 매매계약 1~2 / 경매 1~2 / 상가·권리금 1
- 이전 posts/*.json의 `src`와 같은 판결은 다시 쓰지 않음
- `posts/week01.json`의 type=`reserve` 사례(3·5·7·9·11·13번)는 이미 검증된 판결 — 한 주에 최대 2개까지 릴스로 재활용 가능. 재활용하면 week01.json의 그 항목 type을 `used`로 바꾸고 새 주차 파일에 새 id로 복사
- **실제 판결만.** WebSearch/WebFetch로 확인 (대법원 종합법률정보·법원 보도자료, 법률신문, 주요 언론). 사건번호 우선. 금액·비율·결론·법원명은 출처와 정확히 일치. 확인 안 되면 버리고 교체
- 장면 각색은 가능하지만 사실관계·결론은 바꾸지 않음. 실명·개인정보 금지

## 3. posts/weekNN.json 형식
```json
{"week": 2, "start": "2026-12-01", "posts": [ {...}, ... ]}
```
공통: `id`, `type`("info" 또는 "reel"), `title`(내부용), `slot`(`YYYY-MM-DDTHH:MM`, KST), `caption`

**type=info** (week01.json의 101~107 참고):
| 필드 | 카드 | 설명 |
|---|---|---|
| tag | 1 | 짧은 분류 ("대출 규제 한 장 정리", "경매 입문 2편") |
| hook / sub | 1 | 각 2줄 `<br>`, 줄당 한글 약 9자 / 8자 |
| items | 2~5 | 정확히 4개: `{"t": "제목 2줄", "b": "설명 1~2문장(약 55자)", "tip": "선택, 짧게"}` |
| sum_points | 6 | 3개, 각 20자 안팎 |
| sum_note | 6 | 선택, 한 줄 |
| asof / src | 6 | 기준 시점 / 출처 |

**type=reel** (week01.json의 2·4·6… 참고): tag, hook, sub, s_title, s_body, t_intro, t_big, t_label, t_quote, q_title("당신의 판결은?"), q_ask, opts(2~3개 `[["A","..."],...]`), v_title, v_letter(정답, opts 중 하나), v_head, v_exp, v_points(0~2개), v_foot, l_big(강조는 `<span style=\"color: #E3FF5C\">…</span>`), l_line, src

캡션:
- 정보: 훅 1~2문장 + 저장·공유 유도 / 빈 줄 / `일반 정보이며 개별 상황은 전문가 확인` / 빈 줄 / `#부동산썰방` + 주제 태그 5개
- 릴스: 훅 + "끝까지 보면 판결 공개" 류 + 댓글 유도 / 빈 줄 / `실제 판결 기반 각색 · 법률 자문 아님 · 개별 사안은 전문가 상담` / 빈 줄 / `#부동산썰방 #부동산판례 #릴스` + 주제 태그 4개

## 4. 렌더링·검수
1. `python3 tools/cards.py posts/weekNN.json` → 정보 카드 렌더링 (종료 코드 0이어야 함, OVERFLOW/FONT 경고 시 글자 줄여 다시)
2. `python3 tools/reels.py posts/weekNN.json` → 릴스 렌더링 (게시물당 약 25초, OVERFLOW 경고 시 글자 줄여 다시)
3. Read 도구로 직접 확인: 정보 카드는 각 게시물의 1·2·6번, 릴스는 `ffmpeg -i reels/RNNN.mp4 -vf "select='eq(n\,90)+eq(n\,500)+eq(n\,700)',scale=360:640,tile=3x1" -frames:v 1 /tmp/x.png` 로 장면을 뽑아 확인
4. 사실 재확인: 숫자·결론·법원명·정책 기준일을 출처와 다시 대조

## 5. 업로드
1. `git add cards reels posts && git commit` 후 `git -c push.negotiate=true push`
2. 확인: `curl -s https://api.github.com/repos/kimut69-a11y/real.estate-cards/contents/reels/RNNN.mp4` (raw 주소는 작업 환경에서 막혀 있을 수 있음)

## 6. 예약 작업 14개 만들기
- 먼저 `list_triggers`로 같은 이름이 이미 있으면 건너뜀
- Claude_Code_Remote `create_trigger`, 게시물마다 1회 실행:
  - name: 정보 `부동산 썰방 정보 PNNN (MM/DD 12:30)`, 릴스 `부동산 썰방 릴스 RNNN (MM/DD 21:00)`
  - run_once_at: `YYYY-MM-DDTHH:MM:00[Asia/Seoul]`, initiation: `human_schedule`, notifications: `{"push": true}`
- rate limit 오류면 10초 기다렸다 다시 시도

정보 카드 게시 프롬프트:
```
인스타그램 @real.estate_kr에 예약된 '부동산 썰방' 정보 카드뉴스 PNNN을 게시하세요. 사용자가 미리 요청한 자동 게시이며, 이 작업은 이 게시물 하나만 올립니다.

1. Windsor.ai for Social Media 커넥터의 execute_action 도구를 사용하세요(지연 로드 상태면 ToolSearch로 먼저 불러오세요). connector="instagram", account="17841435414933916", action="create_carousel_post".
2. params의 image_urls는 아래 6개 주소를 이 순서 그대로, caption은 아래 <<< >>> 사이 원문 그대로 넣으세요.
3. 실패하면 오류를 확인하고 한 번만 다시 시도하세요. 첫 시도가 실제로 게시됐는지 불확실하면 중복 게시를 막기 위해 재시도하지 말고 보고만 하세요.
4. 결과(성공 시 media id, 실패 시 오류 내용)를 한 줄로 보고하세요. 다른 게시물이나 댓글은 올리지 마세요.

image_urls:
(PNNN-1.jpg ~ PNNN-6.jpg 주소 6줄)

caption:
<<<
(캡션)
>>>
```

릴스 게시 프롬프트:
```
인스타그램 @real.estate_kr에 예약된 '부동산 썰방' 분쟁 릴스 RNNN을 게시하세요. 사용자가 미리 요청한 자동 게시이며, 이 작업은 이 릴스 하나만 올립니다.

1. Windsor.ai for Social Media 커넥터의 execute_action 도구를 사용하세요(지연 로드 상태면 ToolSearch로 먼저 불러오세요). connector="instagram", account="17841435414933916", action="create_video_post".
2. params: video_url="(RNNN.mp4 주소)", thumb_offset=2500, share_to_feed=true, caption=아래 <<< >>> 사이 원문 그대로.
3. 실패하면 오류를 확인하고 한 번만 다시 시도하세요. 첫 시도가 실제로 게시됐는지 불확실하면 중복 게시를 막기 위해 재시도하지 말고 보고만 하세요. 영상 처리 대기 안내가 나오면 안내대로 상태를 확인하세요.
4. 결과(성공 시 media id, 실패 시 오류 문구 그대로)를 한 줄로 보고하세요. Instagram이 영상 주소를 가져오지 못한다는 오류라면 "영상 호스팅 문제"라고 맨 앞에 적으세요. 다른 게시물이나 댓글은 올리지 마세요.

caption:
<<<
(캡션)
>>>
```

## 7. 보고
마지막 응답(푸시 알림으로 감)에 짧게:
- 문제(Windsor 연결 끊김·체험판 만료, 렌더링 실패, 지난주 릴스 게시 실패 등)가 있으면 맨 위에
- 이번 주 정보 카드 7개·릴스 7개 제목과 게시 시각
- 저장소 링크: https://github.com/kimut69-a11y/real.estate-cards/tree/main/cards , …/tree/main/reels
- 수정·취소하고 싶으면 해당 예약 작업을 끄면 된다는 한 줄

## 반응 기반 우선 주제
(12/6 반응 분석 후 추가 예정)
