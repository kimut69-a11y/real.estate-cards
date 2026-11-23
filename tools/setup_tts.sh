#!/usr/bin/env bash
# 음성 합성(Supertonic 3, 한국어) + 음성 인식(검수용) 도구를 GitHub 릴리스에서 내려받아 ~/tts 에 설치한다.
set -e
D=${TTS_DIR:-$HOME/tts}; mkdir -p "$D"; cd "$D"
V=v1.13.8
B=sherpa-onnx-$V-linux-x64-shared
S=sherpa-onnx-supertonic-3-tts-int8-2026-05-11
A=sherpa-onnx-zipformer-korean-2024-06-24
[ -x "$B/bin/sherpa-onnx-offline-tts" ] || { curl -sSL -o b.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/$V/$B.tar.bz2 && tar xjf b.tar.bz2 && rm b.tar.bz2; }
[ -f "$S/voice.bin" ] || { curl -sSL -o s.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/$S.tar.bz2 && tar xjf s.tar.bz2 && rm s.tar.bz2; }
[ -f "$A/tokens.txt" ] || { curl -sSL -o a.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/$A.tar.bz2 && tar xjf a.tar.bz2 && rm a.tar.bz2; }
echo "TTS ready in $D"
