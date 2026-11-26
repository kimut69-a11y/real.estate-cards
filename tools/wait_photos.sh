#!/usr/bin/env bash
# 쇼츠 대본 JSON을 push한 뒤, GitHub Actions가 사진을 받아 올릴 때까지 기다린다.
# 사용법: bash tools/wait_photos.sh YYYYMMDD [최대초=420]
# assets/photos/status/S<id>.txt 가 생기면 내용을 출력하고 끝(OK 또는 PHOTO 경고). 시간 초과면 TIMEOUT 출력.
id=$1; max=${2:-420}; t=0
cd "$(dirname "$0")/.."
while [ $t -lt $max ]; do
  git pull -q --rebase origin main >/dev/null 2>&1
  if [ -f "assets/photos/status/S$id.txt" ]; then cat "assets/photos/status/S$id.txt"; exit 0; fi
  sleep 20; t=$((t+20))
done
echo "TIMEOUT: 사진 자동 수집 결과가 ${max}초 안에 오지 않음 → 이모지 장면으로 진행"
