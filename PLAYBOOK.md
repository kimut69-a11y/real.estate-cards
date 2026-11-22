# 부동산 썰방 주간 자동화 지침서

인스타그램 @real.estate_kr '부동산 썰방' (30~40대 대상, 부동산 분쟁·경매·판례 썰 카드뉴스)을
매주 자동으로 만들고 예약 게시하기 위한 지침입니다. 주간 예약 작업은 이 문서를 그대로 따릅니다.

## 0. 고정 정보
- 저장소: https://github.com/kimut69-a11y/real.estate-cards (공개, 브랜치 main)
- 이미지 주소: `https://raw.githubusercontent.com/kimut69-a11y/real.estate-cards/main/cards/PNN-k.jpg` (NN=게시물 번호 2자리 이상, k=1~6)
- 게시: Windsor.ai for Social Media 커넥터 `execute_action`
  - connector=`instagram`, account=`17841435414933916`, action=`create_carousel_post`
  - params: `image_urls`(6개, 순서대로), `caption`
- 게시 시간: 매일 12:30, 21:00 (Asia/Seoul) → 주 14개
- 게시물 번호: 1주차 1~14, 2주차 15~28, 3주차 29~42 … (N주차 = 14N-13 ~ 14N)
- 파일: `posts/weekNN.json` (주차 2자리), 카드 `cards/PNN-1.jpg ~ PNN-6.jpg`

## 1. 준비
1. `git clone https://github.com/kimut69-a11y/real.estate-cards` (실패하면 Claude_Code_Remote의 `add_repo`로 owner=kimut69-a11y, repo=real.estate-cards, access=push 를 붙인 뒤 안내대로 clone)
2. `/usr/bin/google-chrome` 와 `python3 -c "import playwright"` 확인. 없으면 설치를 시도하지 말고 중단·보고.
3. 글꼴은 `fonts/` 안에 있음 (OFL 라이선스). 따로 받을 필요 없음.
4. 다음 주차 번호 = `posts/` 안의 가장 큰 weekNN + 1. 이미 그 주차 파일이 있으면 새로 만들지 말고, 빠진 단계(렌더링·push·예약)만 이어서 함.

## 2. 사례 고르기 (14개)
- 주제 비율(권장): 층간소음·누수 등 이웃 분쟁 3~4 / 전세·임대차 3 / 매매계약 2~3 / 경매 3 이상 / 상가·권리금 2
- 기존 `posts/*.json`의 `title`, `src`를 읽어 **같은 판결은 다시 쓰지 않는다.** 비슷한 주제는 결론이 대비되는 사건일 때만.
- **실제 판결만.** WebSearch/WebFetch로 확인한다. 우선 출처: 대법원 종합법률정보·법원 보도자료, 법률신문, 주요 일간지·방송 기사. 사건번호(예: 대법원 2016도14585)를 확인할 수 있는 것을 우선.
- 금액·비율·결론·법원명은 출처와 **정확히 일치**해야 한다. 확인 안 되는 숫자는 쓰지 않는다. 확인이 안 되는 사건은 버리고 다른 사건으로 바꾼다.
- 이야기 장면(대사 등)은 각색 가능하지만 사실관계·결론을 바꾸지 않는다. 실명·특정 가능한 개인정보 금지.
- 최근 판결(1~2년)을 섞어 트렌디하게. 정치 이슈는 다루지 않는다.

## 3. posts/weekNN.json 형식
```json
{"week": 2, "start": "2026-12-01", "posts": [ { ...게시물... }, ... ]}
```
게시물 필드 (week01.json 예시를 참고해 같은 톤·길이로):
| 필드 | 카드 | 설명 / 길이 |
|---|---|---|
| id | – | 게시물 번호 (정수) |
| title | – | 내부용 짧은 제목 |
| slot | – | 게시 시각 `YYYY-MM-DDTHH:MM` (KST) |
| tag | 1 | "법원 실제 판결" / "대법원 판결" / "대법원 판결 · 경매" 등 |
| hook | 1 | 2줄, `<br>`로 구분, 줄당 한글 약 9자 이내 |
| sub | 1 | 2줄, 줄당 약 8자 |
| s_title / s_body | 2 | 사건 개요 제목 2줄 / 본문 1~2문장(약 60자) |
| t_intro / t_big / t_label / t_quote | 3 | 반전·쟁점. t_big 2줄, t_quote 약 60자 |
| q_title / q_ask / opts | 4 | "당신의 판결은?" / 짧은 질문(없으면 "") / 2~3개 `[["A","..."],["B","..."]]` |
| v_title / v_letter / v_head / v_exp | 5 | 정답 글자는 opts 중 하나와 일치. v_head 2줄 |
| v_points / v_foot | 5 | 0~2개 요점 / 부가 한 줄(없으면 "") |
| l_big / l_line | 6 | 교훈. 강조는 `<span style=\"color: #E3FF5C\">…</span>` |
| src | 6 | 출처 (사건번호 또는 매체명) |
| caption | – | 아래 캡션 형식 |

캡션 형식:
```
(훅 질문 1~2문장 + 댓글·저장·공유 유도 한 문장)

실제 판결 기반 각색 · 법률 자문 아님 · 개별 사안은 전문가 상담

#부동산썰방 #주제태그 4~5개
```

## 4. 렌더링·검수
1. `python3 tools/cards.py posts/weekNN.json` → 종료 코드 0이어야 함 (OVERFLOW/FONT 경고 시 해당 필드를 줄여 다시 렌더링)
2. Read 도구로 최소 각 게시물의 1번·5번 카드를 직접 보고 글자 잘림·겹침이 없는지 확인
3. 사실 재확인: 각 게시물의 금액·결론·법원명을 출처와 다시 대조

## 5. 업로드
1. `git add cards posts && git commit` (커밋 메시지 예: "Add week NN cards (posts A-B)") 후 `git -c push.negotiate=true push`
2. raw.githubusercontent.com은 작업 환경에서 막혀 있을 수 있으니, 업로드 확인은
   `curl -s https://api.github.com/repos/kimut69-a11y/real.estate-cards/contents/cards/PNN-1.jpg` 로 한다.

## 6. 예약 작업 14개 만들기
- 먼저 `list_triggers`로 같은 이름("부동산 썰방 게시물 N")이 이미 있는지 확인하고, 있는 건 건너뛴다.
- Claude_Code_Remote `create_trigger`로 게시물마다 1회 실행 작업 생성:
  - name: `부동산 썰방 게시물 N (MM/DD HH:MM)`
  - run_once_at: `YYYY-MM-DDTHH:MM:00[Asia/Seoul]`
  - initiation: `human_schedule`, notifications: `{"push": true}`
  - prompt: 아래 템플릿 (N, 이미지 주소, 캡션을 채움)
- "rate limit" 오류가 나면 10초쯤 기다렸다가 다시 시도.

게시 작업 프롬프트 템플릿:
```
인스타그램 @real.estate_kr에 예약된 '부동산 썰방' 게시물 N을 게시하세요. 사용자가 자동 게시를 요청해 둔 주간 콘텐츠이며, 이 작업은 이 게시물 하나만 올립니다.

1. Windsor.ai for Social Media 커넥터의 execute_action 도구를 사용하세요(지연 로드 상태면 ToolSearch로 먼저 불러오세요). connector="instagram", account="17841435414933916", action="create_carousel_post".
2. params의 image_urls는 아래 6개 주소를 이 순서 그대로, caption은 아래 <<< >>> 사이 원문 그대로 넣으세요.
3. 실패하면 오류를 확인하고 한 번만 다시 시도하세요. 첫 시도가 실제로 게시됐는지 불확실하면 중복 게시를 막기 위해 재시도하지 말고 보고만 하세요.
4. 결과(성공 시 media id, 실패 시 오류 내용)를 한 줄로 보고하세요. 다른 게시물이나 댓글은 올리지 마세요.

image_urls:
(PNN-1.jpg ~ PNN-6.jpg 주소 6줄)

caption:
<<<
(캡션)
>>>
```

## 7. 보고
마지막 응답(푸시 알림으로 감)에 짧게:
- 이번 주 14개 제목과 게시 시각
- 저장소 cards 폴더 링크: https://github.com/kimut69-a11y/real.estate-cards/tree/main/cards
- 수정·취소하고 싶으면 해당 예약 작업을 끄면 된다는 한 줄
- 문제(Windsor 연결 끊김·체험판 만료, 렌더링 실패 등)가 있으면 맨 위에 표시

## 이미 다룬 사례 (1주차)
1 실거주 이유로 계약갱신 거절 후 재임대 / 2~14는 posts/week01.json 참고
