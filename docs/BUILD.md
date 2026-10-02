# 개발 환경 및 재빌드

이 저장소는 제작 자료 공개본입니다. 추출된 원본 리소스와 일부 외부 도구·중간 산출물을 제외하므로 clone 직후 한 명령으로 동일 빌드를 생성하는 구성은 아닙니다. 일반 사용자는 릴리즈 xdelta를 적용하세요.

## 필요한 자료

- README 해시와 일치하는 일본판 ISO. 작업 루트 파일명은 `Ultimate Spider-Man (Japan).iso`입니다.
- Python 3.13 및 `requirements-extended.txt`에 기록된 패키지.
- NanumSquare Neo Bold의 `NanumSquareNeo-cBd.ttf` 등 스크립트에서 참조하는 비교 글꼴. 글꼴은 별도 준비합니다.
- Zig C 컴파일러: 현재 스크립트는 `work/compiler/ziglang/zig.exe` 경로를 사용합니다. MIPS 타깃 옵션은 `tools/build_subtitle_runtime.py`에 있습니다.
- 영상 재생성 시 FFmpeg, vgmstream 및 관련 변환 도구와 원본 영상 추출물이 필요합니다. 외부 도구 버전과 경로는 실행 환경에 맞춰 확인해야 합니다.

## 기존 제작 흐름

1. `tools/iso.py`, `inspect_initial.py`, `extract_paks.py`, `extract_all.py` 등을 참고하여 원본 ELF·아카이브와 매니페스트를 `work/`에 준비합니다.
2. `translation/`의 JSON·TSV를 수정합니다. 버튼 제어 코드와 식별자를 유지합니다.
3. 영상 소스·매니페스트와 필요한 중간물을 준비합니다. 기본 빌드는 기존 자막 영상 중간물을 사용하며 `-ReencodeVideos`는 영상 재생성을 요청합니다.
4. `powershell -ExecutionPolicy Bypass -File .\rebuild_extended.ps1 -Python python`으로 제작 파이프라인을 실행합니다. 누락된 추출물이나 도구 경로는 각 스크립트 입력을 확인하여 준비해야 합니다.
5. 텍스트·자막·보존 검사 결과를 확인하고 새 부팅으로 실제 화면과 진행을 검수한 후 xdelta를 생성합니다.

`work/`, `build/`, 모델·실행 파일·원본 게임 리소스는 포함하지 않습니다. ASR 도구는 번역 보조용이며 받아쓰기를 다시 실행하는 것만으로 기존 검수 결과를 재현할 수 없습니다. 공개된 빌드 스크립트의 완전한 클린 환경 재현성은 검증하지 않았습니다.
