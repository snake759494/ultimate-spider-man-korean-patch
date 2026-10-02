# 기술 설명

일본판 SLPM-66404의 ELF, PACKS/AMALGA.PAK, PACKS/MOVIES.PAK를 수정합니다. 파일 LBA를 보존하고 아카이브 확장에는 확인된 0 패딩만 사용합니다. 영상은 일본어 대사 IPU 7편과 어트랙트 PSS 1편을 처리합니다.

글꼴은 NanumSquare Neo Bold 17px를 사용하며 KS X 1001 한글 2,350자와 ASCII 80자로 확장했습니다. 원본 진행 폭 17을 유지하고 20×20 글리프에 gx/gy -1 오프셋을 적용합니다. 8방향 1px 검은 외곽선과 원본 CLUT 알파 120을 사용하고 배경을 투명 인덱스 0으로 보정했습니다.

실시간 자막은 음성 재생·정지와 프레임 렌더링에 연결한 MIPS 코드 및 생성 테이블로 표시합니다. `subtitle_runtime.c`, `build_subtitle_runtime.py`, `build_subtitle_table.py`에 구현이 있습니다.

검증 기록은 당시 실행 범위를 나타냅니다. 과거 smoke 기록의 자막 개수는 최종 테이블과 다를 수 있으며, 최종 외곽선 빌드 확인 범위는 `font_outline_runtime_qa.json`에 기록되어 있습니다. 공개 준비 과정에서 새 전체 플레이 검수를 수행하지 않았습니다. `source_manifest.json`은 원 작업 폴더의 제작 시점 목록이며 공개 저장소 전체 파일 목록이 아닙니다.
